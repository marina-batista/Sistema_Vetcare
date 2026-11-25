"""REQ 05 – Manter Animal (todo animal precisa estar vinculado a um tutor)"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ...core.comum import Pagina
from ...core.database import get_db
from ..autenticacao.seguranca import requer_permissao
from .esquemas import AnimalIn, AnimalOut
from .modelos import Animal, Tutor
from .servicos import animal_out

router = APIRouter(prefix="/animais", tags=["Animais (REQ 05)"])
# Leitura liberada também para quem usa agenda, prontuário e relatórios (precisam listar animais/tutores)
LEITURA = requer_permissao(("tutores_animais", "ver"), ("agenda", "ver"), ("prontuario", "ver"), ("relatorios", "ver"))
EDITAR = requer_permissao(("tutores_animais", "editar"))
EXCLUIR = requer_permissao(("tutores_animais", "excluir"))


def _obter(db: Session, id: int) -> Animal:
    a = db.get(Animal, id)
    if not a:
        raise HTTPException(404, "Animal não encontrado.")
    return a


def _validar_tutor(db: Session, tutor_id: int) -> None:
    if not db.get(Tutor, tutor_id):
        raise HTTPException(400, "Tutor responsável não encontrado.")


@router.get("", response_model=Pagina[AnimalOut])
def listar(
    q: str | None = None,
    tutor_id: int | None = None,
    especie: str | None = None,
    pagina: int = Query(1, ge=1),
    tamanho: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    query = db.query(Animal).join(Tutor)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Animal.nome.ilike(like), Tutor.nome.ilike(like)))
    if tutor_id:
        query = query.filter(Animal.tutor_id == tutor_id)
    if especie:
        query = query.filter(Animal.especie == especie)
    total = query.count()
    itens = query.order_by(Animal.nome).offset((pagina - 1) * tamanho).limit(tamanho).all()
    return Pagina(itens=[animal_out(a) for a in itens], total=total, pagina=pagina, tamanho=tamanho)


@router.get("/{id}", response_model=AnimalOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(LEITURA)):
    return animal_out(_obter(db, id))


@router.post("", response_model=AnimalOut, status_code=201)
def criar(dados: AnimalIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    _validar_tutor(db, dados.tutor_id)
    a = Animal(**dados.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return animal_out(a)


@router.put("/{id}", response_model=AnimalOut)
def atualizar(id: int, dados: AnimalIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    a = _obter(db, id)
    _validar_tutor(db, dados.tutor_id)
    for campo, valor in dados.model_dump().items():
        setattr(a, campo, valor)
    db.commit()
    db.refresh(a)
    return animal_out(a)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    db.delete(_obter(db, id))  # apaga também os agendamentos do animal
    db.commit()
    return Response(status_code=204)
