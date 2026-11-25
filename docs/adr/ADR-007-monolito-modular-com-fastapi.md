# ADR 007: Implementação do Monolito Modular com FastAPI (rotas por módulo)

**Status:** Aceito

**Relação com a Etapa 1:** concretiza o ADR 002 (Monolito Modular) e o Diagrama de Módulos (Figura 2). A Etapa 1 não definia tecnologias.

**Contexto:** a Etapa 1 definiu um monolito modular em três camadas (Apresentação, Negócio e Persistência), com os módulos Autenticação, Cadastros, Agendamento, Clínico, Financeiro e Notificações "em pacotes independentes". Na Etapa 2 foi preciso escolher como transformar essa divisão em código.

**Decisão:**

- **Camada de Negócio:** Python com **FastAPI**. Cada módulo é um pacote em `backend/app/modulos/<módulo>/` com seus próprios `modelos.py` (tabelas), `esquemas.py` (validação), regras e `rotas*.py` (**APIRouter do FastAPI**). O `main.py` só registra as rotas de cada módulo. As dependências seguem as setas da Figura 1 (Agendamento → Cadastros → Autenticação).
- Os componentes internos do Módulo de Agendamento da Figura 1 viraram arquivos separados: `rotas.py` (Calendário de Consultas) e `disponibilidade.py` (Validador de Disponibilidade).
- **Camada de Persistência:** SQLite com SQLAlchemy (`backend/app/core/database.py`), num único banco compartilhado pelos módulos.
- **Camada de Apresentação:** aplicação web em HTML, CSS e JavaScript (`frontend/`), que consome a API REST em `/api`. O próprio processo FastAPI entrega esses arquivos, então o sistema sobe com um único comando.
- Os módulos Clínico, Financeiro e Notificações já existem como pacotes vazios, documentados para a próxima sprint.

**Consequências:**

- Positivas: a estrutura de pastas corresponde ao diagrama de módulos. Um módulo novo é só mais um pacote com seu `APIRouter`, sem mexer nos existentes (manutenibilidade). A documentação da API é gerada automaticamente em `/docs`. Não há CORS nem um segundo servidor.
- Negativas: SQLite atende bem uma clínica pequena e o ambiente acadêmico, mas para várias instâncias (ADR 004) será preciso migrar para um banco servidor (ex.: PostgreSQL). Basta trocar a URL em `core/database.py`. O frontend sem framework tem menos reaproveitamento de componentes.
