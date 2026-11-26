"""Testes do módulo Clínico — REQ 10 (Atendimento), 11 (Prontuário), 12 (Vacina), 13 (Prescrição)."""
from datetime import date


def _animal_id(cliente, veterinaria):
    return cliente.get("/api/animais", headers=veterinaria).json()["itens"][0]["id"]


def test_prontuario_lista_atendimentos_do_seed(cliente, veterinaria):
    animal = _animal_id(cliente, veterinaria)
    r = cliente.get("/api/atendimentos", headers=veterinaria, params={"animal_id": animal})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_registrar_atendimento_conclui_agendamento(cliente, veterinaria):
    hoje = date.today().isoformat()
    ags = cliente.get("/api/agendamentos", headers=veterinaria,
                      params={"data_inicio": hoje, "data_fim": hoje}).json()
    alvo = next(a for a in ags if a["status"] in ("aguardando", "em_atendimento"))
    r = cliente.post("/api/atendimentos", headers=veterinaria, json={
        "animal_id": alvo["animal_id"], "agendamento_id": alvo["id"],
        "diagnostico": "Teste de atendimento", "anamnese": "sem queixas",
    })
    assert r.status_code == 201, r.text
    assert r.json()["veterinario_nome"]  # registra o nome do veterinário
    # O agendamento vinculado deve ter sido concluído
    assert cliente.get(f"/api/agendamentos/{alvo['id']}", headers=veterinaria).json()["status"] == "concluido"


def test_recepcao_nao_registra_atendimento(cliente, recepcao):
    animal = cliente.get("/api/animais", headers=recepcao).json()["itens"][0]["id"]
    r = cliente.post("/api/atendimentos", headers=recepcao, json={"animal_id": animal, "diagnostico": "x"})
    assert r.status_code == 403


def test_registrar_vacina_calcula_situacao(cliente, veterinaria):
    animal = _animal_id(cliente, veterinaria)
    r = cliente.post("/api/vacinas", headers=veterinaria, json={
        "animal_id": animal, "vacina": "V10", "data_aplicacao": date.today().isoformat(),
        "proxima_dose": "2030-01-01",
    })
    assert r.status_code == 201, r.text
    assert r.json()["situacao"] == "Em dia"


def test_vacina_nao_aceita_aplicacao_futura(cliente, veterinaria):
    animal = _animal_id(cliente, veterinaria)
    r = cliente.post("/api/vacinas", headers=veterinaria, json={
        "animal_id": animal, "vacina": "V10", "data_aplicacao": "2099-01-01",
    })
    assert r.status_code == 422


def test_emitir_prescricao(cliente, veterinaria):
    animal = _animal_id(cliente, veterinaria)
    r = cliente.post("/api/prescricoes", headers=veterinaria, json={
        "animal_id": animal, "medicamentos": [{"nome": "Dipirona", "dosagem": "1 comprimido"}],
        "observacoes": "após a refeição",
    })
    assert r.status_code == 201, r.text
    assert r.json()["medicamentos"][0]["nome"] == "Dipirona"
    assert r.json()["tutor_nome"]  # inclui o tutor do animal


def test_prescricao_exige_medicamento(cliente, veterinaria):
    animal = _animal_id(cliente, veterinaria)
    r = cliente.post("/api/prescricoes", headers=veterinaria, json={"animal_id": animal, "medicamentos": []})
    assert r.status_code == 422
