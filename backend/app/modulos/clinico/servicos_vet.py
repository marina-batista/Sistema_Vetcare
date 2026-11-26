"""Vínculo entre o usuário logado e o cadastro de veterinário (mesmo e-mail)."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..autenticacao.modelos import Usuario
from ..cadastros.modelos import Veterinario


def veterinario_do_usuario(db: Session, usuario: Usuario) -> Veterinario | None:
    if not usuario.email:
        return None
    return db.query(Veterinario).filter(func.lower(Veterinario.email) == usuario.email.lower()).first()
