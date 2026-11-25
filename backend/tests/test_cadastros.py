"""Módulo de Cadastros — REQ 04, 05, 06."""


def test_req04_crud_tutor_e_validacoes(cliente, recepcao, admin):
    dados = {"nome": "Tutor Teste", "telefone": "(71) 99999-0000", "cpf": "123.456.789-09", "cep": "40000-000"}
    r = cliente.post("/api/tutores", headers=recepcao, json=dados)
    assert r.status_code == 201
    tid = r.json()["id"]
    assert cliente.post("/api/tutores", headers=recepcao, json={**dados, "telefone": "(71) 98888-0000"}).status_code == 409  # CPF
    assert cliente.post("/api/tutores", headers=recepcao, json={**dados, "cpf": "123"}).status_code == 422
    assert cliente.get("/api/tutores", headers=recepcao, params={"q": "Tutor Teste"}).json()["total"] == 1
    assert cliente.delete(f"/api/tutores/{tid}", headers=admin).status_code == 204


def test_req04_tutor_com_animais_nao_e_excluido(cliente, admin):
    assert cliente.delete("/api/tutores/1", headers=admin).status_code == 409


def test_req05_animal_vinculado_a_tutor(cliente, recepcao):
    base = {"nome": "Bolinha", "especie": "Cão", "sexo": "Fêmea", "tutor_id": 999}
    assert cliente.post("/api/animais", headers=recepcao, json=base).status_code == 400
    assert cliente.post("/api/animais", headers=recepcao, json={**base, "tutor_id": 1, "data_nascimento": "2999-01-01"}).status_code == 422
    r = cliente.post("/api/animais", headers=recepcao, json={**base, "tutor_id": 1, "raca": "SRD"})
    assert r.status_code == 201 and r.json()["tutor_nome"]


def test_req05_busca_por_animal_ou_tutor(cliente, veterinaria):
    nomes = [a["nome"] for a in cliente.get("/api/animais", headers=veterinaria, params={"q": "Ana Paula"}).json()["itens"]]
    assert "Thor" in nomes


def test_req06_veterinario_horarios_e_crmv(cliente, admin):
    vet = {"nome": "Vet Teste", "crmv": "CRMV-BA 99999", "especialidade": "Cirurgia",
           "horarios": [{"dia": "Segunda", "inicio": "08:00", "fim": "12:00", "ativo": True}]}
    assert cliente.post("/api/veterinarios", headers=admin, json=vet).status_code == 201
    assert cliente.post("/api/veterinarios", headers=admin, json=vet).status_code == 409
    invalido = {**vet, "crmv": "CRMV-BA 88888", "horarios": [{"dia": "Segunda", "inicio": "12:00", "fim": "08:00"}]}
    assert cliente.post("/api/veterinarios", headers=admin, json=invalido).status_code == 422
