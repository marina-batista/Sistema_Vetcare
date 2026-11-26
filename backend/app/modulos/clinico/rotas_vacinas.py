"""Controle de Vacinas (Etapa 1, Figura 1) — REQ 12 Registrar Vacinação."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.modelos import Usuario
from ..autenticacao.seguranca import requer_permissao
from ..cadastros.modelos import Animal
from .esquemas import VacinaIn, VacinaOut
from .modelos import Vacina
from .servicos import vacina_out

router = APIRouter(prefix="/vacinas", tags=["Vacinação (REQ 12)"])
LEITURA = requer_permissao(("prontuario", "ver"))
EDITAR = requer_permissao(("prontuario", "editar"))
EXCLUIR = requer_permissao(("prontuario", "excluir"))


def _obter(db: Session, id: int) -> Vacina:
    v = db.get(Vacina, id)
    if not v:
        raise HTTPException(404, "Vacina não encontrada.")
    return v


@router.get("", response_model=list[VacinaOut])
def listar(animal_id: int | None = None, db: Session = Depends(get_db), _=Depends(LEITURA)):
    q = db.query(Vacina)
    if animal_id:
        q = q.filter(Vacina.animal_id == animal_id)
    return [vacina_out(v) for v in q.order_by(Vacina.data_aplicacao.desc())]


@router.post("", response_model=VacinaOut, status_code=201)
def criar(dados: VacinaIn, db: Session = Depends(get_db), usuario: Usuario = Depends(EDITAR)):
    if not db.get(Animal, dados.animal_id):
        raise HTTPException(400, "Animal não encontrado.")
    v = Vacina(**dados.model_dump(), veterinario_nome=usuario.nome)
    db.add(v)
    db.commit()
    db.refresh(v)
    return vacina_out(v)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    db.delete(_obter(db, id))
    db.commit()
    return Response(status_code=204)
