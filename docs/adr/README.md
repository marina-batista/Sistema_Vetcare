# ADRs — Registros de Decisão de Arquitetura

Os ADRs 001 a 006 foram definidos na **Etapa 1** (documento "Projeto Clínica VetCare – Etapa 1").
A partir do ADR 007 estão as decisões da **Etapa 2 (Sprint 1)**, incluindo os desvios em relação à Etapa 1.
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
| [013](ADR-013-telas-proximas-sprints-no-navegador.md) | Telas das próximas sprints com dados no navegador | Etapa 2 | Temporário | **Desvio** temporário da Figura 2 |
