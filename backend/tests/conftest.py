"""Configuração dos testes: cada execução usa um banco temporário, populado com os dados de exemplo."""
import os
import tempfile

import pytest

os.environ["VETCARE_DB"] = os.path.join(tempfile.mkdtemp(), "teste.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def cliente():
    with TestClient(app) as c:
        yield c


def _token(cliente, email):
    r = cliente.post("/api/auth/login", json={"email": email, "senha": "vetcare123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture(scope="session")
def admin(cliente):
    return _token(cliente, "alex@vetcare.com")


@pytest.fixture(scope="session")
def recepcao(cliente):
    return _token(cliente, "marina@vetcare.com")


@pytest.fixture(scope="session")
def veterinaria(cliente):
    return _token(cliente, "camila.r@vetcare.com")
