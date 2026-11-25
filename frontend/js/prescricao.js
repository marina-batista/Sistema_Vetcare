/* ==========================================================
   prescricao.js — popup "Emitir prescrição" + geração do PDF
   Usado em veterinario/prontuario.html e veterinario/prescricoes.html
   (fora da Sprint 1: as prescrições ficam salvas no navegador)
   ========================================================== */

/** Prescrições antigas guardavam só o nome do medicamento (texto); converte para objeto. */
function normalizarMedicamento(m) {
  return typeof m === "string" ? { nome: m, dosagem: "", frequencia: "", instrucoes: "" } : m;
}

function todasPrescricoes() {
  return [...Local.ler("prescricoes", []), ...MOCK.prescricoes]
    .map((p) => ({ ...p, medicamentos: p.medicamentos.map(normalizarMedicamento) }))
    .sort((a, b) => b.data.localeCompare(a.data));
}

function htmlPrescricao(p) {
  return `<p><strong>Data:</strong> ${dataBR(p.data)} · <strong>Veterinário(a):</strong> ${escapar(p.vet)}</p>
    <p><strong>Animal:</strong> ${escapar(p.animal)} · <strong>Tutor(a):</strong> ${escapar(p.tutor)}</p>
    <table class="tabela" style="margin:12px 0">
      <thead><tr><th>Medicamento</th><th>Dosagem</th><th>Frequência e duração</th><th>Instruções</th></tr></thead>
      <tbody>${p.medicamentos.map((m) => `<tr><td>${escapar(m.nome)}</td><td>${escapar(m.dosagem || "—")}</td><td>${escapar(m.frequencia || "—")}</td><td>${escapar(m.instrucoes || "—")}</td></tr>`).join("")}</tbody>
    </table>
    <p><strong>Observações gerais:</strong> ${escapar(p.observacoes || p.orientacoes || "—")}</p>`;
}

/** Abre a prescrição numa janela de impressão — no diálogo, escolha "Salvar como PDF". */
function imprimirPrescricao(p) {
  const w = window.open("", "_blank");
  if (!w) return toast("Permita pop-ups neste site para gerar o PDF.", "erro");
  w.document.write(`<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>Prescrição · ${escapar(p.animal)}</title>
    <style>body{font-family:Arial,sans-serif;max-width:760px;margin:40px auto;color:#1b2e2e}h1{color:#1e6767}
    table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px;border-bottom:1px solid #ccc}</style></head>
    <body><h1>VetCare · Prescrição veterinária</h1>${htmlPrescricao(p)}
    <p style="margin-top:70px">______________________________<br>${escapar(p.vet)}</p></body></html>`);
  w.document.close();
  w.focus();
  w.print();
}

function linhaMedicamentoHTML(i) {
  const c = (nome, rotulo, dica) => `<input name="${nome}" aria-label="${rotulo} ${i + 1}" placeholder="${dica}">`;
  return c("med_nome", "Medicamento", "Ex.: Anti-inflamatório oral") + c("med_dosagem", "Dosagem", "Ex.: 1 comprimido")
    + c("med_frequencia", "Frequência e duração", "Ex.: 1× ao dia por 3 dias") + c("med_instrucoes", "Instruções", "Ex.: após a refeição");
}

/**
 * Popup "Emitir prescrição".
 *   animal:  objeto do animal (vindo da API) — o subtítulo mostra animal, tutor e data
 *   animais: lista para escolher, quando o popup é aberto sem um animal definido
 */
function abrirPrescricao({ animal = null, animais = [], usuario, aoEmitir }) {
  const hoje = isoData(new Date());
  const escolherAnimal = !animal
    ? `<div class="campo"><label class="rotulo" for="presc_animal">Animal</label>
         <select id="presc_animal" name="presc_animal" required><option value="">Selecione</option>${opcoes(animais.map((a) => [a.id, `${a.nome} — ${a.tutor_nome}`]))}</select></div>`
    : "";

  abrirModal({
    titulo: "Emitir prescrição",
    subtitulo: animal ? `${animal.nome} · Tutor(a) ${animal.tutor_nome} · ${dataBR(hoje)}` : `Selecione o animal · ${dataBR(hoje)}`,
    largura: "larga",
    htmlExtra: `${escolherAnimal}
      <div class="linhas-med" id="linhasMed">
        <span class="rotulo" aria-hidden="true">Medicamento</span><span class="rotulo" aria-hidden="true">Dosagem</span>
        <span class="rotulo" aria-hidden="true">Frequência e duração</span><span class="rotulo" aria-hidden="true">Instruções</span>
        ${linhaMedicamentoHTML(0)}
      </div>
      <button type="button" class="link-acao link-adicionar" id="btnAddMed">+ Adicionar medicamento</button>`,
    campos: [{ nome: "observacoes", rotulo: "Observações gerais", tipo: "textarea", largura: "inteira" }],
    textoSalvar: "Gerar prescrição (PDF)",
    aoAbrir: (form) => {
      let linhas = 1;
      form.querySelector("#btnAddMed").onclick = () => {
        form.querySelector("#linhasMed").insertAdjacentHTML("beforeend", linhaMedicamentoHTML(linhas));
        form.querySelectorAll("[name=med_nome]")[linhas++].focus();
      };
    },
    aoSalvar: async (dados, form) => {
      const val = (n) => [...form.querySelectorAll(`[name=${n}]`)].map((i) => i.value.trim());
      const [nomes, dosagens, freqs, instrucoes] = ["med_nome", "med_dosagem", "med_frequencia", "med_instrucoes"].map(val);
      const medicamentos = nomes.map((nome, i) => ({ nome, dosagem: dosagens[i], frequencia: freqs[i], instrucoes: instrucoes[i] }))
        .filter((m) => m.nome);
      if (!medicamentos.length) throw new Error("Informe ao menos um medicamento.");
      const a = animal || animais.find((x) => x.id === Number(form.elements.presc_animal.value));
      const prescricao = {
        id: "p" + Date.now(), data: hoje, animal_id: a.id, animal: a.nome, tutor: a.tutor_nome,
        medicamentos, observacoes: dados.observacoes || "", vet: usuario.nome,
      };
      const lista = Local.ler("prescricoes", []);
      lista.push(prescricao);
      Local.gravar("prescricoes", lista);
      imprimirPrescricao(prescricao);
      toast("Prescrição emitida.");
      if (aoEmitir) aoEmitir(prescricao);
    },
  });
}
