from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.database.models import Aluno

router = APIRouter(prefix="/alunos", tags=["Alunos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AlunoCreate(BaseModel):
    cartao_id: int
    nome: str
    status: Optional[str] = "ATIVADO"

class AlunoResponse(BaseModel):
    id: int
    cartao_id: int
    nome: str
    status: str

@router.get("/", response_model=List[AlunoResponse])
def listar_alunos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os alunos com paginação"""
    query = db.query(Aluno)
    if status:
        query = query.filter(Aluno.status == status)
    
    alunos = query.offset(skip).limit(limit).all()
    
    return [
        AlunoResponse(
            id=a.id,
            cartao_id=a.cartao_id,
            nome=a.nome,
            status=a.status
        )
        for a in alunos
    ]

@router.get("/{aluno_id}", response_model=AlunoResponse)
def get_aluno(aluno_id: int, db: Session = Depends(get_db)):
    """Retorna um aluno específico"""
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    return AlunoResponse(
        id=aluno.id,
        cartao_id=aluno.cartao_id,
        nome=aluno.nome,
        status=aluno.status
    )

@router.post("/", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    """Cadastra um novo aluno"""
    # Verifica se cartão já existe
    existente = db.query(Aluno).filter(Aluno.cartao_id == aluno.cartao_id).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail=f"Cartão {aluno.cartao_id} já está cadastrado"
        )
    
    novo_aluno = Aluno(
        cartao_id=aluno.cartao_id,
        nome=aluno.nome,
        status=aluno.status
    )
    db.add(novo_aluno)
    db.commit()
    db.refresh(novo_aluno)
    
    return AlunoResponse(
        id=novo_aluno.id,
        cartao_id=novo_aluno.cartao_id,
        nome=novo_aluno.nome,
        status=novo_aluno.status
    )
