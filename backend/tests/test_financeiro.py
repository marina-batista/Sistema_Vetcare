"""Testes do módulo Financeiro — REQ 14 (Pagamento), 15 (Dashboard), 17 (Relatório)."""
from datetime import date


def test_tabela_precos(cliente, recepcao):
    r = cliente.get("/api/pagamentos/precos", headers=recepcao)
    assert r.status_code == 200
    assert r.json()["Consulta"] > 0


def test_registrar_pagamento(cliente, recepcao):
    hoje = date.today().isoformat()
    ags = cliente.get("/api/agendamentos", headers=recepcao,
                      params={"data_inicio": hoje, "data_fim": hoje}).json()
    alvo = ags[0]
    r = cliente.post("/api/pagamentos", headers=recepcao, json={
        "agendamento_id": alvo["id"], "valor": 180.0, "forma": "Pix", "data": hoje,
    })
    assert r.status_code == 201, r.text
    assert r.json()["animal_nome"] == alvo["animal_nome"]  # deriva o animal do agendamento


def test_pagamento_recusa_valor_zero(cliente, recepcao):
    r = cliente.post("/api/pagamentos", headers=recepcao,
                     json={"valor": 0, "forma": "Pix", "data": date.today().isoformat()})
    assert r.status_code == 422


def test_dashboard_financeiro(cliente, admin):
    r = cliente.get("/api/financeiro/dashboard", headers=admin, params={"periodo": "mes"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["recebido"] >= 0
    assert len(d["series"]) == 6  # últimas 6 semanas
    assert len(d["formas"]) == 3  # Pix, Cartão, Dinheiro


def test_dashboard_exige_permissao_relatorios(cliente, recepcao):
    # Recepcionista não tem acesso ao financeiro/relatórios
    r = cliente.get("/api/financeiro/dashboard", headers=recepcao, params={"periodo": "mes"})
    assert r.status_code == 403


def test_relatorio_faturamento(cliente, admin):
    r = cliente.get("/api/financeiro/relatorio-faturamento", headers=admin,
                    params={"data_inicio": "2026-01-01", "data_fim": date.today().isoformat()})
    assert r.status_code == 200, r.text
    assert r.json()["total_valor"] >= 0
