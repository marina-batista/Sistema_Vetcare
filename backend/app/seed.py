"""Dados iniciais para demonstração (rodam só quando o banco está vazio).
Para recriar: apague o arquivo backend/vetcare.db e reinicie o servidor."""
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from .modulos.agendamento.modelos import Agendamento
from .modulos.autenticacao.modelos import Usuario
from .modulos.autenticacao.seguranca import hash_senha, normalizar_permissoes
from .modulos.cadastros.modelos import Animal, Tutor, Veterinario
from .modulos.clinico.modelos import Atendimento, Prescricao, Vacina
from .modulos.financeiro.modelos import Pagamento
from .modulos.financeiro.servicos import preco_sugerido

SENHA_PADRAO = "vetcare123"


def _horarios(**dias):
    """_horarios(Segunda=("08:00","12:00"), ...) -> lista no formato do banco (Seg–Sáb)."""
    ordem = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
    chaves = {"Segunda": "seg", "Terça": "ter", "Quarta": "qua", "Quinta": "qui", "Sexta": "sex", "Sábado": "sab"}
    out = []
    for dia in ordem:
        faixa = dias.get(chaves[dia])
        out.append({"dia": dia, "inicio": faixa[0] if faixa else "08:00",
                    "fim": faixa[1] if faixa else "12:00", "ativo": bool(faixa)})
    return out


def _dia_util_anterior(d: date) -> date:
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def popular_se_vazio(db: Session) -> None:
    if db.query(Usuario).first():
        return

    senha = hash_senha(SENHA_PADRAO)
    usuarios = [
        ("Alex Maycon", "alex@vetcare.com", "administrador", True),
        ("Rafael Moreira", "rafael.m@vetcare.com", "administrador", True),
        ("Marina", "marina@vetcare.com", "recepcionista", True),
        ("Mariana Alves", "mariana.a@vetcare.com", "recepcionista", True),
        ("Paulo Santos", "paulo.s@vetcare.com", "recepcionista", True),
        ("Daniela Freitas", "daniela.f@vetcare.com", "recepcionista", False),
        ("Camila Rocha", "camila.r@vetcare.com", "veterinario", True),
        ("Rafael Nunes", "rafael.n@vetcare.com", "veterinario", True),
        ("Letícia Prado", "leticia.p@vetcare.com", "veterinario", True),
    ]
    for nome, email, perfil, ativo in usuarios:
        db.add(Usuario(nome=nome, email=email, perfil=perfil, ativo=ativo, senha_hash=senha,
                       permissoes=normalizar_permissoes(None, perfil)))

    camila = Veterinario(nome="Camila Rocha", crmv="CRMV-BA 00001", especialidade="Clínica geral",
                         telefone="(71) 98100-2001", email="camila.r@vetcare.com",
                         horarios=_horarios(seg=("08:00", "17:00"), ter=("08:00", "17:00"), qua=("08:00", "17:00"),
                                            qui=("13:00", "17:00"), sex=("08:00", "12:00")))
    rafael = Veterinario(nome="Rafael Nunes", crmv="CRMV-BA 00002", especialidade="Cirurgia",
                         telefone="(71) 98100-2002", email="rafael.n@vetcare.com",
                         horarios=_horarios(seg=("08:00", "18:00"), ter=("08:00", "18:00"), qua=("08:00", "18:00"),
                                            qui=("08:00", "18:00"), sex=("08:00", "18:00")))
    leticia = Veterinario(nome="Letícia Prado", crmv="CRMV-BA 00003", especialidade="Dermatologia",
                          telefone="(71) 98100-2003", email="leticia.p@vetcare.com",
                          horarios=_horarios(seg=("08:00", "18:00"), ter=("08:00", "18:00"), qua=("08:00", "18:00"),
                                             qui=("08:00", "18:00"), sex=("08:00", "18:00"), sab=("08:00", "12:00")))
    henrique = Veterinario(nome="Henrique Barros", crmv="CRMV-BA 00004", especialidade="Felinos",
                           telefone="(71) 98100-2004", ativo=False,
                           horarios=_horarios(seg=("08:00", "12:00"), qua=("08:00", "12:00")))
    db.add_all([camila, rafael, leticia, henrique])

    tutores = {}
    for nome, tel, email in [
        ("Ana Paula Souza", "(71) 98700-1122", "anapaula.souza@email.com"),
        ("Carlos Mendes", "(71) 99120-7788", "carlos.m@email.com"),
        ("Beatriz Lima", "(71) 98233-1020", "bia.lima@email.com"),
        ("Rogério Alves", "(71) 99345-6677", "roger.alves@email.com"),
        ("Juliana Costa", "(71) 98456-9900", "ju.costa@email.com"),
        ("Fernando Rocha", "(71) 99871-4412", "fer.rocha@email.com"),
        ("Marcos Teixeira", "(71) 98765-2210", "marcos.t@email.com"),
        ("Paulo Ribeiro", "(71) 98611-3030", "paulo.ribeiro@email.com"),
        ("Helena Duarte", "(71) 99002-4545", "helena.d@email.com"),
        ("Nicolie Mendes", "(71) 98812-3456", "nicola.mendes@email.com"),
    ]:
        tutores[nome] = Tutor(nome=nome, telefone=tel, email=email, cidade="Salvador")
    tutores["Nicolie Mendes"].nome = "Nicolie Alves Mendes dos Santos"
    for tutor, (cep, rua, num, bairro) in {
        "Nicolie Mendes": ("41000-000", "Rua das Acácias", "120", "Pituba"),
        "Ana Paula Souza": ("40150-000", "Rua Marques de Caravelas", "45", "Barra"),
        "Carlos Mendes": ("41820-000", "Avenida Tancredo Neves", "1200", "Caminho das Árvores"),
    }.items():
        t = tutores[tutor]
        t.cep, t.endereco, t.numero, t.bairro = cep, rua, num, bairro
    db.add_all(tutores.values())

    animais = {}
    for nome, esp, raca, sexo, nasc, tutor in [
        ("Thor", "Cão", "Labrador", "Macho", date(2021, 3, 14), "Ana Paula Souza"),
        ("Mel", "Cão", "SRD", "Fêmea", date(2024, 8, 2), "Carlos Mendes"),
        ("Luna", "Gato", "Siamês", "Fêmea", date(2023, 5, 21), "Beatriz Lima"),
        ("Bob", "Cão", "Poodle", "Macho", date(2018, 11, 9), "Rogério Alves"),
        ("Nina", "Gato", "Persa", "Fêmea", date(2025, 1, 30), "Juliana Costa"),
        ("Max", "Cão", "Golden Retriever", "Macho", date(2022, 6, 17), "Fernando Rocha"),
        ("Pipoca", "Cão", "Shih Tzu", "Fêmea", date(2020, 2, 5), "Marcos Teixeira"),
        ("Zeca", "Cão", "Dachshund", "Macho", date(2023, 4, 10), "Paulo Ribeiro"),
        ("Mia", "Gato", "SRD", "Fêmea", date(2024, 3, 2), "Helena Duarte"),
        ("Bidu", "Cão", "Beagle", "Macho", date(2019, 9, 12), "Nicolie Mendes"),
        ("Frida", "Gato", "SRD", "Fêmea", date(2022, 12, 1), "Nicolie Mendes"),
    ]:
        animais[nome] = Animal(nome=nome, especie=esp, raca=raca, sexo=sexo,
                               data_nascimento=nasc, tutor=tutores[tutor])
    db.add_all(animais.values())

    hoje = date.today()

    def ag(dia: date, hora: str, animal: str, vet: Veterinario, tipo: str, status: str, duracao: int = 30):
        h, m = map(int, hora.split(":"))
        novo = Agendamento(animal=animais[animal], veterinario=vet, data_hora=datetime.combine(dia, time(h, m)),
                           tipo=tipo, status=status, duracao_min=duracao)
        if status == "cancelado":
            novo.cancelamento_motivo = "Cancelada pelo tutor"
            novo.cancelamento_justificativa = "Tutora informou que o animal está em viagem."
        db.add(novo)

    # Agenda de hoje (Visão geral da recepção e Fila do dia da Dra. Camila)
    ag(hoje, "09:00", "Thor", camila, "Consulta", "em_atendimento")
    ag(hoje, "09:30", "Mel", rafael, "Retorno", "aguardando")
    ag(hoje, "10:00", "Luna", leticia, "Vacina", "confirmado")
    ag(hoje, "10:30", "Bob", camila, "Retorno", "aguardando")
    ag(hoje, "11:00", "Nina", rafael, "Consulta", "confirmado")
    ag(hoje, "11:30", "Max", leticia, "Consulta", "confirmado")
    ag(hoje, "13:30", "Pipoca", camila, "Vacina", "agendado")
    ag(hoje, "14:00", "Bidu", rafael, "Consulta", "cancelado")
    ag(hoje, "14:30", "Zeca", camila, "Consulta", "agendado")
    ag(hoje, "16:00", "Mia", camila, "Consulta", "agendado")

    # Demais dias úteis da semana atual (Agenda semanal)
    segunda = hoje - timedelta(days=hoje.weekday())
    semana = {
        1: [("08:30", "Nina", rafael, "Consulta", 30), ("14:00", "Max", leticia, "Cirurgia", 60)],
        2: [("09:00", "Thor", camila, "Retorno", 30), ("11:00", "Pipoca", leticia, "Retorno", 30)],
        3: [("10:00", "Mel", rafael, "Consulta", 30), ("15:00", "Bob", camila, "Retorno", 30)],
        4: [("09:30", "Luna", leticia, "Consulta", 30), ("13:00", "Max", rafael, "Vacina", 30)],
        0: [("15:00", "Frida", leticia, "Consulta", 30)],
    }
    for offset, itens in semana.items():
        dia = segunda + timedelta(days=offset)
        if dia == hoje:
            continue
        for hora, animal, vet, tipo, dur in itens:
            ag(dia, hora, animal, vet, tipo, "concluido" if dia < hoje else "confirmado", dur)

    # Histórico (última visita / último atendimento)
    for dias_atras, animal, vet in [
        (30, "Mel", rafael), (40, "Nina", rafael), (45, "Bob", camila), (60, "Thor", rafael),
        (62, "Pipoca", camila), (70, "Zeca", camila), (85, "Mia", camila), (150, "Max", leticia),
        (170, "Luna", leticia), (220, "Bidu", rafael),
    ]:
        ag(_dia_util_anterior(hoje - timedelta(days=dias_atras)), "10:00", animal, vet, "Consulta", "concluido")

    db.commit()
    _popular_clinico_e_financeiro(db, animais, {"Camila Rocha": camila, "Rafael Nunes": rafael, "Letícia Prado": leticia})


# ---------- Dados dos módulos Clínico e Financeiro (REQ 10–15) ----------
def _popular_clinico_e_financeiro(db: Session, animais: dict, vets: dict) -> None:
    """Cria atendimentos (prontuário), vacinas, prescrições e pagamentos a partir das consultas concluídas."""
    hoje = date.today()

    # Atendimentos (REQ 10/11): registra uma consulta concluída recente de alguns animais
    historico = [
        ("Thor", "Camila Rocha", "Otite externa leve.", "Limpeza e antibiótico tópico por 7 dias; retorno em 15 dias.",
         "Tutor relata coceira na orelha há 3 dias.", "38,6 °C", "92 bpm", "31 kg"),
        ("Mel", "Rafael Nunes", "Check-up sem alterações.", "Manter dieta e vermifugação em dia.",
         "Retorno de rotina.", "38,4 °C", "96 bpm", "8 kg"),
        ("Bob", "Camila Rocha", "Gastroenterite aguda.", "Dieta leve, hidratação e protetor gástrico por 5 dias.",
         "Vômito e apatia desde ontem.", "39,1 °C", "110 bpm", "12 kg"),
        ("Pipoca", "Letícia Prado", "Dermatite alérgica.", "Shampoo medicamentoso 2x/semana por 4 semanas.",
         "Lesões na região dorsal.", "38,7 °C", "104 bpm", "6 kg"),
        ("Zeca", "Camila Rocha", "Consulta de rotina.", "Vacinação em dia; peso adequado.",
         "Sem queixas.", "38,5 °C", "100 bpm", "9 kg"),
    ]
    atendimentos = {}
    for i, (an, vet_nome, diag, proc, anam, temp, fc, peso) in enumerate(historico):
        at = Atendimento(
            animal=animais[an], veterinario=vets.get(vet_nome),
            veterinario_nome=f"Dr(a). {vet_nome}", data_hora=datetime.combine(
                _dia_util_anterior(hoje - timedelta(days=30 + i * 12)), time(10, 0)),
            diagnostico=diag, procedimentos=proc, anamnese=anam, exame_fisico="Mucosas normocoradas.",
            temperatura=temp, freq_cardiaca=fc, peso=peso,
            observacoes="Retorno conforme orientação.",
        )
        db.add(at)
        atendimentos[an] = at

    # Vacinas (REQ 12): algumas em dia e outras vencendo nos próximos 30 dias (geram notificação)
    vacinas = [
        ("Thor", "V10", "Zoetis", "A10021", hoje - timedelta(days=400), hoje - timedelta(days=35)),
        ("Thor", "Antirrábica", "MSD", "R55410", hoje - timedelta(days=360), hoje + timedelta(days=5)),
        ("Luna", "V4 (felina)", "Zoetis", "F20110", hoje - timedelta(days=350), hoje + timedelta(days=12)),
        ("Nina", "Antirrábica", "MSD", "R77820", hoje - timedelta(days=340), hoje + timedelta(days=20)),
        ("Mel", "V10", "Ceva", "C88100", hoje - timedelta(days=200), hoje + timedelta(days=165)),
        ("Bob", "Giárdia", "Zoetis", "G44021", hoje - timedelta(days=120), None),
    ]
    for an, nome, fab, lote, aplic, prox in vacinas:
        db.add(Vacina(animal=animais[an], vacina=nome, fabricante=fab, lote=lote,
                      data_aplicacao=aplic, proxima_dose=prox, veterinario_nome="Dra. Camila Rocha"))

    # Prescrições (REQ 13): vinculadas a alguns atendimentos
    db.add(Prescricao(
        animal=animais["Thor"], atendimento=atendimentos["Thor"], veterinario_nome="Dra. Camila Rocha",
        data=atendimentos["Thor"].data_hora,
        medicamentos=[
            {"nome": "Antibiótico tópico otológico", "dosagem": "5 gotas", "frequencia": "2× ao dia por 7 dias",
             "instrucoes": "Aplicar no ouvido esquerdo."},
            {"nome": "Anti-inflamatório oral", "dosagem": "1 comprimido", "frequencia": "1× ao dia por 3 dias",
             "instrucoes": "Administrar após a refeição."},
        ],
        observacoes="Retornar em 15 dias para reavaliação."))
    db.add(Prescricao(
        animal=animais["Bob"], atendimento=atendimentos["Bob"], veterinario_nome="Dra. Camila Rocha",
        data=atendimentos["Bob"].data_hora,
        medicamentos=[{"nome": "Protetor gástrico", "dosagem": "1 comprimido", "frequencia": "A cada 12h por 5 dias",
                       "instrucoes": "Em jejum."}],
        observacoes="Dieta leve por 3 dias."))

    # Pagamentos (REQ 14/15): recebimento das consultas concluídas (deixa algumas sem pagar = "a receber")
    concluidos = db.query(Agendamento).filter(Agendamento.status == "concluido").order_by(Agendamento.data_hora).all()
    formas = ["Pix", "Cartão", "Dinheiro", "Pix", "Cartão", "Pix"]
    for i, a in enumerate(concluidos):
        if i % 7 == 5:  # deixa ~1 em cada 7 sem pagamento registrado
            continue
        db.add(Pagamento(agendamento_id=a.id, animal_id=a.animal_id, valor=preco_sugerido(a.tipo),
                         forma=formas[i % len(formas)], parcelas=1, data=a.data_hora.date(),
                         registrado_por="Marina"))

    db.commit()
