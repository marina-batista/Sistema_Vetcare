# ADR 016: Dashboard financeiro apenas com recebimentos (sem controle de despesas)

**Status:** Aceito

**Relação com a Etapa 1:** **sem desvio** — o Documento de Requisitos (REQ 15) pede "valores recebidos e quantidade de atendimentos"; não há requisito de despesas.

**Contexto:** o protótipo do dashboard (Figma) mostrava "Saídas" e "Saldo", mas nenhum requisito funcional prevê o registro de despesas da clínica. Implementar um módulo de contas a pagar estaria fora do escopo dos 17 requisitos.

**Decisão:** o REQ 14 registra apenas **recebimentos**. O dashboard (REQ 15) apresenta: **Recebido**, **A receber** (consultas concluídas ainda sem pagamento, estimadas por uma tabela de preços de referência), **Ticket médio** e **Atendimentos** no período, além de gráficos de recebimentos e de atendimentos por semana e da distribuição por forma de pagamento. Os campos "Saídas" e "Saldo" do protótipo foram removidos.

**Consequências:**

- Positivas: o dashboard mostra só números que o sistema realmente tem, sem dados inventados.
- Positivas: a "tabela de preços de referência" (`financeiro/servicos.py`) centraliza os valores e também sugere o valor no recebimento.
- Negativas: não há visão de lucro/saldo. Um módulo de despesas pode ser acrescentado como um novo pacote sem alterar os módulos existentes (manutenibilidade — Figura 2).
