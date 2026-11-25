/* ==========================================================
   api.js — comunicação com o backend FastAPI + sessão do usuário
   Toda tela inclui este arquivo. Exemplo de uso:
     const tutores = await api("/tutores", { query: { q: "ana" } });
     await api("/tutores", { method: "POST", body: { nome, telefone } });
   ========================================================== */
const API_BASE = "/api"; // mesmo servidor do FastAPI (ver backend/app/main.py)
const CHAVE_TOKEN = "vetcare_token";
const CHAVE_USUARIO = "vetcare_usuario";

function getToken() {
  return localStorage.getItem(CHAVE_TOKEN) || sessionStorage.getItem(CHAVE_TOKEN);
}

function usuarioLogado() {
  const bruto = localStorage.getItem(CHAVE_USUARIO) || sessionStorage.getItem(CHAVE_USUARIO);
  try { return bruto ? JSON.parse(bruto) : null; } catch { return null; }
}

/** "Manter conectado" = localStorage (sobrevive ao fechar o navegador); senão sessionStorage. */
function salvarSessao(token, usuario, manterConectado) {
  limparSessao();
  const armazenamento = manterConectado ? localStorage : sessionStorage;
  armazenamento.setItem(CHAVE_TOKEN, token);
  armazenamento.setItem(CHAVE_USUARIO, JSON.stringify(usuario));
}

function limparSessao() {
  [localStorage, sessionStorage].forEach((s) => { s.removeItem(CHAVE_TOKEN); s.removeItem(CHAVE_USUARIO); });
}

/** Atualiza os dados do usuário guardados (ex.: permissões alteradas pelo administrador). */
function atualizarUsuarioSalvo(usuario) {
  const armazenamento = localStorage.getItem(CHAVE_TOKEN) ? localStorage : sessionStorage;
  armazenamento.setItem(CHAVE_USUARIO, JSON.stringify(usuario));
}

/** pode("tutores_animais", "excluir") → true/false, conforme as permissões do usuário logado.
    Módulos: tutores_animais, agenda, prontuario, pagamentos, relatorios, usuarios
    Ações: ver, editar, excluir. (O backend confere de novo — isto só esconde botões.) */
function pode(modulo, acao = "ver", usuario = usuarioLogado()) {
  return !!(usuario && usuario.permissoes && usuario.permissoes[modulo] && usuario.permissoes[modulo][acao]);
}

/** Primeira tela do menu que o usuário pode abrir (definida em layout.js). */
function paginaInicial(usuario) {
  const itens = typeof itensMenu === "function" ? itensMenu(usuario) : [];
  return itens.length ? itens[0][2] : "/auth/login.html";
}

let MODULO_DA_PAGINA = null;
/** Coloque no topo de cada tela protegida, informando o módulo dela.
    Redireciona se não estiver logado ou se não tiver permissão de visualizar o módulo. */
function exigirLogin(modulo) {
  const usuario = usuarioLogado();
  if (!usuario || !getToken()) {
    location.replace("/auth/login.html");
    throw new Error("Não autenticado");
  }
  MODULO_DA_PAGINA = modulo;
  if (modulo && !pode(modulo, "ver", usuario)) {
    location.replace(paginaInicial(usuario));
    throw new Error("Sem permissão");
  }
  return usuario;
}

/** Converte o "detail" de erro do FastAPI numa mensagem legível. */
function mensagemDeErro(detalhe) {
  if (typeof detalhe === "string") return detalhe;
  if (Array.isArray(detalhe)) {
    return detalhe.map((e) => {
      const campo = e.loc ? e.loc[e.loc.length - 1] : "";
      const msg = String(e.msg || "").replace(/^Value error, /, "");
      return campo && !msg.includes(" ") ? `${campo}: ${msg}` : msg;
    }).join(" · ");
  }
  return "Não foi possível concluir a operação.";
}

async function api(caminho, { method = "GET", body, query } = {}) {
  const url = new URL(API_BASE + caminho, location.origin);
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
    });
  }
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let resp;
  try {
    resp = await fetch(url, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch {
    throw new Error("Sem conexão com o servidor. O backend está rodando?");
  }

  const rotaPublica = caminho.startsWith("/auth/login") || caminho.startsWith("/auth/recuperar") || caminho.startsWith("/auth/redefinir");
  if (resp.status === 401 && !rotaPublica) {
    limparSessao();
    location.replace("/auth/login.html");
    throw new Error("Sessão expirada");
  }
  if (resp.status === 204) return null;

  const dados = await resp.json().catch(() => null);
  if (!resp.ok) throw new Error(mensagemDeErro(dados && dados.detail));
  return dados;
}
