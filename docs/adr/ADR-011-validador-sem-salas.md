# ADR 011: Validador de Disponibilidade sem controle de salas

**Status:** Aceito

**Relação com a Etapa 1:** **altera o componente Validador de Disponibilidade** (Figura 1), descrito como lógica que "impede choques de horário entre veterinários e salas".

**Contexto:** nenhum requisito do Documento de Requisitos menciona salas ou consultórios. O REQ 07 relaciona apenas animal, tutor, veterinário, data e horário.

**Decisão:** o validador (`modulos/agendamento/disponibilidade.py`) confere:

- se o veterinário está ativo;
- se o horário está dentro do expediente cadastrado para aquele dia da semana;
- se o horário não se sobrepõe a outro agendamento do **mesmo veterinário** ou do **mesmo animal**.

Ele também calcula os horários livres oferecidos no popup *Novo agendamento*. Salas não foram modeladas.

**Consequências:**

- Positivas: o escopo segue o documento de requisitos, e o modelo de dados fica mais simples.
- Negativas: se a clínica passar a ter consultórios compartilhados, será preciso criar a entidade Sala e incluí-la na checagem de conflito.
