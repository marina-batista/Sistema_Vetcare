"""Monta a resposta de agendamento com os dados do animal, tutor e veterinário."""
from .esquemas import AgendamentoOut
from .modelos import Agendamento


def agendamento_out(a: Agendamento) -> AgendamentoOut:
    return AgendamentoOut(
        id=a.id, animal_id=a.animal_id, animal_nome=a.animal.nome,
        animal_especie=a.animal.especie, animal_raca=a.animal.raca,
        animal_nascimento=a.animal.data_nascimento, tutor_id=a.animal.tutor_id,
        tutor_nome=a.animal.tutor.nome, veterinario_id=a.veterinario_id,
        veterinario_nome=a.veterinario.nome, data_hora=a.data_hora,
        duracao_min=a.duracao_min, tipo=a.tipo, status=a.status, observacoes=a.observacoes,
        cancelamento_motivo=a.cancelamento_motivo, cancelamento_justificativa=a.cancelamento_justificativa,
    )
