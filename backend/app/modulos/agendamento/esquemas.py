"""Entrada e saída da API do módulo de Agendamento."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

TipoAgendamento = Literal["Consulta", "Retorno", "Vacina", "Cirurgia", "Exame"]
# agendado -> confirmado -> aguardando (chegou) -> em_atendimento -> concluido | cancelado
StatusAgendamento = Literal["agendado", "confirmado", "aguardando", "em_atendimento", "concluido", "cancelado"]
MotivoCancelamento = Literal["Cancelada pelo tutor", "Cancelada pela clínica", "Tutor não compareceu", "Remarcada"]


# ---------- Agendamentos ----------
class AgendamentoIn(BaseModel):
    animal_id: int
    veterinario_id: int
    data_hora: datetime
    tipo: TipoAgendamento = "Consulta"
    duracao_min: int = Field(default=30, ge=15, le=240)
    observacoes: str | None = Field(default=None, max_length=500)


class AgendamentoOut(BaseModel):
    id: int
    animal_id: int
    animal_nome: str
    animal_especie: str
    animal_raca: str | None
    animal_nascimento: date | None
    tutor_id: int
    tutor_nome: str
    veterinario_id: int
    veterinario_nome: str
    data_hora: datetime
    duracao_min: int
    tipo: str
    status: str
    observacoes: str | None
    cancelamento_motivo: str | None = None
    cancelamento_justificativa: str | None = None


class StatusAgendamentoIn(BaseModel):
    status: StatusAgendamento


class CancelamentoIn(BaseModel):
    motivo: MotivoCancelamento
    justificativa: str = Field(min_length=3, max_length=500)


class DisponibilidadeOut(BaseModel):
    horarios: list[str]  # ["08:00", "08:30", ...]
    mensagem: str | None = None
