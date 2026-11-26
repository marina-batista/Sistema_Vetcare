"""Regras do módulo Financeiro: tabela de preços de referência, montagem do pagamento e agregações."""
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from ..agendamento.modelos import Agendamento
from .esquemas import (
    DashboardOut,
    FatiaForma,
    LinhaFaturamento,
    PagamentoOut,
    PontoSerie,
    RelatorioFaturamentoOut,
)
from .modelos import Pagamento

# Preços de referência (sugestão de valor no recebimento e estimativa do "a receber")
PRECOS = {"Consulta": 180.0, "Retorno": 90.0, "Vacina": 95.0, "Cirurgia": 1200.0, "Exame": 150.0}
FORMAS = ["Pix", "Cartão", "Dinheiro"]


def preco_sugerido(tipo: str | None) -> float:
    return PRECOS.get(tipo or "", 180.0)


def pagamento_out(p: Pagamento) -> PagamentoOut:
    ag = p.agendamento
    animal = p.animal or (ag.animal if ag else None)
    return PagamentoOut(
        id=p.id, agendamento_id=p.agendamento_id, animal_id=p.animal_id,
        animal_nome=animal.nome if animal else None,
        veterinario_nome=ag.veterinario.nome if ag else None,
        tipo=ag.tipo if ag else None,
        valor=p.valor, forma=p.forma, parcelas=p.parcelas, data=p.data,
        observacoes=p.observacoes, registrado_por=p.registrado_por, criado_em=p.criado_em,
    )


def _intervalo(periodo: str) -> tuple[date, date, str]:
    hoje = date.today()
    if periodo == "dia":
        return hoje, hoje, hoje.strftime("%d/%m/%Y")
    if periodo == "semana":
        inicio = hoje - timedelta(days=hoje.weekday())
        return inicio, inicio + timedelta(days=6), "Semana atual"
    inicio = hoje.replace(day=1)
    prox = (inicio + timedelta(days=32)).replace(day=1)
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
             "agosto", "setembro", "outubro", "novembro", "dezembro"]
    return inicio, prox - timedelta(days=1), f"{meses[inicio.month - 1].capitalize()} de {inicio.year}"


def _pagamentos_entre(db: Session, inicio: date, fim: date) -> list[Pagamento]:
    return db.query(Pagamento).filter(Pagamento.data >= inicio, Pagamento.data <= fim).all()


def _concluidos_entre(db: Session, inicio: date, fim: date) -> list[Agendamento]:
    return db.query(Agendamento).filter(
        Agendamento.status == "concluido",
        Agendamento.data_hora >= datetime.combine(inicio, time.min),
        Agendamento.data_hora <= datetime.combine(fim, time.max),
    ).all()


def dashboard(db: Session, periodo: str) -> DashboardOut:
    inicio, fim, rotulo = _intervalo(periodo)
    pagos = _pagamentos_entre(db, inicio, fim)
    concluidos = _concluidos_entre(db, inicio, fim)

    recebido = sum(p.valor for p in pagos)
    ticket = recebido / len(pagos) if pagos else 0.0

    # "A receber": consultas concluídas no período ainda sem pagamento (estimativa pela tabela de preços)
    pagos_ag = {p.agendamento_id for p in pagos if p.agendamento_id}
    a_receber = sum(preco_sugerido(a.tipo) for a in concluidos if a.id not in pagos_ag)

    # Série das últimas 6 semanas (recebimentos e atendimentos concluídos por semana)
    series: list[PontoSerie] = []
    semanas: list[tuple[date, date]] = []
    cursor = fim - timedelta(days=fim.weekday())  # segunda da semana do fim
    for _ in range(6):
        semanas.append((cursor, cursor + timedelta(days=6)))
        cursor -= timedelta(days=7)
    for i, (ini_s, fim_s) in enumerate(reversed(semanas)):
        ps = _pagamentos_entre(db, ini_s, fim_s)
        cs = _concluidos_entre(db, ini_s, fim_s)
        series.append(PontoSerie(rotulo=f"Sem {i + 1}", entradas=sum(p.valor for p in ps), atendimentos=len(cs)))

    # Recebimentos por forma de pagamento (percentual sobre o total do período)
    formas: list[FatiaForma] = []
    for f in FORMAS:
        v = sum(p.valor for p in pagos if p.forma == f)
        pct = round((v / recebido) * 100) if recebido else 0
        formas.append(FatiaForma(forma=f, valor=v, percentual=pct))

    recentes = db.query(Pagamento).order_by(Pagamento.criado_em.desc()).limit(6).all()
    return DashboardOut(
        periodo_rotulo=rotulo, recebido=recebido, a_receber=a_receber, atendimentos=len(concluidos),
        ticket_medio=ticket, series=series, formas=formas, recentes=[pagamento_out(p) for p in recentes],
    )


def relatorio_faturamento(db: Session, inicio: date, fim: date) -> RelatorioFaturamentoOut:
    pagos = _pagamentos_entre(db, inicio, fim)
    linhas = []
    for f in FORMAS:
        ps = [p for p in pagos if p.forma == f]
        if ps:
            linhas.append(LinhaFaturamento(forma=f, recebimentos=len(ps), valor=sum(p.valor for p in ps)))
    return RelatorioFaturamentoOut(
        linhas=linhas, total_recebimentos=len(pagos), total_valor=sum(p.valor for p in pagos),
    )
