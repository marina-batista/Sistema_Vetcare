"""Tabelas do módulo de Cadastros. As relações com "Agendamento" usam o nome da classe (texto),
assim este módulo não precisa importar o módulo de Agendamento."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database import Base

if TYPE_CHECKING:  # só para o editor; em execução o SQLAlchemy resolve pelo nome
    from ..agendamento.modelos import Agendamento


# ---------- Tutores e animais (REQ 04, 05) ----------
class Tutor(Base):
    __tablename__ = "tutores"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    telefone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(9), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    numero: Mapped[str | None] = mapped_column(String(10), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(80), nullable=True)
    cidade: Mapped[str | None] = mapped_column(String(80), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    animais: Mapped[list["Animal"]] = relationship(back_populates="tutor")


class Animal(Base):
    __tablename__ = "animais"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), index=True)
    especie: Mapped[str] = mapped_column(String(30))
    raca: Mapped[str | None] = mapped_column(String(60), nullable=True)
    sexo: Mapped[str] = mapped_column(String(10))
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutores.id"))

    tutor: Mapped[Tutor] = relationship(back_populates="animais")
    agendamentos: Mapped[list["Agendamento"]] = relationship(
        back_populates="animal", cascade="all, delete-orphan"
    )


# ---------- Veterinários (REQ 06) ----------
class Veterinario(Base):
    __tablename__ = "veterinarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    crmv: Mapped[str] = mapped_column(String(30), unique=True)
    especialidade: Mapped[str] = mapped_column(String(60))
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # O e-mail liga o veterinário ao usuário de login com perfil "veterinario"
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Lista de {"dia": "Segunda", "inicio": "08:00", "fim": "12:00", "ativo": true}
    horarios: Mapped[list] = mapped_column(JSON, default=list)

    agendamentos: Mapped[list["Agendamento"]] = relationship(back_populates="veterinario")
