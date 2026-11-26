"""REQ 15 – Dashboard Financeiro (valores recebidos e atendimentos no período) e
REQ 17 – Relatório de faturamento por forma de pagamento."""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.seguranca import requer_permissao
from .esquemas import DashboardOut, RelatorioFaturamentoOut
from .servicos import dashboard, relatorio_faturamento

router = APIRouter(prefix="/financeiro", tags=["Financeiro (REQ 15, 17)"])
LEITURA = requer_permissao(("relatorios", "ver"))


@router.get("/dashboard", response_model=DashboardOut)
def painel(
    periodo: str = Query(default="mes", pattern="^(dia|semana|mes)$"),
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    return dashboard(db, periodo)


@router.get("/relatorio-faturamento", response_model=RelatorioFaturamentoOut)
def faturamento(data_inicio: date, data_fim: date, db: Session = Depends(get_db), _=Depends(LEITURA)):
    """REQ 17 — faturamento por forma de pagamento no período (usado pela tela de Relatórios)."""
    return relatorio_faturamento(db, data_inicio, data_fim)
