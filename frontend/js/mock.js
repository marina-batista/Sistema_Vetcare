/* ==========================================================
   mock.js — DADOS DE EXEMPLO para as telas que ficam FORA desta sprint
   (financeiro, pagamentos, notificações, prontuário clínico, vacinas, prescrições).
   Na próxima sprint, troque cada uso de MOCK por uma chamada api("/...").
   ========================================================== */
const MOCK = {
  financeiro: {
    recebido: 48320, saidas: 32700, aReceber: 6150, atendimentos: 412,
    semanas: [
      { rotulo: "Semana 1", entradas: 11200, saidas: 7800, atendimentos: 96 },
      { rotulo: "Semana 2", entradas: 12600, saidas: 8400, atendimentos: 108 },
      { rotulo: "Semana 3", entradas: 11900, saidas: 7900, atendimentos: 99 },
      { rotulo: "Semana 4", entradas: 12620, saidas: 8600, atendimentos: 109 },
    ],
    formas: [["Pix", 52], ["Cartão", 38], ["Dinheiro", 10]],
  },

  // Tabela de preços usada na tela de pagamentos
  precos: { Consulta: 180, Retorno: 90, Vacina: 95, Cirurgia: 1200, Exame: 150 },

  recebimentos: [
    { animal: "Mel", valor: 150, forma: "Pix", quando: "Hoje, 09:40" },
    { animal: "Bob", valor: 220, forma: "Cartão", quando: "Hoje, 08:55" },
    { animal: "Luna", valor: 95, forma: "Dinheiro", quando: "Ontem" },
  ],

  vacinasAVencer: [
    { tutor: "Beatriz Lima", animal: "Luna", assunto: "Vacina V10 vence em 5 dias", canal: "WhatsApp" },
    { tutor: "Juliana Costa", animal: "Nina", assunto: "Vacina antirrábica vence em 7 dias", canal: "E-mail" },
    { tutor: "Ana Paula Souza", animal: "Thor", assunto: "Vacina V10 vence hoje", canal: "WhatsApp" },
  ],

  // Histórico clínico de exemplo (por nome do animal)
  historicoClinico: {
    Thor: [
      { data: "2026-04-08", vet: "Dr. Rafael Nunes", diagnostico: "Otite externa leve.", observacoes: "Limpeza e antibiótico tópico por 7 dias; retorno em 15 dias.", peso: "31 kg" },
      { data: "2025-11-20", vet: "Dra. Camila Rocha", diagnostico: "Check-up sem alterações.", observacoes: "Peso estável; manter a dieta atual.", peso: "32 kg" },
      { data: "2025-05-14", vet: "Dra. Letícia Prado", diagnostico: "Gastroenterite aguda.", observacoes: "Dieta leve, hidratação e probiótico." },
    ],
  },

  vacinas: {
    Thor: [
      { vacina: "V10", fabricante: "Zoetis", lote: "A10021", aplicacao: "2025-10-12", proxima: "2026-10-12" },
      { vacina: "Antirrábica", fabricante: "MSD", lote: "R55410", aplicacao: "2025-09-20", proxima: "2026-09-20" },
      { vacina: "Giárdia", fabricante: "Zoetis", lote: "G88120", aplicacao: "2026-05-14", proxima: "2027-05-14" },
      { vacina: "Gripe canina", fabricante: "Ceva", lote: "C33019", aplicacao: "2026-03-10", proxima: "2027-03-10" },
    ],
  },

  prescricoes: [
    { id: "m1", data: "2026-10-12", animal: "Thor", tutor: "Ana Paula Souza", vet: "Camila Rocha",
      medicamentos: [
        { nome: "Antibiótico tópico otológico", dosagem: "5 gotas", frequencia: "2× ao dia por 7 dias", instrucoes: "Aplicar no ouvido esquerdo." },
        { nome: "Anti-inflamatório oral", dosagem: "1 comprimido", frequencia: "1× ao dia por 3 dias", instrucoes: "Administrar após a refeição" },
      ],
      observacoes: "Retornar em 15 dias para reavaliação." },
    // Exemplos abaixo usam o formato antigo (só o nome); prescricao.js converte automaticamente
    { id: "m2", data: "2026-09-29", animal: "Bob", tutor: "Rogério Alves", medicamentos: ["Anti-inflamatório oral"], orientacoes: "1 comprimido ao dia por 5 dias, após alimentação.", vet: "Camila Rocha" },
    { id: "m3", data: "2026-09-15", animal: "Pipoca", tutor: "Marcos Teixeira", medicamentos: ["Antiparasitário oral"], orientacoes: "Dose única; repetir em 30 dias.", vet: "Camila Rocha" },
    { id: "m4", data: "2026-09-02", animal: "Zeca", tutor: "Paulo Ribeiro", medicamentos: ["Antibiótico oral", "Protetor gástrico"], orientacoes: "A cada 12 horas por 10 dias.", vet: "Camila Rocha" },
    { id: "m5", data: "2026-08-21", animal: "Mia", tutor: "Helena Duarte", medicamentos: ["Vermífugo"], orientacoes: "Dose única.", vet: "Camila Rocha" },
    { id: "m6", data: "2026-08-08", animal: "Thor", tutor: "Ana Paula Souza", medicamentos: ["Shampoo medicamentoso"], orientacoes: "Banho 2x por semana por 4 semanas.", vet: "Camila Rocha" },
    { id: "m7", data: "2026-07-24", animal: "Bob", tutor: "Rogério Alves", medicamentos: ["Colírio lubrificante"], orientacoes: "1 gota em cada olho 3x ao dia.", vet: "Camila Rocha" },
  ],

  faturamento: [
    { grupo: "Pix", qtd: 214, valor: 25126 },
    { grupo: "Cartão", qtd: 156, valor: 18362 },
    { grupo: "Dinheiro", qtd: 42, valor: 4832 },
  ],
};

/* Armazenamento local simples (simula o backend dessas telas nesta sprint) */
const Local = {
  ler(chave, padrao) { try { return JSON.parse(localStorage.getItem("vetcare_" + chave)) ?? padrao; } catch { return padrao; } },
  gravar(chave, valor) { localStorage.setItem("vetcare_" + chave, JSON.stringify(valor)); },
};
