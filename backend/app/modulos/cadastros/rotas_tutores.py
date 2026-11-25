"""REQ 04 – Manter Tutor"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ...core.comum import Pagina
from ...core.database import get_db
from ..autenticacao.seguranca import requer_permissao
from .esquemas import TutorIn, TutorOut
from .modelos import Tutor
from .servicos import tutor_out

router = APIRouter(prefix="/tutores", tags=["Tutores (REQ 04)"])
# Leitura liberada também para quem usa agenda, prontuário e relatórios (precisam listar animais/tutores)
LEITURA = requer_permissao(("tutores_animais", "ver"), ("agenda", "ver"), ("prontuario", "ver"), ("relatorios", "ver"))
EDITAR = requer_permissao(("tutores_animais", "editar"))
EXCLUIR = requer_permissao(("tutores_animais", "excluir"))


def _obter(db: Session, id: int) -> Tutor:
    t = db.get(Tutor, id)
    if not t:
        raise HTTPException(404, "Tutor não encontrado.")
    return t


def _validar_cpf_unico(db: Session, cpf: str | None, ignorar_id: int | None = None) -> None:
    if not cpf:
        return
    q = db.query(Tutor).filter(Tutor.cpf == cpf)
    if ignorar_id:
        q = q.filter(Tutor.id != ignorar_id)
    if q.first():
        raise HTTPException(409, "Já existe um tutor com este CPF.")


@router.get("", response_model=Pagina[TutorOut])
def listar(
    q: str | None = None,
    situacao: Literal["com_animais", "sem_animais"] | None = None,
    pagina: int = Query(1, ge=1),
    tamanho: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    query = db.query(Tutor)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Tutor.nome.ilike(like), Tutor.telefone.ilike(like), Tutor.email.ilike(like)))
    if situacao == "com_animais":
        query = query.filter(Tutor.animais.any())
    elif situacao == "sem_animais":
        query = query.filter(~Tutor.animais.any())
    total = query.count()
    itens = query.order_by(Tutor.nome).offset((pagina - 1) * tamanho).limit(tamanho).all()
    return Pagina(itens=[tutor_out(t) for t in itens], total=total, pagina=pagina, tamanho=tamanho)


@router.get("/{id}", response_model=TutorOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(LEITURA)):
    return tutor_out(_obter(db, id))


@router.post("", response_model=TutorOut, status_code=201)
def criar(dados: TutorIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    _validar_cpf_unico(db, dados.cpf)
    t = Tutor(**dados.model_dump())
    db.add(t)
    db.commit()
    return tutor_out(t)


@router.put("/{id}", response_model=TutorOut)
def atualizar(id: int, dados: TutorIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    t = _obter(db, id)
    _validar_cpf_unico(db, dados.cpf, ignorar_id=id)
    for campo, valor in dados.model_dump().items():
        setattr(t, campo, valor)
    db.commit()
    return tutor_out(t)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    t = _obter(db, id)
    if t.animais:
        raise HTTPException(409, "Este tutor possui animais vinculados. Exclua ou transfira os animais antes.")
    db.delete(t)
    db.commit()
    return Response(status_code=204)
