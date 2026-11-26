"""Gerenciador de Prontuários (Etapa 1, Figura 1) — REQ 10 Registrar Atendimento e REQ 11 Manter Prontuário.
O prontuário do animal é o histórico dos seus atendimentos."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.modelos import Usuario
from ..autenticacao.seguranca import requer_permissao
from ..cadastros.modelos import Animal
from ..agendamento.modelos import Agendamento
from .esquemas import AtendimentoIn, AtendimentoOut
from .modelos import Atendimento
from .servicos import atendimento_out
from .servicos_vet import veterinario_do_usuario

router = APIRouter(prefix="/atendimentos", tags=["Prontuário (REQ 10, 11)"])
LEITURA = requer_permissao(("prontuario", "ver"))
EDITAR = requer_permissao(("prontuario", "editar"))
EXCLUIR = requer_permissao(("prontuario", "excluir"))


def _obter(db: Session, id: int) -> Atendimento:
    a = db.get(Atendimento, id)
    if not a:
        raise HTTPException(404, "Atendimento não encontrado.")
    return a


@router.get("", response_model=list[AtendimentoOut])
def listar(animal_id: int | None = None, db: Session = Depends(get_db), _=Depends(LEITURA)):
    """Histórico de atendimentos (prontuário). Filtra por animal quando informado."""
    q = db.query(Atendimento)
    if animal_id:
        q = q.filter(Atendimento.animal_id == animal_id)
    return [atendimento_out(a) for a in q.order_by(Atendimento.data_hora.desc())]


@router.get("/{id}", response_model=AtendimentoOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(LEITURA)):
    return atendimento_out(_obter(db, id))


@router.post("", response_model=AtendimentoOut, status_code=201)
def criar(dados: AtendimentoIn, db: Session = Depends(get_db), usuario: Usuario = Depends(EDITAR)):
    """Registra o atendimento (REQ 10). Se vier de um agendamento, conclui a consulta (REQ 07)."""
    if not db.get(Animal, dados.animal_id):
        raise HTTPException(400, "Animal não encontrado.")
    vet = veterinario_do_usuario(db, usuario)
    at = Atendimento(
        **dados.model_dump(),
        veterinario_id=vet.id if vet else None,
        veterinario_nome=usuario.nome,
    )
    db.add(at)
    # Integração com a agenda: conclui o agendamento vinculado, se ainda estiver aberto
    if dados.agendamento_id:
        ag = db.get(Agendamento, dados.agendamento_id)
        if ag and ag.status not in ("concluido", "cancelado"):
            ag.status = "concluido"
    db.commit()
    db.refresh(at)
    return atendimento_out(at)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    db.delete(_obter(db, id))
    db.commit()
    return Response(status_code=204)
