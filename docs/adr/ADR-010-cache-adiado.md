# ADR 010: Sem cache nesta sprint; índices e paginação no banco

**Status:** Aceito

**Relação com a Etapa 1:** **adia o ADR 005** (cache de dados e concorrência).

**Contexto:** o ADR 005 prevê cache em memória da agenda do dia e da lista de veterinários. Com o volume de uma clínica (centenas de tutores e animais, dezenas de consultas por dia), as consultas ao banco já respondem bem abaixo de um segundo. Um cache agora traria o risco de dados desatualizados, que o próprio ADR 005 aponta, sem ganho perceptível.

**Decisão:** não usar cache nesta sprint. O desempenho vem de índices nas colunas mais buscadas (nome de tutor e animal, e-mail, data/hora do agendamento), de **paginação** nas listagens (`?pagina=&tamanho=`) e de consultas filtradas por período e veterinário. O cache volta a ser avaliado se as medições passarem do tempo-alvo.

**Consequências:**

- Positivas: sem risco de inconsistência entre cache e banco, e menos código.
- Negativas: com um volume muito maior, a agenda do dia pode ficar mais lenta e exigir o cache previsto no ADR 005.
