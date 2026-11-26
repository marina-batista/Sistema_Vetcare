"""Entrada e saída da API do módulo Financeiro (pagamento, dashboard, relatório)."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

FormaPagamento = Literal["Pix", "Cartão", "Dinheiro"]


# ---------- Pagamento (REQ 14) ----------
class PagamentoIn(BaseModel):
    agendamento_id: int | None = None
    animal_id: int | None = None
    valor: float = Field(gt=0)
    forma: FormaPagamento = "Pix"
    parcelas: int = Field(default=1, ge=1, le=12)
    data: date
    observacoes: str | None = Field(default=None, max_length=500)


class PagamentoOut(BaseModel):
    id: int
    agendamento_id: int | None
    animal_id: int | None
    animal_nome: str | None
    veterinario_nome: str | None
    tipo: str | None
    valor: float
    forma: str
    parcelas: int
    data: date
    observacoes: str | None
    registrado_por: str | None
    criado_em: datetime


# ---------- Dashboard financeiro (REQ 15) ----------
class PontoSerie(BaseModel):
    rotulo: str
    entradas: float
    atendimentos: int


class FatiaForma(BaseModel):
    forma: str
    valor: float
    percentual: int


class DashboardOut(BaseModel):
    periodo_rotulo: str
    recebido: float
    a_receber: float
    atendimentos: int
    ticket_medio: float
    series: list[PontoSerie]
    formas: list[FatiaForma]
    recentes: list[PagamentoOut]


# ---------- Relatório de faturamento (REQ 17) ----------
class LinhaFaturamento(BaseModel):
    forma: str
    recebimentos: int
    valor: float


class RelatorioFaturamentoOut(BaseModel):
    linhas: list[LinhaFaturamento]
    total_recebimentos: int
    total_valor: float
