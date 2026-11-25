"""Módulo de Autenticação — REQ 01, 02, 03 e controle de acesso (ADR 008)."""


def test_req02_login_valido_e_invalido(cliente):
    assert cliente.post("/api/auth/login", json={"email": "alex@vetcare.com", "senha": "vetcare123"}).status_code == 200
    assert cliente.post("/api/auth/login", json={"email": "alex@vetcare.com", "senha": "errada"}).status_code == 401


def test_req02_rota_protegida_exige_token(cliente):
    assert cliente.get("/api/tutores").status_code == 401


def test_req02_usuario_inativo_nao_entra(cliente):
    r = cliente.post("/api/auth/login", json={"email": "daniela.f@vetcare.com", "senha": "vetcare123"})
    assert r.status_code == 403


def test_veterinaria_vinculada_ao_cadastro(cliente, veterinaria):
    assert cliente.get("/api/auth/me", headers=veterinaria).json()["veterinario_id"] is not None


def test_req01_crud_usuario(cliente, admin):
    novo = {"nome": "Teste Usuário", "email": "teste.usuario@vetcare.com", "perfil": "recepcionista", "senha": "abc123"}
    r = cliente.post("/api/usuarios", headers=admin, json=novo)
    assert r.status_code == 201
    uid = r.json()["id"]
    assert cliente.post("/api/usuarios", headers=admin, json=novo).status_code == 409  # e-mail duplicado
    r = cliente.put(f"/api/usuarios/{uid}", headers=admin, json={**novo, "nome": "Outro Nome", "senha": None})
    assert r.json()["nome"] == "Outro Nome"
    assert cliente.delete(f"/api/usuarios/{uid}", headers=admin).status_code == 204


def test_permissoes_por_perfil(cliente, recepcao, veterinaria):
    assert cliente.get("/api/usuarios", headers=recepcao).status_code == 403
    assert cliente.post("/api/tutores", headers=veterinaria, json={"nome": "X Y", "telefone": "71999990000"}).status_code == 403
    assert cliente.delete("/api/tutores/3", headers=recepcao).status_code == 403  # recepção não exclui por padrão


def test_adr008_permissao_ajustada_por_usuario(cliente, admin):
    r = cliente.get("/api/usuarios/permissoes-padrao", headers=admin).json()
    perms = r["padrao"]["recepcionista"]
    perms["relatorios"] = {"ver": True, "editar": False, "excluir": False}
    usuarios = cliente.get("/api/usuarios", headers=admin, params={"q": "mariana"}).json()
    u = usuarios[0]
    r = cliente.put(f"/api/usuarios/{u['id']}", headers=admin,
                    json={"nome": u["nome"], "email": u["email"], "perfil": "recepcionista", "permissoes": perms})
    assert r.json()["modulos_extras"] == ["relatorios"]


def test_admin_nao_remove_propria_permissao(cliente, admin):
    eu = cliente.get("/api/auth/me", headers=admin).json()
    perms = eu["permissoes"]
    perms["usuarios"]["editar"] = False
    r = cliente.put(f"/api/usuarios/{eu['id']}", headers=admin,
                    json={"nome": eu["nome"], "email": eu["email"], "perfil": "administrador", "permissoes": perms})
    assert r.status_code == 400


def test_req03_recuperar_e_redefinir_senha(cliente, capsys):
    assert cliente.post("/api/auth/recuperar-senha", json={"email": "paulo.s@vetcare.com"}).status_code == 200
    codigo = capsys.readouterr().out.split("paulo.s@vetcare.com: ")[1][:6]
    r = cliente.post("/api/auth/redefinir-senha", json={"email": "paulo.s@vetcare.com", "codigo": "000000", "nova_senha": "nova123"})
    assert r.status_code == 400
    r = cliente.post("/api/auth/redefinir-senha", json={"email": "paulo.s@vetcare.com", "codigo": codigo, "nova_senha": "nova123"})
    assert r.status_code == 200
    assert cliente.post("/api/auth/login", json={"email": "paulo.s@vetcare.com", "senha": "nova123"}).status_code == 200
