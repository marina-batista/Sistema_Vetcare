# ADR 017: Notificações com disparo simulado (sem gateway de WhatsApp/e-mail)

**Status:** Aceito (continua a linha do ADR 012)

**Relação com a Etapa 1:** **esclarecimento** — a Figura 1 previa o módulo de Notificações; esta decisão registra até onde ele vai nesta entrega.

**Contexto:** o REQ 16 (Notificar Tutor) pede o envio de avisos sobre consultas e vacinas. A integração real com um provedor de WhatsApp ou de e-mail exige contas, credenciais e custo, e não é necessária para demonstrar a regra de negócio.

**Decisão:** o backend calcula as notificações pendentes a partir dos dados reais — consultas dos próximos 7 dias (agendadas/confirmadas) e vacinas que vencem nos próximos 30 dias — e registra o **envio** numa tabela (`notificacoes`), evitando duplicatas por uma referência. O disparo real (WhatsApp/e-mail) é **simulado**: marcar como "enviada" grava o histórico, mas nenhuma mensagem sai de fato. A configuração de disparo automático também é persistida.

**Consequências:**

- Positivas: a regra de negócio (quem notificar, quando e por qual canal) fica implementada e testável, com histórico real no banco.
- Positivas: trocar a simulação por um provedor real significa implementar uma única função de envio, sem mudar as rotas nem as telas.
- Negativas: nesta entrega nenhuma mensagem chega ao tutor; o "canal" (WhatsApp/E-mail) é apenas informativo, escolhido pelo e-mail do tutor.
