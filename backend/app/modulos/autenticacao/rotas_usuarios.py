"""REQ 01 – Manter Usuário (perfil + permissões ajustáveis por módulo)"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ...core.database import get_db
from .esquemas import AtivoIn, UsuarioCreate, UsuarioOut, UsuarioUpdate
from .modelos import CodigoRecuperacao, Sessao, Usuario
from .seguranca import (
    MODULOS,
    PERMISSOES_PADRAO,
    hash_senha,
    normalizar_permissoes,
    requer_permissao,
)
from .servicos import usuario_out

router = APIRouter(prefix="/usuarios", tags=["Usuários (REQ 01)"])
VER = requer_permissao(("usuarios", "ver"))
EDITAR = requer_permissao(("usuarios", "editar"))
EXCLUIR = requer_permissao(("usuarios", "excluir"))


def _obter(db: Session, id: int) -> Usuario:
    u = db.get(Usuario, id)
    if not u:
        raise HTTPException(404, "Usuário não encontrado.")
    return u


def _email_em_uso(db: Session, email: str, ignorar_id: int | None = None) -> bool:
    q = db.query(Usuario).filter(func.lower(Usuario.email) == email.lower())
    if ignorar_id:
        q = q.filter(Usuario.id != ignorar_id)
    return q.first() is not None


@router.get("/permissoes-padrao")
def permissoes_padrao(_=Depends(VER)):
    """Módulos e permissões padrão de cada perfil (usado no popup Editar usuário)."""
    return {"modulos": list(MODULOS.items()), "padrao": PERMISSOES_PADRAO}


@router.get("", response_model=list[UsuarioOut])
def listar(q: str | None = None, perfil: str | None = None, ativo: bool | None = None,
           db: Session = Depends(get_db), _=Depends(VER)):
    query = db.query(Usuario)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Usuario.nome.ilike(like), Usuario.email.ilike(like)))
    if perfil:
        query = query.filter(Usuario.perfil == perfil)
    if ativo is not None:
        query = query.filter(Usuario.ativo == ativo)
    return [usuario_out(db, u) for u in query.order_by(Usuario.nome)]


@router.get("/{id}", response_model=UsuarioOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(VER)):
    return usuario_out(db, _obter(db, id))


@router.post("", response_model=UsuarioOut, status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db), _=Depends(EDITAR)):
    if _email_em_uso(db, dados.email):
        raise HTTPException(409, "Já existe um usuário com este e-mail.")
    u = Usuario(nome=dados.nome.strip(), email=dados.email.strip().lower(), perfil=dados.perfil,
                ativo=dados.ativo, senha_hash=hash_senha(dados.senha),
                permissoes=normalizar_permissoes(dados.permissoes, dados.perfil))
    db.add(u)
    db.commit()
    return usuario_out(db, u)


@router.put("/{id}", response_model=UsuarioOut)
def atualizar(id: int, dados: UsuarioUpdate, db: Session = Depends(get_db), admin: Usuario = Depends(EDITAR)):
    u = _obter(db, id)
    if _email_em_uso(db, dados.email, ignorar_id=id):
        raise HTTPException(409, "Já existe um usuário com este e-mail.")
    permissoes = normalizar_permissoes(dados.permissoes, dados.perfil)
    if u.id == admin.id:
        if not dados.ativo:
            raise HTTPException(400, "Você não pode desativar o próprio usuário.")
        if not permissoes["usuarios"]["editar"]:
            raise HTTPException(400, "Você não pode remover a sua própria permissão de gerenciar usuários.")
    u.nome, u.email, u.perfil = dados.nome.strip(), dados.email.strip().lower(), dados.perfil
    u.ativo, u.permissoes = dados.ativo, permissoes
    if dados.senha:
        u.senha_hash = hash_senha(dados.senha)
    if not dados.ativo:
        db.query(Sessao).filter(Sessao.usuario_id == id).delete()
    db.commit()
    return usuario_out(db, u)


@router.patch("/{id}/status", response_model=UsuarioOut)
def alterar_status(id: int, dados: AtivoIn, db: Session = Depends(get_db), admin: Usuario = Depends(EDITAR)):
    u = _obter(db, id)
    if u.id == admin.id and not dados.ativo:
        raise HTTPException(400, "Você não pode desativar o próprio usuário.")
    u.ativo = dados.ativo
    if not dados.ativo:
        db.query(Sessao).filter(Sessao.usuario_id == id).delete()
    db.commit()
    return usuario_out(db, u)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), admin: Usuario = Depends(EXCLUIR)):
    u = _obter(db, id)
    if u.id == admin.id:
        raise HTTPException(400, "Você não pode excluir o próprio usuário.")
    db.query(Sessao).filter(Sessao.usuario_id == id).delete()
    db.query(CodigoRecuperacao).filter(CodigoRecuperacao.usuario_id == id).delete()
    db.delete(u)
    db.commit()
    return Response(status_code=204)
