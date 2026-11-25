"""REQ 06 – Manter Veterinário (CRMV, especialidade e horários de atendimento)"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.seguranca import requer_permissao, usuario_atual
from .esquemas import VeterinarioIn, VeterinarioOut
from .modelos import Veterinario

router = APIRouter(prefix="/veterinarios", tags=["Veterinários (REQ 06)"])
# Cadastro de profissionais faz parte do módulo "Usuários e acessos"; a lista é aberta a qualquer usuário logado
EDITAR = requer_permissao(("usuarios", "editar"))
EXCLUIR = requer_permissao(("usuarios", "excluir"))


def _obter(db: Session, id: int) -> Veterinario:
    v = db.get(Veterinario, id)
    if not v:
        raise HTTPException(404, "Veterinário não encontrado.")
    return v


def _crmv_em_uso(db: Session, crmv: str, ignorar_id: int | None = None) -> bool:
    q = db.query(Veterinario).filter(func.upper(Veterinario.crmv) == crmv.strip().upper())
    if ignorar_id:
        q = q.filter(Veterinario.id != ignorar_id)
    return q.first() is not None


def _salvar(v: Veterinario, dados: VeterinarioIn) -> None:
    v.nome, v.crmv, v.especialidade = dados.nome.strip(), dados.crmv.strip().upper(), dados.especialidade
    v.telefone, v.email, v.ativo = dados.telefone, (dados.email or None), dados.ativo
    v.horarios = [h.model_dump() for h in dados.horarios]


@router.get("", response_model=list[VeterinarioOut])
def listar(q: str | None = None, ativo: bool | None = None,
           db: Session = Depends(get_db), _=Depends(usuario_atual)):
    query = db.query(Veterinario)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(or_(Veterinario.nome.ilike(like), Veterinario.crmv.ilike(like)))
    if ativo is not None:
        query = query.filter(Veterinario.ativo == ativo)
    return query.order_by(Veterinario.ativo.desc(), Veterinario.nome).all()


@router.get("/{id}", response_model=VeterinarioOut)
def obter(id: int, db: Session = Depends(get_db), _=Depends(usuario_atual)):
    return _obter(db, id)


@router.post("", response_model=VeterinarioOut, status_code=201)
def criar(dados: VeterinarioIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    if _crmv_em_uso(db, dados.crmv):
        raise HTTPException(409, "Já existe um veterinário com este CRMV.")
    v = Veterinario()
    _salvar(v, dados)
    db.add(v)
    db.commit()
    return v


@router.put("/{id}", response_model=VeterinarioOut)
def atualizar(id: int, dados: VeterinarioIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    v = _obter(db, id)
    if _crmv_em_uso(db, dados.crmv, ignorar_id=id):
        raise HTTPException(409, "Já existe um veterinário com este CRMV.")
    _salvar(v, dados)
    db.commit()
    return v


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    v = _obter(db, id)
    if v.agendamentos:
        raise HTTPException(409, "Este profissional possui agendamentos. Desative-o em vez de excluir.")
    db.delete(v)
    db.commit()
    return Response(status_code=204)
