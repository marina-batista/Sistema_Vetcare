/* ==========================================================
   ui.js — utilidades de interface reaproveitadas pelas telas
   (formatação, badges, modal de formulário, paginação, toast)
   ========================================================== */

/** Sempre use ao colocar dados do usuário dentro de innerHTML (evita XSS). */
function escapar(v) {
  return String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function toast(msg, tipo = "ok") {
  const t = document.createElement("div");
  t.className = "toast" + (tipo === "erro" ? " erro" : "");
  t.setAttribute("role", tipo === "erro" ? "alert" : "status");
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3800);
}

/* ---------- Datas ---------- */
const zero = (n) => String(n).padStart(2, "0");
function paraData(v) { return typeof v === "string" && v.length === 10 ? new Date(v + "T00:00") : new Date(v); }
function isoData(d) { return `${d.getFullYear()}-${zero(d.getMonth() + 1)}-${zero(d.getDate())}`; }
function dataBR(v) { return v ? paraData(v).toLocaleDateString("pt-BR") : "—"; }
function horaBR(v) { const d = paraData(v); return `${zero(d.getHours())}:${zero(d.getMinutes())}`; }
function mesmoDia(a, b) { return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate(); }
function somarDias(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x; }
function capitalizar(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
function dataExtenso(d = new Date()) {
  return capitalizar(d.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long", year: "numeric" }));
}
/** "Hoje, 08:12" · "Ontem, 17:40" · "02/09/2026" */
function quando(v) {
  if (!v) return "—";
  const d = paraData(v), hoje = new Date();
  if (mesmoDia(d, hoje)) return "Hoje, " + horaBR(v);
  if (mesmoDia(d, somarDias(hoje, -1))) return "Ontem, " + horaBR(v);
  return dataBR(v);
}
function idade(nascimento) {
  if (!nascimento) return "—";
  const n = paraData(nascimento), h = new Date();
  let meses = (h.getFullYear() - n.getFullYear()) * 12 + h.getMonth() - n.getMonth();
  if (h.getDate() < n.getDate()) meses--;
  if (meses >= 12) { const a = Math.floor(meses / 12); return `${a} ${a === 1 ? "ano" : "anos"}`; }
  meses = Math.max(meses, 0);
  return `${meses} ${meses === 1 ? "mês" : "meses"}`;
}
function moeda(v) { return Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }); }

/* ---------- Badges ---------- */
const STATUS_AGENDAMENTO = {
  agendado: ["Agendado", ""],
  confirmado: ["Confirmado", ""],
  aguardando: ["Aguardando", "laranja"],
  em_atendimento: ["Em atendimento", "verde"],
  concluido: ["Concluído", "verde"],
  cancelado: ["Cancelado", "vermelho"],
};
function badge(texto, cor = "") { return `<span class="badge ${cor}">${escapar(texto)}</span>`; }
function badgeStatus(status) { const [t, c] = STATUS_AGENDAMENTO[status] || [status, ""]; return badge(t, c); }
function inicial(nome) { return escapar((nome || "?").trim().charAt(0).toUpperCase()); }

/* ---------- Diversos ---------- */
function debounce(fn, ms = 300) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
function parametro(nome) { return new URLSearchParams(location.search).get(nome); }
function opcoes(lista, selecionado) {
  return lista.map(([v, t]) => `<option value="${escapar(v)}" ${String(v) === String(selecionado ?? "") ? "selected" : ""}>${escapar(t)}</option>`).join("");
}

const ICONE_OLHO = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>`;
/** Botões com data-olho="idDoInput" mostram/ocultam a senha. */
function ativarOlhoSenha(raiz = document) {
  raiz.querySelectorAll("[data-olho]").forEach((btn) => {
    btn.innerHTML = ICONE_OLHO;
    btn.setAttribute("aria-label", "Mostrar senha");
    btn.onclick = () => {
      const inp = document.getElementById(btn.dataset.olho);
      const mostrar = inp.type === "password";
      inp.type = mostrar ? "text" : "password";
      btn.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
    };
  });
}

/* ---------- Máscaras de digitação (CPF, telefone, CEP) ---------- */
const MASCARAS = {
  cpf: (v) => v.replace(/\D/g, "").slice(0, 11)
    .replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2"),
  telefone: (v) => {
    const d = v.replace(/\D/g, "").slice(0, 11);
    return d.replace(/(\d{2})(\d)/, "($1) $2").replace(d.length > 10 ? /(\d{5})(\d)/ : /(\d{4})(\d)/, "$1-$2");
  },
  cep: (v) => v.replace(/\D/g, "").slice(0, 8).replace(/(\d{5})(\d)/, "$1-$2"),
};
const PADROES = { cpf: "\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}", cep: "\\d{5}-\\d{3}" };
function aplicarMascara(input, tipo) {
  input.addEventListener("input", () => { input.value = MASCARAS[tipo](input.value); });
}

/* ---------- Paginação ("Mostrando 1–7 de 128" + Anterior/Próxima) ---------- */
function renderPaginacao(el, { pagina, tamanho, total }, aoMudar) {
  const ini = total ? (pagina - 1) * tamanho + 1 : 0;
  const fim = Math.min(pagina * tamanho, total);
  el.innerHTML = `<span>Mostrando ${ini}–${fim} de ${total}</span>
    <div class="paginacao">
      <button class="btn" data-p="${pagina - 1}" ${pagina <= 1 ? "disabled" : ""}>Anterior</button>
      <button class="btn" data-p="${pagina + 1}" ${fim >= total ? "disabled" : ""}>Próxima</button>
    </div>`;
  el.querySelectorAll("button").forEach((b) => (b.onclick = () => aoMudar(Number(b.dataset.p))));
}

/* ---------- Modal de formulário genérico (usado pelos "popups") ----------
   abrirModal({
     titulo: "Cadastrar animal", subtitulo: "...",
     campos: [{ nome, rotulo, tipo: "text|email|tel|date|time|password|number|select|textarea|checkbox",
                obrigatorio, opcoes: [[valor, texto]], placeholder, dica, largura: "inteira", attrs }],
     valores: { ... }, textoSalvar: "Salvar",
     aoSalvar: async (dados, form) => { ... }, // lance um Error para mostrar a mensagem no modal
     botoesExtras: [{ texto, classe, aoClicar: async (fechar) => {} }],
     classeSalvar: "btn-laranja" | "btn-vermelho", largura: "estreita" | "larga",
     htmlExtra: "antes dos campos", htmlDepois: "depois dos campos",
     aoAbrir: (form) => { ... }                // para campos que dependem uns dos outros
   })
   Campos aceitam também  mascara: "cpf" | "telefone" | "cep". 
*/
function campoHTML(c, valor) {
  const id = `campo_${c.nome}`;
  const v = valor ?? c.padrao ?? "";
  const req = c.obrigatorio ? "required" : "";
  let input;
  if (c.tipo === "select") {
    const vazio = c.placeholder !== undefined ? `<option value="">${escapar(c.placeholder)}</option>` : "";
    input = `<select id="${id}" name="${c.nome}" ${req} ${c.attrs || ""}>${vazio}${opcoes(c.opcoes, v)}</select>`;
  } else if (c.tipo === "textarea") {
    input = `<textarea id="${id}" name="${c.nome}" ${req} placeholder="${escapar(c.dica || "")}" ${c.attrs || ""}>${escapar(v)}</textarea>`;
  } else if (c.tipo === "checkbox") {
    return `<div class="${c.largura === "inteira" ? "inteira" : ""}"><label class="check"><input type="checkbox" id="${id}" name="${c.nome}" ${v ? "checked" : ""}> ${escapar(c.rotulo)}</label></div>`;
  } else {
    const mascara = c.mascara ? `data-mascara="${c.mascara}" inputmode="numeric" ${PADROES[c.mascara] ? `pattern="${PADROES[c.mascara]}"` : ""}` : "";
    input = `<input id="${id}" name="${c.nome}" type="${c.tipo || "text"}" value="${escapar(v)}" ${req} ${mascara}
      placeholder="${escapar(c.dica || "")}" ${c.min ? `minlength="${c.min}"` : ""} ${c.attrs || ""}>`;
  }
  return `<div class="${c.largura === "inteira" ? "inteira" : ""}"><label class="rotulo" for="${id}">${escapar(c.rotulo)}</label>${input}</div>`;
}

function abrirModal({ titulo, subtitulo = "", campos = [], valores = {}, textoSalvar = "Salvar", aoSalvar, botoesExtras = [],
  htmlExtra = "", htmlDepois = "", classeSalvar = "btn-primario", largura = "", aoAbrir }) {
  const fundo = document.createElement("div");
  fundo.className = "modal-fundo";
  const anterior = document.activeElement;
  fundo.innerHTML = `
    <form class="modal ${largura}" role="dialog" aria-modal="true" aria-labelledby="modal-titulo">
      <h2 id="modal-titulo">${escapar(titulo)}</h2>
      ${subtitulo ? `<p class="sub">${escapar(subtitulo)}</p>` : `<div style="height:20px"></div>`}
      ${htmlExtra}
      ${campos.length ? `<div class="grade-form">${campos.map((c) => campoHTML(c, valores[c.nome])).join("")}</div>` : ""}
      ${htmlDepois}
      <p class="erro-form" role="alert"></p>
      <div class="botoes-form">
        ${botoesExtras.map((b, i) => `<button type="button" class="btn ${b.classe || ""} ${i === 0 ? "esquerda" : ""}" data-extra="${i}">${escapar(b.texto)}</button>`).join("")}
        <button type="button" class="btn" data-cancelar>Cancelar</button>
        ${aoSalvar ? `<button type="submit" class="btn ${classeSalvar}">${escapar(textoSalvar)}</button>` : ""}
      </div>
    </form>`;
  document.body.appendChild(fundo);
  const form = fundo.querySelector("form");
  const erro = fundo.querySelector(".erro-form");

  const aoTeclar = (e) => { if (e.key === "Escape") fechar(); };
  function fechar() {
    fundo.remove();
    document.removeEventListener("keydown", aoTeclar);
    if (anterior && anterior.focus) anterior.focus();
  }
  document.addEventListener("keydown", aoTeclar);
  fundo.addEventListener("mousedown", (e) => { if (e.target === fundo) fechar(); });
  fundo.querySelector("[data-cancelar]").onclick = fechar;
  fundo.querySelectorAll("[data-extra]").forEach((b) => {
    b.onclick = async () => {
      erro.textContent = "";
      try { await botoesExtras[Number(b.dataset.extra)].aoClicar(fechar); } catch (err) { erro.textContent = err.message; }
    };
  });
  form.querySelectorAll("[data-mascara]").forEach((i) => aplicarMascara(i, i.dataset.mascara));
  if (aoAbrir) aoAbrir(form);
  (form.querySelector("input:not([type=checkbox]):not(:disabled), select:not(:disabled), textarea:not(:disabled)") || form.querySelector("button")).focus();

  form.onsubmit = async (e) => {
    e.preventDefault();
    if (!aoSalvar) return;
    erro.textContent = "";
    const dados = {};
    campos.forEach((c) => {
      const el = form.elements[c.nome];
      let v = c.tipo === "checkbox" ? el.checked : el.value.trim();
      if (v === "") v = null;
      if (c.tipo === "number" && v !== null) v = Number(v);
      dados[c.nome] = v;
    });
    const btn = form.querySelector("[type=submit]");
    btn.disabled = true;
    try { await aoSalvar(dados, form); fechar(); }
    catch (err) { erro.textContent = err.message; }
    finally { btn.disabled = false; }
  };
  return { fundo, form, fechar };
}

/** Janela só de leitura (ex.: ver prescrição). */
function abrirDialogo(titulo, html) {
  return abrirModal({ titulo, htmlExtra: `<div>${html}</div>` });
}
