"""Senhas (hash PBKDF2), sessões por token e controle de acesso (perfil + permissões por usuário)."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ...core.database import get_db
from .modelos import Sessao, Usuario

_ITERACOES = 120_000
bearer = HTTPBearer(auto_error=False)


def hash_senha(senha: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), _ITERACOES).hex()
    return f"{salt}${h}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    salt, h = senha_hash.split("$", 1)
    calc = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt.encode(), _ITERACOES).hex()
    return hmac.compare_digest(calc, h)


def criar_sessao(db: Session, usuario: Usuario, manter_conectado: bool) -> str:
    token = secrets.token_hex(32)
    horas = 24 * 30 if manter_conectado else 8
    db.add(Sessao(token=token, usuario_id=usuario.id, expira_em=datetime.now() + timedelta(hours=horas)))
    db.commit()
    return token


def usuario_atual(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    """Dependência: exige o header  Authorization: Bearer <token>."""
    nao_autorizado = HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão expirada. Faça login novamente.")
    if not cred:
        raise nao_autorizado
    sessao = db.get(Sessao, cred.credentials)
    if not sessao or sessao.expira_em < datetime.now():
        raise nao_autorizado
    usuario = db.get(Usuario, sessao.usuario_id)
    if not usuario or not usuario.ativo:
        raise nao_autorizado
    return usuario


# ---------- Permissões por módulo (popup "Editar usuário") ----------
MODULOS = {
    "tutores_animais": "Tutores e animais",
    "agenda": "Agenda e agendamentos",
    "prontuario": "Prontuário e prescrições",
    "pagamentos": "Pagamentos",
    "relatorios": "Relatórios e financeiro",
    "usuarios": "Usuários e acessos",
}


def _p(ver=False, editar=False, excluir=False) -> dict:
    return {"ver": ver, "editar": editar, "excluir": excluir}


# Padrão de cada perfil — o administrador pode ajustar por usuário
PERMISSOES_PADRAO = {
    "administrador": {m: _p(True, True, True) for m in MODULOS},
    "recepcionista": {
        "tutores_animais": _p(True, True), "agenda": _p(True, True), "prontuario": _p(),
        "pagamentos": _p(True, True), "relatorios": _p(), "usuarios": _p(),
    },
    "veterinario": {
        "tutores_animais": _p(), "agenda": _p(), "prontuario": _p(True, True, True),
        "pagamentos": _p(), "relatorios": _p(), "usuarios": _p(),
    },
}


def normalizar_permissoes(permissoes: dict | None, perfil: str) -> dict:
    """Completa módulos faltantes e garante que quem edita/exclui também visualiza."""
    base = permissoes or PERMISSOES_PADRAO.get(perfil, {})
    out = {}
    for m in MODULOS:
        a = base.get(m) or {}
        editar, excluir = bool(a.get("editar")), bool(a.get("excluir"))
        out[m] = {"ver": bool(a.get("ver")) or editar or excluir, "editar": editar, "excluir": excluir}
    return out


def permissoes_efetivas(usuario: Usuario) -> dict:
    return normalizar_permissoes(usuario.permissoes, usuario.perfil)


def requer_permissao(*pares: tuple[str, str]):
    """Libera se o usuário tiver QUALQUER uma das permissões.
    Uso: Depends(requer_permissao(("tutores_animais", "editar")))"""

    def verificar(usuario: Usuario = Depends(usuario_atual)) -> Usuario:
        perms = permissoes_efetivas(usuario)
        if not any(perms[m][acao] for m, acao in pares):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Você não tem permissão para esta ação.")
        return usuario

    return verificar
