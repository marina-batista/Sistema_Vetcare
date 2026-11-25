# ADR 008: Permissões padrão por perfil, ajustáveis por usuário

**Status:** Aceito

**Relação com a Etapa 1:** **altera o ADR 003 (RBAC)**. Lá ficou definido que as permissões seriam "atreladas ao cargo/papel e não individualmente a cada funcionário".

**Contexto:** no protótipo da tela *Editar usuário*, o administrador escolhe o perfil e ajusta, por módulo, o que aquela pessoa pode **Visualizar**, **Criar e editar** e **Excluir**. Com o RBAC puro seria preciso criar um perfil novo para cada exceção (ex.: uma recepcionista que também acessa relatórios).

**Decisão:** manter os três perfis (Administrador, Recepcionista e Veterinário), cada um com um **conjunto padrão de permissões**. O administrador pode ajustar esse conjunto por usuário, e o ajuste fica salvo na coluna `permissoes` da tabela `usuarios`. Todas as rotas usam `requer_permissao(("módulo", "ação"))` do módulo de Autenticação. Regras de consistência:

- quem cria/edita ou exclui também visualiza;
- o administrador não pode remover a própria permissão de gerenciar usuários nem se desativar;
- trocar o perfil reaplica o padrão daquele perfil.

O padrão segue as táticas da Etapa 1: a recepção não acessa prontuários nem prescrições, e só o administrador acessa relatórios e o financeiro.

**Consequências:**

- Positivas: exceções são atendidas sem criar perfis novos. A checagem continua centralizada em um único lugar (`autenticacao/seguranca.py`), e o menu de cada pessoa mostra só o que ela pode acessar.
- Negativas: perde-se parte da simplicidade de gestão do RBAC puro, porque é preciso conferir as exceções individuais em auditorias. Mudanças de permissão valem na próxima requisição; o menu se atualiza ao abrir uma tela.
