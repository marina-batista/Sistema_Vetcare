"""Monta a resposta de usuário com permissões efetivas e o vínculo com o cadastro de veterinário."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..cadastros.modelos import Veterinario
from .esquemas import UsuarioOut
from .modelos import Usuario
from .seguranca import PERMISSOES_PADRAO, permissoes_efetivas


def usuario_out(db: Session, u: Usuario) -> UsuarioOut:
    out = UsuarioOut.model_validate(u)
    out.permissoes = permissoes_efetivas(u)
    padrao = PERMISSOES_PADRAO.get(u.perfil, {})
    out.modulos_extras = [m for m, a in out.permissoes.items() if a["ver"] and not padrao.get(m, {}).get("ver")]
    if u.perfil == "veterinario":
        vet = db.query(Veterinario).filter(func.lower(Veterinario.email) == u.email.lower()).first()
        out.veterinario_id = vet.id if vet else None
    return out
