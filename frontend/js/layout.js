/* ==========================================================
   layout.js — menu lateral de acordo com o perfil e as permissões
   Uso em cada tela:  montarLayout(usuario, "tutores");
   ========================================================== */

// [chave, texto, link, módulo de permissão]
const TELAS = [
  ["usuarios", "Usuários e acessos", "/admin/usuarios.html", "usuarios"],
  ["veterinarios", "Veterinários", "/admin/veterinarios.html", "usuarios"],
  ["financeiro", "Financeiro", "/admin/financeiro.html", "relatorios"],
  ["relatorios", "Relatórios", "/admin/relatorios.html", "relatorios"],
  ["visao-geral", "Visão geral", "/recepcao/visao-geral.html", "agenda"],
  ["agenda", "Agenda", "/recepcao/agenda.html", "agenda"],
  ["tutores", "Tutores", "/recepcao/tutores.html", "tutores_animais"],
  ["animais", "Animais", "/recepcao/animais.html", "tutores_animais"],
  ["pagamentos", "Pagamentos", "/recepcao/pagamentos.html", "pagamentos"],
  ["notificacoes", "Notificações", "/recepcao/notificacoes.html", "agenda"],
  ["fila", "Fila do dia", "/veterinario/fila.html", "prontuario"],
  ["prontuarios", "Prontuários", "/veterinario/prontuarios.html", "prontuario"],
  ["prescricoes", "Prescrições", "/veterinario/prescricoes.html", "prontuario"],
  ["vacinacao", "Vacinação", "/veterinario/prontuarios.html?aba=vacinacao", "prontuario"],
];
// Menu de cada perfil (igual ao Figma)
const MENU_DO_PERFIL = {
  administrador: ["usuarios", "veterinarios", "financeiro", "relatorios"],
  recepcionista: ["visao-geral", "agenda", "tutores", "animais", "pagamentos", "notificacoes"],
  veterinario: ["fila", "prontuarios", "prescricoes", "vacinacao"],
};
const ROTULO_PERFIL = { administrador: "Administrador", recepcionista: "Recepção", veterinario: "Veterinária(o)" };

/** Itens do menu: os do perfil que o usuário pode ver + telas de módulos liberados além do padrão. */
function itensMenu(usuario) {
  const doPerfil = MENU_DO_PERFIL[usuario.perfil] || [];
  const extras = usuario.modulos_extras || [];
  return TELAS.filter(([chave, , , modulo]) =>
    pode(modulo, "ver", usuario) && (doPerfil.includes(chave) || extras.includes(modulo)));
}

function desenharMenu(usuario, ativo) {
  const aside = document.getElementById("sidebar");
  aside.innerHTML = `
    <a class="logo" href="${paginaInicial(usuario)}">
      <img src="/assets/logo.svg" alt="VetCare — página inicial">
    </a>
    <nav class="nav" aria-label="Menu principal">
      ${itensMenu(usuario).map(([chave, texto, href]) => `<a href="${href}" class="${chave === ativo ? "ativo" : ""}" ${chave === ativo ? 'aria-current="page"' : ""}>${texto}</a>`).join("")}
    </nav>
    <div class="usuario-box">
      <div class="avatar" aria-hidden="true">${inicial(usuario.nome)}</div>
      <div>
        <strong>${escapar(usuario.nome)}</strong>
        <small>${ROTULO_PERFIL[usuario.perfil] || ""}</small>
        <button class="sair" id="btnSair" type="button">Sair</button>
      </div>
    </div>`;
  document.getElementById("btnSair").onclick = async () => {
    try { await api("/auth/logout", { method: "POST" }); } catch { /* ignora */ }
    limparSessao();
    location.href = "/auth/login.html";
  };
}

function montarLayout(usuario, ativo) {
  desenharMenu(usuario, ativo);
  // Busca as permissões atualizadas (o administrador pode ter mudado algo)
  api("/auth/me").then((atual) => {
    if (JSON.stringify(atual) === JSON.stringify(usuarioLogado())) return;
    atualizarUsuarioSalvo(atual);
    if (MODULO_DA_PAGINA && !pode(MODULO_DA_PAGINA, "ver", atual)) return location.replace(paginaInicial(atual));
    desenharMenu(atual, ativo);
  }).catch(() => {});
}
