# VetCare — Sistema de Gestão Veterinária

Trabalho Final da disciplina **Engenharia de Software 1 (UFBA)**.  
**Integrantes:** Alex Maycon Lima Dos Santos, Gabrielly Santos Farias e Marina Batista Rocha  

---

## 📌 Sobre o Projeto

O **VetCare** é uma solução completa para gerenciamento operacional, clínico e financeiro de clínicas veterinárias.  

A aplicação adota a arquitetura de **Monolito Modular em Camadas** (ADR 002 e ADR 007):
* **Backend:** Python 3.10+ com FastAPI, SQLAlchemy e SQLite
* **Frontend:** HTML5, CSS3 e JavaScript Vanilla
* **Autenticação:** Sessão por token e controle de acesso baseado em papéis (RBAC - ADR 008)

---

## 🎯 Requisitos Funcionais Implementados (100%)

O projeto cobre **100% dos requisitos funcionais (17 de 17)** previstos na especificação do sistema:

| Requisito | Descrição | Módulo | Situação |
| :--- | :--- | :--- | :--- |
| **REQ 01** | Manter Usuário | Autenticação | ✅ Implementado |
| **REQ 02** | Autenticar Usuário | Autenticação | ✅ Implementado |
| **REQ 03** | Recuperar Senha | Autenticação | ✅ Implementado (ADR 012) |
| **REQ 04** | Manter Tutor | Cadastros | ✅ Implementado (ViaCEP) |
| **REQ 05** | Manter Animal | Cadastros | ✅ Implementado |
| **REQ 06** | Manter Veterinário | Cadastros | ✅ Implementado |
| **REQ 07** | Agendar Consulta | Agendamento | ✅ Implementado |
| **REQ 08** | Cancelar Consulta | Agendamento | ✅ Implementado |
| **REQ 09** | Consultar Agenda | Agendamento | ✅ Implementado |
| **REQ 10** | Registrar Atendimento | Clínico | ✅ Implementado |
| **REQ 11** | Manter Prontuário | Clínico | ✅ Implementado |
| **REQ 12** | Registrar Vacinação | Clínico | ✅ Implementado |
| **REQ 13** | Emitir Prescrição | Clínico | ✅ Implementado (ADR 015) |
| **REQ 14** | Registrar Pagamento | Financeiro | ✅ Implementado |
| **REQ 15** | Dashboard Financeiro | Financeiro | ✅ Implementado (ADR 016) |
| **REQ 16** | Notificar Tutor | Notificações | ✅ Implementado (ADR 017) |
| **REQ 17** | Relatórios Gerenciais | Financeiro | ✅ Implementado |

---

## 🛠️ Arquitetura e Decisões (ADRs)

O detalhamento de todas as **Decisões Arquiteturais (ADRs 007 a 017)** encontra-se documentado na pasta `docs/adr/`:
* **ADRs 007 a 013:** Estruturação FastAPI, RBAC flexível e decisões da Sprint 1.
* **ADRs 014 a 017:** Integração dos módulos Clínico, Financeiro, Notificações, exportação de relatórios/PDFs no cliente e simulação de envio de notificações.

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
   * **Documentação da API (Swagger):** `http://localhost:8000/docs`

> **Nota:** O banco de dados SQLite (`vetcare.db`) é gerado e povoado com dados de teste automaticamente na primeira execução.

---

## 🔑 Usuários de teste (Senha: `vetcare123`)

* **Administrador:** `alex@vetcare.com`
* **Recepção:** `marina@vetcare.com`
* **Veterinária:** `camila.r@vetcare.com`

---

## 🧪 Testes Automatizados

O repositório inclui **37 testes automatizados** (pytest) cobrindo todos os 6 módulos da aplicação em banco de dados isolado/temporário:

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest
```
