"""Entrada e saída da API do módulo Clínico (atendimento, prontuário, vacina, prescrição)."""
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


# ---------- Atendimento (REQ 10) ----------
class AtendimentoIn(BaseModel):
    animal_id: int
    agendamento_id: int | None = None
    anamnese: str | None = Field(default=None, max_length=4000)
    exame_fisico: str | None = Field(default=None, max_length=4000)
    temperatura: str | None = Field(default=None, max_length=20)
    freq_cardiaca: str | None = Field(default=None, max_length=20)
    peso: str | None = Field(default=None, max_length=20)
    diagnostico: str = Field(min_length=2, max_length=255)
    procedimentos: str | None = Field(default=None, max_length=1000)
    observacoes: str | None = Field(default=None, max_length=4000)


class AtendimentoOut(BaseModel):
    id: int
    animal_id: int
    animal_nome: str
    agendamento_id: int | None
    data_hora: datetime
    anamnese: str | None
    exame_fisico: str | None
    temperatura: str | None
    freq_cardiaca: str | None
    peso: str | None
    diagnostico: str
    procedimentos: str | None
    observacoes: str | None
    veterinario_nome: str


# ---------- Vacina (REQ 12) ----------
class VacinaIn(BaseModel):
    animal_id: int
    vacina: str = Field(min_length=1, max_length=80)
    fabricante: str | None = Field(default=None, max_length=80)
    lote: str | None = Field(default=None, max_length=40)
    data_aplicacao: date
    proxima_dose: date | None = None
    observacoes: str | None = Field(default=None, max_length=1000)

    @field_validator("data_aplicacao")
    @classmethod
    def aplicacao_nao_futura(cls, v):
        if v > date.today():
            raise ValueError("A data de aplicação não pode estar no futuro")
        return v


class VacinaOut(BaseModel):
    id: int
    animal_id: int
    animal_nome: str
    vacina: str
    fabricante: str | None
    lote: str | None
    data_aplicacao: date
    proxima_dose: date | None
    observacoes: str | None
    veterinario_nome: str | None
    situacao: str  # Em dia | Vence em breve | Vence hoje | Vencida | Dose única


# ---------- Prescrição (REQ 13) ----------
class Medicamento(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    dosagem: str | None = Field(default=None, max_length=120)
    frequencia: str | None = Field(default=None, max_length=120)
    instrucoes: str | None = Field(default=None, max_length=255)


class PrescricaoIn(BaseModel):
    animal_id: int
    atendimento_id: int | None = None
    medicamentos: list[Medicamento] = Field(min_length=1)
    observacoes: str | None = Field(default=None, max_length=1000)


class PrescricaoOut(BaseModel):
    id: int
    animal_id: int
    animal_nome: str
    tutor_nome: str
    atendimento_id: int | None
    data: datetime
    veterinario_nome: str
    medicamentos: list[Medicamento]
    observacoes: str | None
