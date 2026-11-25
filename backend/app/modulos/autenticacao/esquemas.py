"""Entrada e saída da API do módulo de Autenticação."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ...core.comum import EMAIL

Perfil = Literal["administrador", "recepcionista", "veterinario"]
# {"agenda": {"ver": True, "editar": True, "excluir": False}, ...}
Permissoes = dict[str, dict[str, bool]]


# ---------- Autenticação ----------
class LoginIn(BaseModel):
    email: str
    senha: str
    manter_conectado: bool = False


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool
    ultimo_acesso: datetime | None = None
    veterinario_id: int | None = None  # preenchido quando o perfil é "veterinario"
    permissoes: dict | None = None  # permissões efetivas (já com o padrão do perfil)
    modulos_extras: list[str] = []  # módulos liberados além do padrão do perfil (aparecem no menu)


class LoginOut(BaseModel):
    token: str
    usuario: UsuarioOut


class RecuperarSenhaIn(BaseModel):
    email: str = Field(pattern=EMAIL)


class RedefinirSenhaIn(BaseModel):
    email: str = Field(pattern=EMAIL)
    codigo: str = Field(min_length=6, max_length=6)
    nova_senha: str = Field(min_length=6)


# ---------- Usuários ----------
class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=EMAIL)
    perfil: Perfil
    senha: str = Field(min_length=6)
    ativo: bool = True
    permissoes: Permissoes | None = None  # vazio = padrão do perfil


class UsuarioUpdate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=EMAIL)
    perfil: Perfil
    ativo: bool = True
    senha: str | None = Field(default=None, min_length=6)  # vazio = mantém a senha atual
    permissoes: Permissoes | None = None


class AtivoIn(BaseModel):
    ativo: bool
