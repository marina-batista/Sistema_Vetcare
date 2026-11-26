"""Gerenciador de Prescrições (Etapa 1, Figura 1) — REQ 13 Emitir Prescrição."""
from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.modelos import Usuario
from ..autenticacao.seguranca import requer_permissao
from ..cadastros.modelos import Animal
from .esquemas import PrescricaoIn, PrescricaoOut
from .modelos import Atendimento, Prescricao
from .servicos import prescricao_out

router = APIRouter(prefix="/prescricoes", tags=["Prescrições (REQ 13)"])
LEITURA = requer_permissao(("prontuario", "ver"))
EDITAR = requer_permissao(("prontuario", "editar"))
EXCLUIR = requer_permissao(("prontuario", "excluir"))


def _obter(db: Session, id: int) -> Prescricao:
    p = db.get(Prescricao, id)
    if not p:
        raise HTTPException(404, "Prescrição não encontrada.")
    return p


@router.get("", response_model=list[PrescricaoOut])
def listar(
    animal_id: int | None = None,
    data_inicio: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    q = db.query(Prescricao)
    if animal_id:
        q = q.filter(Prescricao.animal_id == animal_id)
    if data_inicio:
        q = q.filter(Prescricao.data >= datetime.combine(datetime.fromisoformat(data_inicio), time.min))
    return [prescricao_out(p) for p in q.order_by(Prescricao.data.desc())]


@router.get("/{id}", response_model=PrescricaoOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(LEITURA)):
    return prescricao_out(_obter(db, id))


@router.post("", response_model=PrescricaoOut, status_code=201)
def criar(dados: PrescricaoIn, db: Session = Depends(get_db), usuario: Usuario = Depends(EDITAR)):
    if not db.get(Animal, dados.animal_id):
        raise HTTPException(400, "Animal não encontrado.")
    if dados.atendimento_id and not db.get(Atendimento, dados.atendimento_id):
        raise HTTPException(400, "Atendimento vinculado não encontrado.")
    p = Prescricao(
        animal_id=dados.animal_id, atendimento_id=dados.atendimento_id,
        medicamentos=[m.model_dump() for m in dados.medicamentos],
        observacoes=dados.observacoes, veterinario_nome=usuario.nome,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return prescricao_out(p)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    db.delete(_obter(db, id))
    db.commit()
    return Response(status_code=204)
