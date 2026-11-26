# ADR 015: Geração de prescrições (PDF) e relatórios (CSV) no cliente

**Status:** Aceito

**Relação com a Etapa 1:** **esclarecimento da Figura 1** — a Figura 1 não previa um componente de geração de documentos; esta decisão registra onde essa responsabilidade ficou.

**Contexto:** o REQ 13 (Emitir Prescrição) e o REQ 17 (Relatórios Gerenciais) precisam entregar documentos ao usuário (prescrição em PDF, relatórios exportáveis). Um serviço de geração de documentos no servidor (render de PDF, planilhas) acrescentaria dependências e infraestrutura sem necessidade nesta fase.

**Decisão:** o backend guarda e devolve os **dados** (a prescrição e os números dos relatórios); a **formatação do documento** acontece no navegador — a prescrição é aberta numa janela de impressão (o usuário escolhe "Salvar como PDF") e os relatórios são exportados em CSV/impressão a partir da pré-visualização. Nenhum arquivo é armazenado no servidor.

**Consequências:**

- Positivas: sem dependências de bibliotecas de PDF no servidor; o documento sai com os dados reais da API.
- Positivas: a prescrição fica registrada no banco (REQ 13) mesmo que o PDF seja gerado no cliente.
- Negativas: a aparência do PDF depende do navegador; não há um arquivo versionado guardado pela clínica. Um serviço de documentos pode ser adicionado depois sem mudar as rotas da API.
