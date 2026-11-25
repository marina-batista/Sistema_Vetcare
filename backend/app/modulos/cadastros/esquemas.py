"""Entrada e saída da API do módulo de Cadastros."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ...core.comum import EMAIL

HORA = r"^([01]\d|2[0-3]):[0-5]\d$"
CPF = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
CEP = r"^\d{5}-\d{3}$"
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
DiaSemana = Literal["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


# ---------- Tutores ----------
class TutorIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    cpf: str | None = Field(default=None, pattern=CPF)
    telefone: str = Field(min_length=8, max_length=20)
    email: str | None = Field(default=None, pattern=EMAIL)
    cep: str | None = Field(default=None, pattern=CEP)
    endereco: str | None = Field(default=None, max_length=255)
    numero: str | None = Field(default=None, max_length=10)
    bairro: str | None = Field(default=None, max_length=80)
    cidade: str | None = Field(default=None, max_length=80)


class TutorOut(TutorIn):
    id: int
    qtd_animais: int = 0
    ultima_visita: datetime | None = None


# ---------- Animais ----------
class AnimalIn(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    especie: str = Field(min_length=2, max_length=30)
    raca: str | None = Field(default=None, max_length=60)
    sexo: Literal["Macho", "Fêmea"]
    data_nascimento: date | None = None
    tutor_id: int

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_no_passado(cls, v):
        if v and v > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro")
        return v


class AnimalOut(AnimalIn):
    id: int
    tutor_nome: str
    ultimo_atendimento: datetime | None = None
    em_atendimento: bool = False


# ---------- Veterinários ----------
class Horario(BaseModel):
    dia: DiaSemana
    inicio: str = Field(pattern=HORA)
    fim: str = Field(pattern=HORA)
    ativo: bool = True


class VeterinarioIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    crmv: str = Field(min_length=3, max_length=30)
    especialidade: str = Field(min_length=2, max_length=60)
    telefone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, pattern=EMAIL)
    ativo: bool = True
    horarios: list[Horario] = []

    @field_validator("horarios")
    @classmethod
    def inicio_antes_do_fim(cls, horarios):
        for h in horarios:
            if h.ativo and h.inicio >= h.fim:
                raise ValueError(f"{h.dia}: o horário inicial deve ser antes do final")
        return horarios


class VeterinarioOut(VeterinarioIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
