"""Calendário de Consultas (Etapa 1, Figura 1) — REQ 07 Agendar, REQ 08 Cancelar e REQ 09 Consultar Agenda.
As regras de horário ficam em disponibilidade.py (Validador de Disponibilidade)."""
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.seguranca import requer_permissao
from ..cadastros.modelos import Veterinario
from .disponibilidade import horarios_livres, validar_agendamento
from .esquemas import (
    AgendamentoIn,
    AgendamentoOut,
    CancelamentoIn,
    DisponibilidadeOut,
    StatusAgendamentoIn,
)
from .modelos import Agendamento
from .servicos import agendamento_out

router = APIRouter(prefix="/agendamentos", tags=["Agendamento (REQ 07, 08, 09)"])
LEITURA = requer_permissao(("agenda", "ver"), ("prontuario", "ver"), ("pagamentos", "ver"), ("relatorios", "ver"))
EDITAR = requer_permissao(("agenda", "editar"))
EXCLUIR = requer_permissao(("agenda", "excluir"))
# Recepção confirma / registra chegada; veterinário inicia e conclui o atendimento
MUDAR_STATUS = requer_permissao(("agenda", "editar"), ("prontuario", "editar"))
FINALIZADOS = ("concluido", "cancelado")


def _obter(db: Session, id: int) -> Agendamento:
    a = db.get(Agendamento, id)
    if not a:
        raise HTTPException(404, "Agendamento não encontrado.")
    return a


@router.get("", response_model=list[AgendamentoOut])
def listar(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    veterinario_id: int | None = None,
    animal_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    q = db.query(Agendamento)
    if data_inicio:
        q = q.filter(Agendamento.data_hora >= datetime.combine(data_inicio, time.min))
    if data_fim:
        q = q.filter(Agendamento.data_hora <= datetime.combine(data_fim, time.max))
    if veterinario_id:
        q = q.filter(Agendamento.veterinario_id == veterinario_id)
    if animal_id:
        q = q.filter(Agendamento.animal_id == animal_id)
    if status:
        q = q.filter(Agendamento.status.in_(status.split(",")))
    return [agendamento_out(a) for a in q.order_by(Agendamento.data_hora)]


# Precisa vir antes de "/{id}" para o FastAPI não tentar ler "disponibilidade" como número
@router.get("/disponibilidade", response_model=DisponibilidadeOut)
def disponibilidade(
    veterinario_id: int,
    data: date,
    duracao_min: int = Query(30, ge=15, le=240),
    ignorar_id: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    """Horários livres do veterinário no dia (preenche o campo "Horário" do popup)."""
    vet = db.get(Veterinario, veterinario_id)
    if not vet:
        raise HTTPException(404, "Veterinário não encontrado.")
    livres, mensagem = horarios_livres(db, vet, data, duracao_min, ignorar_id)
    return DisponibilidadeOut(horarios=livres, mensagem=mensagem)


@router.get("/{id}", response_model=AgendamentoOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(LEITURA)):
    return agendamento_out(_obter(db, id))


@router.post("", response_model=AgendamentoOut, status_code=201)
def criar(dados: AgendamentoIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    if dados.data_hora < datetime.now() - timedelta(minutes=5):
        raise HTTPException(400, "Não é possível agendar em uma data/horário que já passou.")
    validar_agendamento(db, dados)
    ag = Agendamento(**dados.model_dump(), status="agendado")
    db.add(ag)
    db.commit()
    db.refresh(ag)
    return agendamento_out(ag)


@router.put("/{id}", response_model=AgendamentoOut)
def atualizar(id: int, dados: AgendamentoIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    ag = _obter(db, id)
    if ag.status in FINALIZADOS:
        raise HTTPException(400, "Agendamentos concluídos ou cancelados não podem ser alterados.")
    validar_agendamento(db, dados, ignorar_id=id)
    for campo, valor in dados.model_dump().items():
        setattr(ag, campo, valor)
    db.commit()
    db.refresh(ag)
    return agendamento_out(ag)


@router.post("/{id}/cancelamento", response_model=AgendamentoOut)
def cancelar(id: int, dados: CancelamentoIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    """Popup "Cancelar consulta": registra o motivo e a justificativa e libera o horário."""
    ag = _obter(db, id)
    if ag.status in FINALIZADOS:
        raise HTTPException(400, "Este agendamento já foi finalizado.")
    ag.status = "cancelado"
    ag.cancelamento_motivo = dados.motivo
    ag.cancelamento_justificativa = dados.justificativa.strip()
    db.commit()
    return agendamento_out(ag)


@router.patch("/{id}/status", response_model=AgendamentoOut)
def alterar_status(id: int, dados: StatusAgendamentoIn, db: Session = Depends(get_db), _=Depends(MUDAR_STATUS)):
    """Recepção: confirmar / registrar chegada. Veterinário: iniciar e concluir atendimento."""
    ag = _obter(db, id)
    if ag.status in FINALIZADOS and dados.status != ag.status:
        raise HTTPException(400, "Este agendamento já foi finalizado.")
    ag.status = dados.status
    db.commit()
    return agendamento_out(ag)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    db.delete(_obter(db, id))
    db.commit()
    return Response(status_code=204)
