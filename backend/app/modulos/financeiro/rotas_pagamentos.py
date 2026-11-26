"""REQ 14 – Registrar Pagamento (recebimento de consultas e procedimentos)."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ...core.database import get_db
from ..autenticacao.modelos import Usuario
from ..autenticacao.seguranca import requer_permissao
from ..agendamento.modelos import Agendamento
from .esquemas import PagamentoIn, PagamentoOut
from .modelos import Pagamento
from .servicos import PRECOS, pagamento_out

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos (REQ 14)"])
LEITURA = requer_permissao(("pagamentos", "ver"), ("relatorios", "ver"))
EDITAR = requer_permissao(("pagamentos", "editar"))
EXCLUIR = requer_permissao(("pagamentos", "excluir"))


def _obter(db: Session, id: int) -> Pagamento:
    p = db.get(Pagamento, id)
    if not p:
        raise HTTPException(404, "Pagamento não encontrado.")
    return p


@router.get("/precos")
def tabela_precos(_=Depends(LEITURA)):
    """Tabela de preços de referência (sugere o valor no recebimento)."""
    return PRECOS


@router.get("", response_model=list[PagamentoOut])
def listar(
    data_inicio: date | None = None,
    data_fim: date | None = None,
    limite: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(LEITURA),
):
    q = db.query(Pagamento)
    if data_inicio:
        q = q.filter(Pagamento.data >= data_inicio)
    if data_fim:
        q = q.filter(Pagamento.data <= data_fim)
    itens = q.order_by(Pagamento.criado_em.desc()).limit(limite).all()
    return [pagamento_out(p) for p in itens]


@router.post("", response_model=PagamentoOut, status_code=201)
def criar(dados: PagamentoIn, db: Session = Depends(get_db), usuario: Usuario = Depends(EDITAR)):
    ag = None
    if dados.agendamento_id:
        ag = db.get(Agendamento, dados.agendamento_id)
        if not ag:
            raise HTTPException(400, "Atendimento não encontrado.")
    p = Pagamento(
        **dados.model_dump(),
        registrado_por=usuario.nome,
    )
    # Se o animal não veio no corpo, usa o do agendamento
    if not p.animal_id and ag:
        p.animal_id = ag.animal_id
    db.add(p)
    db.commit()
    db.refresh(p)
    return pagamento_out(p)


@router.delete("/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), _=Depends(EXCLUIR)):
    db.delete(_obter(db, id))
    db.commit()
    return Response(status_code=204)
