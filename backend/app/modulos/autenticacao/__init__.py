"""Módulo de Autenticação — REQ 01 (Manter Usuário), 02 (Autenticar Usuário) e 03 (Recuperar Senha).

Também concentra o controle de acesso (ADR 003, ajustado pelo ADR 008): todas as rotas dos outros
módulos usam `requer_permissao(...)` daqui para validar o acesso.
"""
