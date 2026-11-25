# ADR 013: Telas das próximas sprints com dados no navegador (temporário)

**Status:** Temporário, a ser substituído quando os módulos Clínico, Financeiro e de Notificações forem implementados

**Relação com a Etapa 1:** **desvio temporário da Figura 2**: nessas telas os dados não passam pela Camada de Negócio nem pela de Persistência.

**Contexto:** todas as telas do protótipo foram codificadas, mas a Sprint 1 cobre só os módulos de Autenticação, Cadastros e Agendamento. As telas de prontuário, vacinação, prescrição, pagamento, notificações, dashboard financeiro e faturamento precisavam funcionar para a demonstração e para validar a navegação.

**Decisão:** essas telas usam dados de exemplo (`frontend/js/mock.js`) e salvam o que o usuário registra no `localStorage` do navegador. Cada uma mostra um aviso laranja de "dados de exemplo". Sempre que possível, já consomem a API real: a fila do dia, os lembretes de consulta, a lista de atendimentos para pagamento e o relatório de atendimentos usam os agendamentos verdadeiros.

**Consequências:**

- Positivas: a navegação completa pode ser apresentada e testada com usuários.
- Negativas: esses dados não são compartilhados entre computadores nem protegidos pelo controle de acesso do backend. Na próxima sprint, cada `MOCK.*` / `Local.ler(...)` deve ser trocado por chamadas à API do módulo correspondente.
