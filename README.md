# VetCare 

Sistema de gestão para clínica veterinária — Engenharia de Software 1 (UFBA).
**Arquitetura:** Monolito Modular em camadas (Etapa 1, ADR 002), implementado com **FastAPI** + SQLite no backend e HTML/CSS/JavaScript no frontend (ADR 007).

## Requisitos da Sprint 1

O Documento de Requisitos tem **17 requisitos funcionais**. Esta sprint cobre os módulos **Autenticação**, **Cadastros** e **Agendamento**:

| Requisito | Prioridade | Módulo | Situação | Telas | Rotas da API |
|---|---|---|---|---|---|
| REQ 01 – Manter Usuário | Alta | Autenticação | ✅ Implementado | `admin/usuarios.html` (popup *Editar usuário* com permissões) | `/api/usuarios` |
| REQ 02 – Autenticar Usuário | Alta | Autenticação | ✅ Implementado | `auth/login.html` | `/api/auth/login`, `/logout`, `/me` |
| REQ 03 – Recuperar Senha | Média | Autenticação | ✅ Implementado | `auth/recuperar-senha.html` | `/api/auth/recuperar-senha`, `/redefinir-senha` |
| REQ 04 – Manter Tutor | Alta | Cadastros | ✅ Implementado | `recepcao/tutores.html` (popup *Editar tutor*) | `/api/tutores` |
| REQ 05 – Manter Animal | Alta | Cadastros | ✅ Implementado | `recepcao/animais.html` (popup *Cadastrar animal*) | `/api/animais` |
| REQ 06 – Manter Veterinário | Alta | Cadastros | ✅ Implementado | `admin/veterinarios.html` | `/api/veterinarios` |
| REQ 07 – Agendar Consulta | Alta | Agendamento | ✅ Implementado | `recepcao/agenda.html` (popup *Novo agendamento*), `recepcao/visao-geral.html` | `/api/agendamentos`, `/api/agendamentos/disponibilidade` |
| REQ 08 – Cancelar Consulta | Alta | Agendamento | ✅ Implementado | `recepcao/agenda.html` (popup *Cancelar consulta*) | `/api/agendamentos/{id}/cancelamento` |
| REQ 09 – Consultar Agenda | Alta | Agendamento | ✅ Implementado | `recepcao/agenda.html` (Dia / Semana / Profissional), `veterinario/fila.html` | `/api/agendamentos?data_inicio=&data_fim=&veterinario_id=` |
| REQ 10 – Registrar Atendimento | Alta | Clínico | 🖼️ Tela pronta, dados de exemplo | `veterinario/prontuario.html` | próxima sprint |
| REQ 11 – Manter Prontuário | Alta | Clínico | 🖼️ Tela pronta, dados de exemplo | `veterinario/prontuarios.html`, `prontuario.html` | próxima sprint |
| REQ 12 – Registrar Vacinação | Média | Clínico | 🖼️ Tela pronta, dados de exemplo | `prontuario.html?aba=vacinacao` (popup *Registrar vacina*) | próxima sprint |
| REQ 13 – Emitir Prescrição | Média | Clínico | 🖼️ Tela pronta, dados de exemplo | `veterinario/prescricoes.html` (popup *Emitir prescrição*) | próxima sprint |
| REQ 14 – Registrar Pagamento | Alta | Financeiro | 🖼️ Tela pronta, dados de exemplo | `recepcao/pagamentos.html` | próxima sprint |
| REQ 15 – Dashboard Financeiro | Média | Financeiro | 🖼️ Tela pronta, dados de exemplo | `admin/financeiro.html` | próxima sprint |
| REQ 16 – Notificar Tutor | Média | Notificações | 🖼️ Tela pronta, dados de exemplo | `recepcao/notificacoes.html` | próxima sprint |
| REQ 17 – Gerar Relatórios Gerenciais | Média | Financeiro | 🖼️ Tela pronta (parte usa a API) | `admin/relatorios.html` | próxima sprint |

**Escopo planejado da sprint (~30%):** REQ 01 a REQ 07 (7 de 17 = 41%). REQ 08 e REQ 09 foram entregues junto porque pertencem ao mesmo módulo (Agendamento) e às mesmas telas, então a cobertura real é de 9 de 17 (53%). As telas de REQ 10 a 17 já existem com dados de exemplo (ADR 013).

### Regras de negócio implementadas

- **Agendamento (Validador de Disponibilidade):** o veterinário precisa estar ativo, o horário precisa estar dentro do expediente dele e não pode haver choque com outro agendamento do mesmo veterinário ou do mesmo animal. O popup só oferece horários livres (ADR 006 e ADR 011).
- **Cancelamento:** registra o motivo e a justificativa e libera o horário.
- **Animal:** sempre vinculado a um tutor, e a data de nascimento não pode estar no futuro. Um tutor com animais não pode ser excluído.
- **Tutor:** CPF, telefone e CEP têm máscara e validação. O CEP preenche endereço, bairro e cidade pelo ViaCEP (precisa de internet).
- **Segurança:** senhas com hash PBKDF2, sessão por token e permissões por módulo (Visualizar / Criar e editar / Excluir), com padrão por perfil e ajuste por usuário (ADR 008). O backend recusa o que não é permitido (erro 403) e o frontend esconde botões e telas.

## Arquitetura (Etapa 1 → código)

| Etapa 1 (Figura 2) | Onde está no código |
|---|---|
| Camada de Apresentação — Aplicação Web | `frontend/` (uma pasta por área: `auth`, `admin`, `recepcao`, `veterinario`) |
| Camada de Negócio — módulo Autenticação | `backend/app/modulos/autenticacao/` |
| Camada de Negócio — módulo Cadastros | `backend/app/modulos/cadastros/` |
| Camada de Negócio — módulo Agendamento | `backend/app/modulos/agendamento/` (`rotas.py` = Calendário de Consultas, `disponibilidade.py` = Validador de Disponibilidade) |
| Camada de Negócio — Clínico, Financeiro, Notificações | `backend/app/modulos/clinico/`, `financeiro/`, `notificacoes/` (próxima sprint) |
| Camada de Persistência — Banco de Dados VetCare | `backend/app/core/database.py` (SQLite: `backend/vetcare.db`) |

Cada módulo tem `modelos.py` (tabelas), `esquemas.py` (validação), `servicos.py` (regras e respostas) e `rotas*.py` (rotas FastAPI). As dependências seguem a Figura 1: Agendamento usa Cadastros, e todos usam Autenticação para validar o acesso. A rota `GET /api/saude` verifica a API e o banco (ADR 009).

As decisões e os desvios em relação à Etapa 1 estão em [`docs/adr/`](docs/adr/README.md), numerados a partir do ADR 007.

## Como rodar

Precisa do **Python 3.10 ou mais novo**.

```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abra **http://localhost:8000** (telas) e **http://localhost:8000/docs** (documentação interativa da API).

O banco `backend/vetcare.db` é criado sozinho com dados de exemplo. Se o banco veio de uma versão anterior, as colunas novas são adicionadas automaticamente ao iniciar. Para recomeçar do zero, apague esse arquivo e reinicie o servidor.

### Usuários de teste (senha: `vetcare123`)

| Perfil | E-mail |
|---|---|
| Administrador | `alex@vetcare.com` |
| Recepção | `marina@vetcare.com` |
| Veterinária | `camila.r@vetcare.com` |

**Recuperar senha:** como não há servidor de e-mail, o código de 6 dígitos aparece no **terminal** onde o `uvicorn` está rodando (ADR 012).

## Testes

20 testes automatizados (login, permissões, cadastros, validador de horários, cancelamento e agenda), rodando num banco temporário. Dentro de `backend`, com o ambiente ativado:

```
pip install -r requirements-dev.txt && python -m pytest
```

## Estrutura de pastas

```
vetcare/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py               # cria o app, registra as rotas de cada módulo e serve o frontend
│       ├── seed.py               # dados de exemplo
│       ├── core/                 # Camada de Persistência + tipos comuns
│       │   ├── database.py
│       │   └── comum.py
│       └── modulos/              # Camada de Negócio (um pacote por módulo da Etapa 1)
│           ├── autenticacao/     # REQ 01–03: modelos, esquemas, seguranca, servicos, rotas_auth, rotas_usuarios
│           ├── cadastros/        # REQ 04–06: modelos, esquemas, servicos, rotas_tutores, rotas_animais, rotas_veterinarios
│           ├── agendamento/      # REQ 07–09: modelos, esquemas, servicos, disponibilidade, rotas
│           ├── clinico/          # REQ 10–13 (próxima sprint)
│           ├── financeiro/       # REQ 14, 15, 17 (próxima sprint)
│           └── notificacoes/     # REQ 16 (próxima sprint)
├── frontend/
│   ├── css/style.css         # visual do Figma + tokens do guia de estilo (cores, tipografia, medidas)
│   ├── assets/               # logo.svg, simbolo.svg (favicon) e padrao-login.svg (oficiais)
│   ├── js/
│   │   ├── api.js            # chamadas ao backend + sessão
│   │   ├── ui.js             # modal, paginação, datas, badges
│   │   ├── layout.js         # menu lateral (perfil + permissões)
│   │   ├── prescricao.js     # popup "Emitir prescrição" + PDF
│   │   └── mock.js           # dados de exemplo das telas fora da sprint
│   ├── auth/                 # login, recuperar senha
│   ├── admin/                # usuários, veterinários, financeiro, relatórios
│   ├── recepcao/             # visão geral, agenda, tutores, animais, pagamentos, notificações
│   └── veterinario/          # fila do dia, prontuários, prontuário/vacinação, prescrições
└── docs/
    ├── adr/                  # ADR 007 em diante (001–006 estão no documento da Etapa 1)
    └── design/guia_de_estilo.svg
```

## Guia de estilo

`frontend/css/style.css` começa com os tokens do `docs/design/guia_de_estilo.svg`. Use sempre as variáveis, nunca a cor direta:

| Token | Cor | Uso |
|---|---|---|
| `--primary-light` | #72D6CD | fundos suaves, destaques (ex.: avatar) |
| `--primary-default` | #299994 | ícones, gráficos, foco — **não usar em texto pequeno** (3,3 : 1) |
| `--primary-dark` | #1E6767 | títulos e botão primário |
| `--light-bg` | #F7FAFA | fundo das páginas |
| `--gray-text` | #495555 | texto corrido |
| `--cta-button` | #EC830F | botão CTA (`.btn-laranja`), com texto em `--ink` — **uma CTA por tela** |
| `--ink` | #1B2E2E | texto sobre o laranja |

Também seguem o guia: fonte Nunito (alternativa Trebuchet MS), body 16 / linha 1,6, títulos 48-40-24-20 em Bold (ExtraBold só no logo), raios 12 (campos), 20 (cards), 24 (blocos) e 999 (botões), sombra `0 8px 24px rgba(30,103,103,.12)`, espaçamentos 4-8-16-24-32-48-64 e **alvos de toque de no mínimo 44px** (inclusive checkboxes, links "Editar" e blocos da agenda).

## Como a tela conversa com a API

Cada tela é um `.html` que inclui `api.js`, `ui.js` e `layout.js`. Exemplo (tela de Tutores):

```js
const usuario = exigirLogin("tutores_animais");                     // protege a página (módulo de permissão)
montarLayout(usuario, "tutores");                                   // monta o menu

const r = await api("/tutores", { query: { q: "ana", pagina: 1 } }); // GET /api/tutores?q=ana
await api("/tutores", { method: "POST", body: { nome, telefone } }); // POST /api/tutores
```

`api()` envia o token de login automaticamente e transforma os erros do FastAPI em mensagens legíveis.
Para esconder um botão sem permissão: `$("btnNovo").hidden = !pode("tutores_animais", "editar");`

### Para adicionar um novo popup

Use `abrirModal()` (em `ui.js`); todos os popups do sistema usam essa função. Ela também aceita `mascara: "cpf" | "telefone" | "cep"` nos campos, `classeSalvar` (botão laranja/vermelho), `largura: "estreita" | "larga"` e `aoAbrir(form)` para campos que dependem uns dos outros (veja o *Novo agendamento* em `agenda.html`):

```js
abrirModal({
  titulo: "Cadastrar animal",
  subtitulo: "Todo animal precisa estar vinculado a um tutor.",
  campos: [
    { nome: "nome", rotulo: "Nome do animal", obrigatorio: true },
    { nome: "especie", rotulo: "Espécie", tipo: "select", opcoes: [["Cão", "Cão"], ["Gato", "Gato"]] },
  ],
  textoSalvar: "Salvar animal",
  aoSalvar: async (dados) => { await api("/animais", { method: "POST", body: dados }); },
});
```

### Para implementar um módulo da próxima sprint (ex.: Clínico)

1. Dentro de `backend/app/modulos/clinico/`, crie `modelos.py`, `esquemas.py` e `rotas.py`, usando `modulos/cadastros/` como base.
2. Proteja as rotas com `requer_permissao(("prontuario", "ver"))` (ou `"editar"` / `"excluir"`) de `modulos/autenticacao/seguranca.py`.
3. Importe o módulo em `main.py` e acrescente-o ao dicionário `MODULOS`.
4. Na tela, troque o uso de `MOCK.<algo>` / `Local.ler(...)` por `await api("/<rota>")` e remova o aviso laranja (ADR 013).

## Publicar no GitHub

**Opção A — pelo site (sem instalar nada):**
1. Entre em https://github.com, clique em **New repository**, dê o nome `vetcare`, marque **Public** e crie.
2. Na página do repositório vazio, clique em **uploading an existing file**.
3. Arraste **o conteúdo** da pasta `vetcare` (as pastas `backend`, `frontend`, `docs` e os arquivos `README.md` e `.gitignore`). Não envie `.venv` nem `vetcare.db`.
4. Clique em **Commit changes**.

**Opção B — pelo terminal (com o Git instalado):**
```bash
cd vetcare
git init
git add .
git commit -m "Sprint 1: módulos Autenticação, Cadastros e Agendamento"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/vetcare.git
git push -u origin main
```

Cada colega pode depois clonar (`git clone ...`), criar uma branch para a sua tela (`git checkout -b tela-pagamentos`) e abrir um *Pull Request*.
