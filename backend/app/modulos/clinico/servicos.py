"""Monta as respostas do módulo Clínico (inclui a situação da vacina pela próxima dose)."""
from datetime import date, timedelta

from .esquemas import AtendimentoOut, Medicamento, PrescricaoOut, VacinaOut
from .modelos import Atendimento, Prescricao, Vacina


def situacao_vacina(proxima: date | None) -> str:
    if not proxima:
        return "Dose única"
    hoje = date.today()
    if proxima < hoje:
        return "Vencida"
    if proxima == hoje:
        return "Vence hoje"
    if proxima <= hoje + timedelta(days=30):
        return "Vence em breve"
    return "Em dia"


def atendimento_out(a: Atendimento) -> AtendimentoOut:
    return AtendimentoOut(
        id=a.id, animal_id=a.animal_id, animal_nome=a.animal.nome, agendamento_id=a.agendamento_id,
        data_hora=a.data_hora, anamnese=a.anamnese, exame_fisico=a.exame_fisico, temperatura=a.temperatura,
        freq_cardiaca=a.freq_cardiaca, peso=a.peso, diagnostico=a.diagnostico, procedimentos=a.procedimentos,
        observacoes=a.observacoes, veterinario_nome=a.veterinario_nome,
    )


def vacina_out(v: Vacina) -> VacinaOut:
    return VacinaOut(
        id=v.id, animal_id=v.animal_id, animal_nome=v.animal.nome, vacina=v.vacina, fabricante=v.fabricante,
        lote=v.lote, data_aplicacao=v.data_aplicacao, proxima_dose=v.proxima_dose, observacoes=v.observacoes,
        veterinario_nome=v.veterinario_nome, situacao=situacao_vacina(v.proxima_dose),
    )


def prescricao_out(p: Prescricao) -> PrescricaoOut:
    return PrescricaoOut(
        id=p.id, animal_id=p.animal_id, animal_nome=p.animal.nome, tutor_nome=p.animal.tutor.nome,
        atendimento_id=p.atendimento_id, data=p.data, veterinario_nome=p.veterinario_nome,
        medicamentos=[Medicamento(**m) for m in (p.medicamentos or [])], observacoes=p.observacoes,
    )
