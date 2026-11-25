"""Módulo de Agendamento — REQ 07, 08, 09 e Validador de Disponibilidade (ADR 011)."""
from datetime import date, timedelta

PROXIMA_SEGUNDA = date.today() + timedelta(days=7 - date.today().weekday())


def _agendar(cliente, headers, hora, animal_id=1, vet_id=1, dia=PROXIMA_SEGUNDA):
    return cliente.post("/api/agendamentos", headers=headers,
                        json={"animal_id": animal_id, "veterinario_id": vet_id, "data_hora": f"{dia}T{hora}"})


def test_validador_oferece_horarios_livres(cliente, recepcao):
    r = cliente.get("/api/agendamentos/disponibilidade", headers=recepcao,
                    params={"veterinario_id": 1, "data": PROXIMA_SEGUNDA.isoformat()}).json()
    assert r["horarios"][0] == "08:00"
    domingo = PROXIMA_SEGUNDA + timedelta(days=6)
    r = cliente.get("/api/agendamentos/disponibilidade", headers=recepcao,
                    params={"veterinario_id": 1, "data": domingo.isoformat()}).json()
    assert r["horarios"] == [] and "Domingo" in r["mensagem"]


def test_req07_agendar_e_regras(cliente, recepcao):
    assert _agendar(cliente, recepcao, "10:00").status_code == 201
    assert _agendar(cliente, recepcao, "10:15", animal_id=2).status_code == 409   # choque com o mesmo veterinário
    assert _agendar(cliente, recepcao, "10:00", vet_id=2).status_code == 409      # mesmo animal no mesmo horário
    assert _agendar(cliente, recepcao, "20:00", animal_id=2).status_code == 400   # fora do expediente
    assert _agendar(cliente, recepcao, "10:00", dia=date.today() - timedelta(days=3)).status_code == 400  # passado


def test_req08_cancelar_libera_horario(cliente, recepcao):
    ag = _agendar(cliente, recepcao, "11:00").json()
    r = cliente.post(f"/api/agendamentos/{ag['id']}/cancelamento", headers=recepcao,
                     json={"motivo": "Cancelada pelo tutor", "justificativa": "Animal em viagem."})
    assert r.json()["status"] == "cancelado" and r.json()["cancelamento_motivo"] == "Cancelada pelo tutor"
    assert _agendar(cliente, recepcao, "11:00", animal_id=3).status_code == 201  # horário liberado


def test_req09_consultar_agenda_por_dia_e_profissional(cliente, recepcao):
    hoje = date.today().isoformat()
    todos = cliente.get("/api/agendamentos", headers=recepcao, params={"data_inicio": hoje, "data_fim": hoje}).json()
    camila = cliente.get("/api/agendamentos", headers=recepcao,
                         params={"data_inicio": hoje, "data_fim": hoje, "veterinario_id": 1}).json()
    assert len(todos) > len(camila) > 0
    assert all(a["veterinario_id"] == 1 for a in camila)


def test_veterinaria_inicia_atendimento(cliente, veterinaria):
    hoje = date.today().isoformat()
    ag = next(a for a in cliente.get("/api/agendamentos", headers=veterinaria,
                                     params={"data_inicio": hoje, "data_fim": hoje, "veterinario_id": 1}).json()
              if a["status"] == "aguardando")
    r = cliente.patch(f"/api/agendamentos/{ag['id']}/status", headers=veterinaria, json={"status": "em_atendimento"})
    assert r.status_code == 200


def test_saude(cliente):
    assert cliente.get("/api/saude").json()["status"] == "ok"
