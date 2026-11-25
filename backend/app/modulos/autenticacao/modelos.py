"""Tabelas do módulo de Autenticação."""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base


# ---------- Usuários e autenticação (REQ 01, 02, 03) ----------
class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[str] = mapped_column(String(20))  # administrador | recepcionista | veterinario
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    # {"tutores_animais": {"ver": true, "editar": true, "excluir": false}, ...} — vazio = padrão do perfil
    permissoes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ultimo_acesso: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Sessao(Base):
    __tablename__ = "sessoes"
    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    expira_em: Mapped[datetime] = mapped_column(DateTime)


class CodigoRecuperacao(Base):
    __tablename__ = "codigos_recuperacao"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    codigo: Mapped[str] = mapped_column(String(6))
    expira_em: Mapped[datetime] = mapped_column(DateTime)
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
