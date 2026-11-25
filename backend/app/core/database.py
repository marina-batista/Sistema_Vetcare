"""Conexão com o banco SQLite (arquivo backend/vetcare.db, criado automaticamente)."""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# backend/vetcare.db (os testes usam outro arquivo pela variável de ambiente VETCARE_DB)
DB_PATH = Path(os.environ.get("VETCARE_DB") or Path(__file__).resolve().parents[2] / "vetcare.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependência do FastAPI: abre uma sessão por requisição e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
