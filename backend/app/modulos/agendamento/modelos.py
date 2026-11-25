"""Tabela do módulo de Agendamento (ligada a Animal e Veterinário do módulo de Cadastros)."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database import Base

if TYPE_CHECKING:  # só para o editor; em execução o SQLAlchemy resolve pelo nome
    from ..cadastros.modelos import Animal, Veterinario


# ---------- Agendamentos (REQ 07, 08, 09) ----------
class Agendamento(Base):
    __tablename__ = "agendamentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id"))
    veterinario_id: Mapped[int] = mapped_column(ForeignKey("veterinarios.id"))
    data_hora: Mapped[datetime] = mapped_column(DateTime, index=True)
    duracao_min: Mapped[int] = mapped_column(Integer, default=30)
    tipo: Mapped[str] = mapped_column(String(20))  # Consulta | Retorno | Vacina | Cirurgia | Exame
    # agendado -> confirmado -> aguardando (chegou) -> em_atendimento -> concluido | cancelado
    status: Mapped[str] = mapped_column(String(20), default="agendado")
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelamento_motivo: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cancelamento_justificativa: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    animal: Mapped["Animal"] = relationship(back_populates="agendamentos")
    veterinario: Mapped["Veterinario"] = relationship(back_populates="agendamentos")
