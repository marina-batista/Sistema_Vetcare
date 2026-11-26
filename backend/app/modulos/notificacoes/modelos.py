"""Tabelas do módulo de Notificações (REQ 16): histórico de envios e configuração de disparo."""
from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base


# ---------- Notificações enviadas (REQ 16) ----------
class Notificacao(Base):
    __tablename__ = "notificacoes"
    id: Mapped[int] = mapped_column(primary_key=True)
    # referência do que gerou a notificação: "consulta-<id>" ou "vacina-<id>" (evita envio duplicado)
    referencia: Mapped[str] = mapped_column(String(40), index=True)
    tipo: Mapped[str] = mapped_column(String(20))  # consulta | vacina
    tutor_nome: Mapped[str] = mapped_column(String(120))
    animal_nome: Mapped[str] = mapped_column(String(80))
    assunto: Mapped[str] = mapped_column(String(255))
    canal: Mapped[str] = mapped_column(String(20))  # WhatsApp | E-mail
    enviada_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class ConfiguracaoNotificacao(Base):
    """Configuração de disparo automático (uma única linha, id = 1)."""
    __tablename__ = "config_notificacoes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    # {"lembrete24h": bool, "vacina7d": bool, "whatsapp": bool, "email": bool}
    opcoes: Mapped[dict] = mapped_column(JSON, default=dict)
