"""Camada de Negócio do Monolito Modular (Etapa 1 — ADR 002, Figura 2).

Cada pasta é um módulo encapsulado, com modelos, esquemas, regras e rotas FastAPI próprias:

    autenticacao  — REQ 01, 02, 03 (usuários, login, recuperação de senha, permissões)
    cadastros     — REQ 04, 05, 06 (tutores, animais e veterinários)
    agendamento   — REQ 07, 08, 09 (Calendário de Consultas + Validador de Disponibilidade)
    clinico       — REQ 10 a 13 (próxima sprint)
    financeiro    — REQ 14, 15, 17 (próxima sprint)
    notificacoes  — REQ 16 (próxima sprint)

Dependências permitidas (seguem as setas da Figura 1):
    agendamento -> cadastros -> autenticacao (validação de acesso)
"""
