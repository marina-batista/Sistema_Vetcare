"""REQ 02 – Autenticar Usuário | REQ 03 – Recuperar Senha"""
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.comum import Mensagem
from ...core.database import get_db
from .esquemas import LoginIn, LoginOut, RecuperarSenhaIn, RedefinirSenhaIn, UsuarioOut
from .modelos import CodigoRecuperacao, Sessao, Usuario
from .seguranca import bearer, criar_sessao, hash_senha, usuario_atual, verificar_senha
from .servicos import usuario_out

router = APIRouter(prefix="/auth", tags=["Autenticação (REQ 02, REQ 03)"])


def _buscar_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(func.lower(Usuario.email) == email.strip().lower()).first()


@router.post("/login", response_model=LoginOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    usuario = _buscar_por_email(db, dados.email)
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(401, "E-mail ou senha inválidos.")
    if not usuario.ativo:
        raise HTTPException(403, "Usuário desativado. Procure o administrador.")
    usuario.ultimo_acesso = datetime.now()
    token = criar_sessao(db, usuario, dados.manter_conectado)
    return LoginOut(token=token, usuario=usuario_out(db, usuario))


@router.get("/me", response_model=UsuarioOut)
def eu(usuario: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    return usuario_out(db, usuario)


@router.post("/logout", response_model=Mensagem)
def logout(cred: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if cred:
        db.query(Sessao).filter(Sessao.token == cred.credentials).delete()
        db.commit()
    return Mensagem(mensagem="Sessão encerrada.")


def enviar_codigo_por_email(email: str, codigo: str) -> None:
    """Simulação de envio de e-mail (ver docs/adr/ADR-012). O código aparece no terminal."""
    print(f"\n[VetCare] Código de recuperação para {email}: {codigo} (válido por 15 min)\n", flush=True)


@router.post("/recuperar-senha", response_model=Mensagem)
def recuperar_senha(dados: RecuperarSenhaIn, db: Session = Depends(get_db)):
    usuario = _buscar_por_email(db, dados.email)
    if usuario and usuario.ativo:
        codigo = f"{secrets.randbelow(10**6):06d}"
        db.add(CodigoRecuperacao(
            usuario_id=usuario.id, codigo=codigo, expira_em=datetime.now() + timedelta(minutes=15)
        ))
        db.commit()
        enviar_codigo_por_email(usuario.email, codigo)
    # Mesma resposta sempre, para não revelar quais e-mails existem no sistema
    return Mensagem(mensagem="Se o e-mail estiver cadastrado, você receberá um código em instantes.")


@router.post("/redefinir-senha", response_model=Mensagem)
def redefinir_senha(dados: RedefinirSenhaIn, db: Session = Depends(get_db)):
    usuario = _buscar_por_email(db, dados.email)
    registro = None
    if usuario:
        registro = (
            db.query(CodigoRecuperacao)
            .filter(
                CodigoRecuperacao.usuario_id == usuario.id,
                CodigoRecuperacao.codigo == dados.codigo,
                CodigoRecuperacao.usado.is_(False),
            )
            .order_by(CodigoRecuperacao.id.desc())
            .first()
        )
    if not registro or registro.expira_em < datetime.now():
        raise HTTPException(400, "Código inválido ou expirado.")
    usuario.senha_hash = hash_senha(dados.nova_senha)
    registro.usado = True
    db.query(Sessao).filter(Sessao.usuario_id == usuario.id).delete()  # derruba sessões antigas
    db.commit()
    return Mensagem(mensagem="Senha redefinida com sucesso.")
