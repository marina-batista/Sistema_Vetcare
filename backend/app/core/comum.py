"""Tipos e padrões usados por mais de um módulo."""
from typing import Generic, TypeVar

from pydantic import BaseModel

EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    itens: list[T]
    total: int
    pagina: int
    tamanho: int


class Mensagem(BaseModel):
    mensagem: str
