# ADR 012: Recuperação de senha com envio de e-mail simulado

**Status:** Aceito

**Relação com a Etapa 1:** nenhuma (decisão de implementação do REQ 03).

**Contexto:** o REQ 03 pede que o usuário possa recuperar a senha. O protótipo envia um código por e-mail, mas o projeto não tem servidor de e-mail configurado.

**Decisão:** gerar um código de 6 dígitos, válido por 15 minutos e de uso único, salvo na tabela `codigos_recuperacao`. A função `enviar_codigo_por_email()` imprime o código no terminal do servidor. A resposta da API é a mesma exista ou não o e-mail, para não revelar quais contas existem (Segurança). Redefinir a senha encerra as sessões antigas do usuário.

**Consequências:**

- Positivas: o fluxo completo pode ser demonstrado e testado.
- Negativas: em produção é preciso trocar o corpo de `enviar_codigo_por_email()` por um envio real (SMTP ou serviço de e-mail).
