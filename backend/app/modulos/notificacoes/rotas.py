"""REQ 16 – Notificar Tutor: lembretes de consultas agendadas e de vacinas a vencer.
O registro do envio é persistido; o disparo real (WhatsApp/e-mail) é simulado (ver ADR)."""
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.seguranca import requer_permissao
from ..agendamento.modelos import Agendamento
from ..clinico.modelos import Vacina
from .esquemas import (
    ConfiguracaoIn,
    EnvioIn,
    NotificacaoHistorico,
    NotificacaoPendente,
)
from .modelos import ConfiguracaoNotificacao, Notificacao

router = APIRouter(prefix="/notificacoes", tags=["Notificações (REQ 16)"])
LEITURA = requer_permissao(("agenda", "ver"))
EDITAR = requer_permissao(("agenda", "editar"))


def _canal_do_tutor(tutor) -> str:
    return "E-mail" if (tutor and tutor.email) else "WhatsApp"


def _enviadas(db: Session) -> set[str]:
    return {n.referencia for n in db.query(Notificacao.referencia).all()}


@router.get("/consultas", response_model=list[NotificacaoPendente])
def pendentes_consultas(db: Session = Depends(get_db), _=Depends(LEITURA)):
    """Lembretes das consultas dos próximos 7 dias (status agendado/confirmado)."""
    hoje = datetime.now()
    limite = datetime.combine(date.today() + timedelta(days=7), time.max)
    ags = db.query(Agendamento).filter(
        Agendamento.data_hora >= hoje,
        Agendamento.data_hora <= limite,
        Agendamento.status.in_(["agendado", "confirmado"]),
    ).order_by(Agendamento.data_hora).all()
    enviadas = _enviadas(db)
    saida = []
    for a in ags:
        ref = f"consulta-{a.id}"
        envio_em = a.data_hora - timedelta(hours=24)
        tutor = a.animal.tutor
        if ref in enviadas:
            situacao = "Enviada"
        elif envio_em < hoje:
            situacao = "Pendente"
        else:
            situacao = "Agendada"
        saida.append(NotificacaoPendente(
            referencia=ref, tipo="consulta", tutor_nome=tutor.nome, animal_nome=a.animal.nome,
            assunto=f"Lembrete de consulta · {a.data_hora.strftime('%d/%m %H:%M')}",
            envio=envio_em.strftime("%d/%m %H:%M"), canal=_canal_do_tutor(tutor), situacao=situacao,
        ))
    return saida


@router.get("/vacinas", response_model=list[NotificacaoPendente])
def pendentes_vacinas(db: Session = Depends(get_db), _=Depends(LEITURA)):
    """Avisos de vacinas que vencem nos próximos 30 dias."""
    hoje = date.today()
    limite = hoje + timedelta(days=30)
    vacinas = db.query(Vacina).filter(
        Vacina.proxima_dose.isnot(None),
        Vacina.proxima_dose >= hoje,
        Vacina.proxima_dose <= limite,
    ).order_by(Vacina.proxima_dose).all()
    enviadas = _enviadas(db)
    saida = []
    for v in vacinas:
        ref = f"vacina-{v.id}"
        dias = (v.proxima_dose - hoje).days
        quando = "hoje" if dias == 0 else f"em {dias} dia{'s' if dias > 1 else ''}"
        tutor = v.animal.tutor
        saida.append(NotificacaoPendente(
            referencia=ref, tipo="vacina", tutor_nome=tutor.nome, animal_nome=v.animal.nome,
            assunto=f"Vacina {v.vacina} vence {quando}", envio="Hoje 08:00",
            canal=_canal_do_tutor(tutor), situacao="Enviada" if ref in enviadas else "Agendada",
        ))
    return saida


@router.get("/historico", response_model=list[NotificacaoHistorico])
def historico(db: Session = Depends(get_db), _=Depends(LEITURA)):
    return db.query(Notificacao).order_by(Notificacao.enviada_em.desc()).limit(100).all()


@router.post("/enviar", response_model=list[NotificacaoHistorico], status_code=201)
def enviar(dados: EnvioIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    """Marca as notificações selecionadas como enviadas (disparo simulado)."""
    enviadas = _enviadas(db)
    criadas = []
    for item in dados.itens:
        if item.referencia in enviadas:
            continue
        n = Notificacao(
            referencia=item.referencia, tipo=item.tipo, tutor_nome=item.tutor_nome,
            animal_nome=item.animal_nome, assunto=item.assunto, canal=item.canal,
        )
        db.add(n)
        criadas.append(n)
    db.commit()
    for n in criadas:
        db.refresh(n)
    return criadas


@router.get("/config", response_model=ConfiguracaoIn)
def obter_config(db: Session = Depends(get_db), _=Depends(LEITURA)):
    cfg = db.get(ConfiguracaoNotificacao, 1)
    return ConfiguracaoIn(**(cfg.opcoes if cfg else {}))


@router.put("/config", response_model=ConfiguracaoIn)
def salvar_config(dados: ConfiguracaoIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    cfg = db.get(ConfiguracaoNotificacao, 1)
    if not cfg:
        cfg = ConfiguracaoNotificacao(id=1)
        db.add(cfg)
    cfg.opcoes = dados.model_dump()
    db.commit()
    return dados
