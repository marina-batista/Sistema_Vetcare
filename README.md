# VetCare — Sistema de Gestão Veterinária

Sistema de gerenciamento para clínicas veterinárias desenvolvido para a disciplina Engenharia de Software 1 (UFBA).

**Integrantes:** Alex Maycon, Gabrielly Santos e Marina Rocha  

---

## 📌 Requisitos da Sprint 1

Módulos de **Autenticação**, **Cadastros** e **Agendamento** implementados no backend e frontend:

| Requisito | Descrição | Status |
| :--- | :--- | :--- |
| **REQ 01** | Manter Usuário | ✅ Implementado |
| **REQ 02** | Autenticar Usuário | ✅ Implementado |
| **REQ 03** | Recuperar Senha | ✅ Implementado |
| **REQ 04** | Manter Tutor | ✅ Implementado |
| **REQ 05** | Manter Animal | ✅ Implementado |
| **REQ 06** | Manter Veterinário | ✅ Implementado |
| **REQ 07** | Agendar Consulta | ✅ Implementado |
| **REQ 08** | Cancelar Consulta | ✅ Implementado |
| **REQ 09** | Consultar Agenda | ✅ Implementado |
| **REQ 10 a 17** | Módulos Clínico, Financeiro e Notificações | 🖼️ Telas prontas (Próxima Sprint) |

---

## 🛠️ Arquitetura e Decisões (ADRs)

* **Estilo Arquitetural:** Monolito Modular em 3 camadas (Apresentação, Negócio e Persistência).
* **Tecnologias:** Python (FastAPI + SQLAlchemy + SQLite) no backend e HTML/CSS/JavaScript no frontend.
* **Decisões Arquiteturais:** O detalhamento das ADRs (007 a 013) encontra-se na pasta `docs/adr/`.

---

## 🚀 Como rodar o projeto

1. Entrar na pasta do backend:
   ```bash
   cd backend
   ```

2. Criar e ativar o ambiente virtual:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **Mac/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Instalar dependências e iniciar o servidor:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. Abrir no navegador:
   * **Sistema:** `http://localhost:8000`
   * **Documentação da API:** `http://localhost:8000/docs`

---

## 🔑 Usuários de teste (Senha: `vetcare123`)

* **Admin:** `alex@vetcare.com`
* **Recepção:** `marina@vetcare.com`
* **Veterinária:** `camila.r@vetcare.com`

---

## 🧪 Testes automatizados

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest
```
