# ADR 014: Módulos Clínico, Financeiro e Notificações implementados na API

**Status:** Aceito (substitui o ADR 013)

**Relação com a Etapa 1:** **retoma a Figura 2** — os dados dessas telas voltam a passar pela Camada de Negócio e pela de Persistência, como previsto na arquitetura original.

**Contexto:** na Sprint 1 (ADR 013), as telas de prontuário, vacinação, prescrição, pagamento, dashboard, relatórios e notificações usavam dados de exemplo (`frontend/js/mock.js`) e `localStorage`, por estarem fora do escopo daquela entrega. O trabalho final exige pelo menos 80% dos requisitos implementados, então esses módulos foram concluídos.

**Decisão:** foram criados os módulos **Clínico** (REQ 10, 11, 12, 13), **Financeiro** (REQ 14, 15, 17) e **Notificações** (REQ 16) seguindo o mesmo padrão dos módulos existentes — um pacote por módulo, com `modelos.py`, `esquemas.py`, `servicos.py` e `rotas_*.py` (ADR 007). O arquivo `mock.js` foi removido e todas as telas passaram a consumir a API real, com o controle de acesso por perfil/permissão aplicado no backend (ADR 008).

**Consequências:**

- Positivas: os 17 requisitos funcionais ficam implementados e persistidos no banco; os dados são compartilhados entre computadores e protegidos pelo controle de acesso.
- Positivas: a arquitetura de Monolito Modular da Etapa 1 fica completa (6 módulos).
- Negativas: o modelo de dados cresceu (atendimentos, prescrições, vacinas, pagamentos, notificações), aumentando a superfície de testes.
