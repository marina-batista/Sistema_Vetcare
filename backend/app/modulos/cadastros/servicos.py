"""Monta as respostas de tutor e animal com campos calculados (última visita, em atendimento).
Usa as relações do ORM, sem importar o módulo de Agendamento."""
from datetime import datetime

from .esquemas import AnimalOut, TutorOut
from .modelos import Animal, Tutor


def _ultima_visita(agendamentos) -> datetime | None:
    agora = datetime.now()
    return max((a.data_hora for a in agendamentos if a.status != "cancelado" and a.data_hora <= agora), default=None)


def tutor_out(t: Tutor) -> TutorOut:
    return TutorOut(
        id=t.id, nome=t.nome, cpf=t.cpf, telefone=t.telefone, email=t.email, cep=t.cep,
        endereco=t.endereco, numero=t.numero, bairro=t.bairro, cidade=t.cidade,
        qtd_animais=len(t.animais),
        ultima_visita=_ultima_visita([ag for animal in t.animais for ag in animal.agendamentos]),
    )


def animal_out(a: Animal) -> AnimalOut:
    return AnimalOut(
        id=a.id, nome=a.nome, especie=a.especie, raca=a.raca, sexo=a.sexo,
        data_nascimento=a.data_nascimento, tutor_id=a.tutor_id, tutor_nome=a.tutor.nome,
        ultimo_atendimento=_ultima_visita(a.agendamentos),
        em_atendimento=any(ag.status == "em_atendimento" for ag in a.agendamentos),
    )
