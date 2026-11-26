"""Tabela do módulo Financeiro (pagamentos das consultas e procedimentos — REQ 14)."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...core.database import Base

if TYPE_CHECKING:  # só para o editor; em execução o SQLAlchemy resolve pelo nome
    from ..agendamento.modelos import Agendamento
    from ..cadastros.modelos import Animal


# ---------- Pagamentos (REQ 14) ----------
class Pagamento(Base):
    __tablename__ = "pagamentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    agendamento_id: Mapped[int | None] = mapped_column(ForeignKey("agendamentos.id"), nullable=True)
    animal_id: Mapped[int | None] = mapped_column(ForeignKey("animais.id"), nullable=True)
    valor: Mapped[float] = mapped_column(Float)
    forma: Mapped[str] = mapped_column(String(20))  # Pix | Cartão | Dinheiro
    parcelas: Mapped[int] = mapped_column(Integer, default=1)
    data: Mapped[date] = mapped_column(Date, index=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    registrado_por: Mapped[str | None] = mapped_column(String(120), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    agendamento: Mapped["Agendamento | None"] = relationship()
    animal: Mapped["Animal | None"] = relationship()
