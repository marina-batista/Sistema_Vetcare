# ADR 009: Instância única com verificação de saúde; redundância adiada

**Status:** Aceito

**Relação com a Etapa 1:** **adia parte do ADR 004** (monitoramento com redundância e failover).

**Contexto:** o ADR 004 prevê instâncias secundárias e failover para os módulos Clínico e de Agendamento. Nesta sprint o sistema roda na máquina de cada integrante para desenvolvimento e demonstração. Ainda não há ambiente de hospedagem, e o banco é SQLite, um arquivo local (ADR 007).

**Decisão:** executar uma única instância e criar desde já a rota **`GET /api/saude`**, que verifica a API e a conexão com o banco. Ela serve de base para o monitoramento externo previsto no ADR 004. A redundância e o failover ficam para quando houver implantação real, junto com a migração para um banco servidor.

**Consequências:**

- Positivas: menos custo e complexidade agora, e o ponto de monitoramento já fica pronto.
- Negativas: enquanto houver uma única instância, uma falha deixa o sistema indisponível até ser reiniciado.
