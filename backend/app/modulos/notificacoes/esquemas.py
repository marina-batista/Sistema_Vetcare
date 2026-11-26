"""Entrada e saída da API do módulo de Notificações (REQ 16)."""
from datetime import datetime

from pydantic import BaseModel, Field


class NotificacaoPendente(BaseModel):
    referencia: str
    tipo: str  # consulta | vacina
    tutor_nome: str
    animal_nome: str
    assunto: str
    envio: str          # texto do momento previsto de envio ("24/11 08:00")
    canal: str          # WhatsApp | E-mail
    situacao: str       # Agendada | Pendente | Enviada


class NotificacaoHistorico(BaseModel):
    id: int
    tipo: str
    tutor_nome: str
    animal_nome: str
    assunto: str
    canal: str
    enviada_em: datetime


class ItemEnvio(BaseModel):
    referencia: str
    tipo: str = "consulta"
    tutor_nome: str
    animal_nome: str
    assunto: str
    canal: str = "WhatsApp"


class EnvioIn(BaseModel):
    itens: list[ItemEnvio] = Field(min_length=1)


class ConfiguracaoIn(BaseModel):
    lembrete24h: bool = False
    vacina7d: bool = False
    whatsapp: bool = False
    email: bool = False
