"""Testes do módulo de Notificações — REQ 16 (Notificar Tutor)."""


def test_lista_consultas_pendentes(cliente, recepcao):
    r = cliente.get("/api/notificacoes/consultas", headers=recepcao)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_lista_vacinas_a_vencer(cliente, recepcao):
    r = cliente.get("/api/notificacoes/vacinas", headers=recepcao)
    assert r.status_code == 200
    # O seed cria vacinas vencendo em breve
    assert any(n["tipo"] == "vacina" for n in r.json())


def test_enviar_notificacao_registra_historico(cliente, recepcao):
    pendentes = cliente.get("/api/notificacoes/consultas", headers=recepcao).json()
    if not pendentes:
        return
    item = pendentes[0]
    r = cliente.post("/api/notificacoes/enviar", headers=recepcao, json={"itens": [{
        "referencia": item["referencia"], "tipo": item["tipo"], "tutor_nome": item["tutor_nome"],
        "animal_nome": item["animal_nome"], "assunto": item["assunto"], "canal": item["canal"],
    }]})
    assert r.status_code == 201, r.text
    historico = cliente.get("/api/notificacoes/historico", headers=recepcao).json()
    assert any(h["assunto"] == item["assunto"] for h in historico)
    # A mesma consulta agora aparece como "Enviada"
    atual = cliente.get("/api/notificacoes/consultas", headers=recepcao).json()
    marcada = next((n for n in atual if n["referencia"] == item["referencia"]), None)
    assert marcada is None or marcada["situacao"] == "Enviada"


def test_salvar_configuracao(cliente, recepcao):
    r = cliente.put("/api/notificacoes/config", headers=recepcao,
                    json={"lembrete24h": True, "vacina7d": True, "whatsapp": True, "email": False})
    assert r.status_code == 200
    assert cliente.get("/api/notificacoes/config", headers=recepcao).json()["lembrete24h"] is True
