"""Validador de Disponibilidade (Etapa 1, Figura 1): impede agendamentos fora do expediente do
veterinário e choques de horário do mesmo veterinário ou do mesmo animal. Também calcula os horários
livres oferecidos no popup "Novo agendamento" (tática de Prevenção de Erros — ADR 006)."""
from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..cadastros.esquemas import DIAS
from ..cadastros.modelos import Animal, Veterinario
from .esquemas import AgendamentoIn
from .modelos import Agendamento

INTERVALO_MIN = 30  # grade de horários oferecidos no popup


def agendamentos_do_dia(db: Session, dia: date, ignorar_id: int | None):
    q = db.query(Agendamento).filter(
        Agendamento.status != "cancelado",
        Agendamento.data_hora >= datetime.combine(dia, time.min),
        Agendamento.data_hora <= datetime.combine(dia, time.max),
    )
    if ignorar_id:
        q = q.filter(Agendamento.id != ignorar_id)
    return q


def expediente(vet: Veterinario, dia: date) -> dict | None:
    nome_dia = DIAS[dia.weekday()]
    return next((h for h in (vet.horarios or []) if h.get("dia") == nome_dia and h.get("ativo")), None)


def validar_agendamento(db: Session, dados: AgendamentoIn, ignorar_id: int | None = None) -> None:
    """Regras de negócio: animal e veterinário existem, dentro do expediente e sem conflito."""
    animal = db.get(Animal, dados.animal_id)
    if not animal:
        raise HTTPException(400, "Animal não encontrado.")
    vet = db.get(Veterinario, dados.veterinario_id)
    if not vet:
        raise HTTPException(400, "Veterinário não encontrado.")
    if not vet.ativo:
        raise HTTPException(400, f"{vet.nome} está inativo(a) e não recebe agendamentos.")

    inicio = dados.data_hora
    fim = inicio + timedelta(minutes=dados.duracao_min)
    dia = DIAS[inicio.weekday()]
    exp = expediente(vet, inicio.date())
    if not exp:
        raise HTTPException(400, f"{vet.nome} não atende neste dia ({dia}).")
    if inicio.strftime("%H:%M") < exp["inicio"] or fim.strftime("%H:%M") > exp["fim"] or fim.date() != inicio.date():
        raise HTTPException(400, f"Fora do expediente de {vet.nome} ({dia}, {exp['inicio']}–{exp['fim']}).")

    for ag in agendamentos_do_dia(db, inicio.date(), ignorar_id).all():
        ag_fim = ag.data_hora + timedelta(minutes=ag.duracao_min)
        sobrepoe = inicio < ag_fim and ag.data_hora < fim
        if sobrepoe and ag.veterinario_id == vet.id:
            raise HTTPException(409, f"{vet.nome} já tem {ag.tipo.lower()} de {ag.animal.nome} às {ag.data_hora:%H:%M}.")
        if sobrepoe and ag.animal_id == animal.id:
            raise HTTPException(409, f"{animal.nome} já tem um agendamento às {ag.data_hora:%H:%M}.")


def horarios_livres(db: Session, vet: Veterinario, data: date, duracao_min: int,
                    ignorar_id: int | None = None) -> tuple[list[str], str | None]:
    """Retorna (horários livres "HH:MM", mensagem quando não houver nenhum)."""
    if not vet.ativo:
        return [], "Profissional inativo"
    if data < date.today():
        return [], "Data já passou"
    exp = expediente(vet, data)
    if not exp:
        return [], f"Não atende neste dia ({DIAS[data.weekday()]})"
    ocupados = [(ag.data_hora, ag.data_hora + timedelta(minutes=ag.duracao_min))
                for ag in agendamentos_do_dia(db, data, ignorar_id).filter(Agendamento.veterinario_id == vet.id)]
    slot = datetime.combine(data, time.fromisoformat(exp["inicio"]))
    limite = datetime.combine(data, time.fromisoformat(exp["fim"]))
    duracao, agora, livres = timedelta(minutes=duracao_min), datetime.now(), []
    while slot + duracao <= limite:
        if slot >= agora and not any(slot < f and i < slot + duracao for i, f in ocupados):
            livres.append(slot.strftime("%H:%M"))
        slot += timedelta(minutes=INTERVALO_MIN)
    return livres, None if livres else "Sem horários livres neste dia"
