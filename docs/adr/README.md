# ADRs — Registros de Decisão de Arquitetura

Os ADRs 001 a 006 foram definidos na **Etapa 1** (documento "Projeto Clínica VetCare – Etapa 1").
Os ADRs 007 a 013 são da **Etapa 2 (Sprint 1)** e os ADRs 014 a 017 são do **Trabalho Final** (evolução do sistema).
Para registrar um novo desvio, copie `modelo.md` com o próximo número.

| Nº | Decisão | Origem | Status | Relação com a Etapa 1 |
|---|---|---|---|---|
| 001 | Top 4: Segurança, Disponibilidade, Desempenho e Usabilidade | Etapa 1 | Aceito | — |
| 002 | Estilo arquitetural Monolito Modular | Etapa 1 | Aceito | Concretizado pelo ADR 007 |
| 003 | Controle de Acesso Baseado em Papéis (RBAC) | Etapa 1 | **Alterado** | Ajustado pelo ADR 008 |
| 004 | Monitoramento e redundância para disponibilidade | Etapa 1 | **Adiado em parte** | Ver ADR 009 |
| 005 | Cache de dados e concorrência para desempenho | Etapa 1 | **Adiado** | Ver ADR 010 |
| 006 | Validações em tempo real para usabilidade | Etapa 1 | Aceito | Implementado nesta sprint |
| [007](ADR-007-monolito-modular-com-fastapi.md) | Monolito Modular implementado com FastAPI: um pacote e um conjunto de rotas por módulo | Etapa 2 | Aceito | Concretiza o 002 |
| [008](ADR-008-permissoes-ajustaveis-por-usuario.md) | Permissões padrão por perfil, ajustáveis por usuário | Etapa 2 | Aceito | **Desvio** do 003 |
| [009](ADR-009-redundancia-adiada.md) | Instância única com verificação de saúde; redundância adiada | Etapa 2 | Aceito | **Desvio** do 004 |
| [010](ADR-010-cache-adiado.md) | Sem cache nesta sprint; índices e paginação no banco | Etapa 2 | Aceito | **Desvio** do 005 |
| [011](ADR-011-validador-sem-salas.md) | Validador de Disponibilidade sem controle de salas | Etapa 2 | Aceito | **Desvio** da Figura 1 |
| [012](ADR-012-recuperacao-senha-email-simulado.md) | Recuperação de senha com envio de e-mail simulado | Etapa 2 | Aceito | — |
| [013](ADR-013-telas-proximas-sprints-no-navegador.md) | Telas das próximas sprints com dados no navegador | Etapa 2 | **Substituído** pelo 014 | **Desvio** temporário da Figura 2 |
| [014](ADR-014-modulos-clinico-financeiro-notificacoes-na-api.md) | Módulos Clínico, Financeiro e Notificações implementados na API | Final | Aceito | **Retoma a Figura 2** (substitui o 013) |
| [015](ADR-015-geracao-de-documentos-no-cliente.md) | Prescrições (PDF) e relatórios (CSV) gerados no cliente | Final | Aceito | Esclarece a Figura 1 |
| [016](ADR-016-dashboard-sem-controle-de-despesas.md) | Dashboard apenas com recebimentos (sem despesas) | Final | Aceito | Sem desvio (REQ 15) |
| [017](ADR-017-notificacoes-com-disparo-simulado.md) | Notificações com disparo simulado (sem gateway) | Final | Aceito | Esclarece a Figura 1 |
