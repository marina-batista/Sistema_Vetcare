"""Ponto de entrada da API VetCare.

Rodar (dentro da pasta backend):   uvicorn app.main:app --reload
- Telas:            http://localhost:8000
- Documentação API: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .core.database import Base, SessionLocal, engine
from .modulos.agendamento import rotas as rotas_agendamento
from .modulos.autenticacao import rotas_auth, rotas_usuarios
from .modulos.cadastros import rotas_animais, rotas_tutores, rotas_veterinarios
from .seed import popular_se_vazio

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def adicionar_colunas_novas() -> None:
    """Migração simples: se o banco foi criado por uma versão anterior, adiciona as colunas que faltam
    (assim ninguém precisa apagar o vetcare.db ao atualizar o código)."""
    insp = inspect(engine)
    with engine.begin() as con:
        for tabela in Base.metadata.sorted_tables:
            existentes = {c["name"] for c in insp.get_columns(tabela.name)}
            for coluna in tabela.columns:
                if coluna.name not in existentes:
                    tipo = coluna.type.compile(engine.dialect)
                    con.execute(text(f"ALTER TABLE {tabela.name} ADD COLUMN {coluna.name} {tipo}"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # cria as tabelas se não existirem
    adicionar_colunas_novas()
    with SessionLocal() as db:
        popular_se_vazio(db)
    yield


app = FastAPI(
    title="VetCare API",
    description="Monolito Modular — módulos Autenticação (REQ 01–03), Cadastros (REQ 04–06) "
                "e Agendamento (REQ 07–09).",
    version="1.0.0",
    lifespan=lifespan,
)

# Rotas da API (todas começam com /api), agrupadas pelos módulos do Monolito Modular (Etapa 1 — ADR 002).
# Clínico, Financeiro e Notificações entram aqui quando forem implementados.
MODULOS = {
    "Autenticação": (rotas_auth, rotas_usuarios),
    "Cadastros": (rotas_tutores, rotas_animais, rotas_veterinarios),
    "Agendamento": (rotas_agendamento,),
}
for rotas in MODULOS.values():
    for r in rotas:
        app.include_router(r.router, prefix="/api")


@app.get("/api/saude", tags=["Monitoramento"])
def saude():
    """Verificação de saúde (ADR 004 / ADR 009): um monitor externo pode chamar esta rota periodicamente."""
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        banco = "ok"
    except Exception:  # noqa: BLE001
        banco = "indisponível"
    return {"status": "ok" if banco == "ok" else "degradado", "banco": banco, "modulos": list(MODULOS)}

# Frontend: o próprio FastAPI entrega as telas (HTML/CSS/JS) — sem CORS e sem servidor extra.
# Fica por último para não "engolir" as rotas /api e /docs.
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
