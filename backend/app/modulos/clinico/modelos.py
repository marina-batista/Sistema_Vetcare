"""Tabelas do módulo Clínico (Gerenciador de Prontuários, Prescrições e Controle de Vacinas — Etapa 1, Figura 1).
As relações com Animal/Veterinário (módulo Cadastros) e Agendamento usam o nome da classe (texto)."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database import Base

if TYPE_CHECKING:  # só para o editor; em execução o SQLAlchemy resolve pelo nome
    from ..cadastros.modelos import Animal, Veterinario


# ---------- Atendimento / Prontuário (REQ 10, 11) ----------
class Atendimento(Base):
    """Um registro clínico do animal. O conjunto dos atendimentos forma o prontuário (REQ 11)."""
    __tablename__ = "atendimentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id"), index=True)
    veterinario_id: Mapped[int | None] = mapped_column(ForeignKey("veterinarios.id"), nullable=True)
    agendamento_id: Mapped[int | None] = mapped_column(ForeignKey("agendamentos.id"), nullable=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    anamnese: Mapped[str | None] = mapped_column(Text, nullable=True)
    exame_fisico: Mapped[str | None] = mapped_column(Text, nullable=True)
    temperatura: Mapped[str | None] = mapped_column(String(20), nullable=True)
    freq_cardiaca: Mapped[str | None] = mapped_column(String(20), nullable=True)
    peso: Mapped[str | None] = mapped_column(String(20), nullable=True)
    diagnostico: Mapped[str] = mapped_column(String(255))
    procedimentos: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    veterinario_nome: Mapped[str] = mapped_column(String(120))  # nome na época do atendimento

    animal: Mapped["Animal"] = relationship()
    veterinario: Mapped["Veterinario | None"] = relationship()
    prescricoes: Mapped[list["Prescricao"]] = relationship(
        back_populates="atendimento", cascade="all, delete-orphan"
    )


# ---------- Prescrições (REQ 13) ----------
class Prescricao(Base):
    __tablename__ = "prescricoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id"), index=True)
    atendimento_id: Mapped[int | None] = mapped_column(ForeignKey("atendimentos.id"), nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    veterinario_nome: Mapped[str] = mapped_column(String(120))
    # Lista de {"nome": ..., "dosagem": ..., "frequencia": ..., "instrucoes": ...}
    medicamentos: Mapped[list] = mapped_column(JSON, default=list)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    animal: Mapped["Animal"] = relationship()
    atendimento: Mapped["Atendimento | None"] = relationship(back_populates="prescricoes")


# ---------- Vacinas (REQ 12) ----------
class Vacina(Base):
    __tablename__ = "vacinas"
    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id"), index=True)
    vacina: Mapped[str] = mapped_column(String(80))
    fabricante: Mapped[str | None] = mapped_column(String(80), nullable=True)
    lote: Mapped[str | None] = mapped_column(String(40), nullable=True)
    data_aplicacao: Mapped[date] = mapped_column(Date, index=True)
    proxima_dose: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    veterinario_nome: Mapped[str | None] = mapped_column(String(120), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    animal: Mapped["Animal"] = relationship()
