from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Ajustando os imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca

router = APIRouter(prefix="/sessao", tags=["Sessão"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SessaoResponse(BaseModel):
    id: int
    inicio: datetime
    status: str

@router.get("/ativa", response_model=SessaoResponse)
def get_sessao_ativa(db: Session = Depends(get_db)):
    repo = RepositoriosPresenca(db)
    sessao = repo.obter_sessao_ativa()
    
    if not sessao:
        raise HTTPException(status_code=404, detail="Nenhuma sessão ativa")
    
    return SessaoResponse(
        id=sessao.id,
        inicio=sessao.inicio,
        status=sessao.status
    )

@router.post("/iniciar", response_model=SessaoResponse)
def iniciar_sessao(db: Session = Depends(get_db)):
    repo = RepositoriosPresenca(db)
    
    sessao_ativa = repo.obter_sessao_ativa()
    if sessao_ativa:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma sessão ativa (ID: {sessao_ativa.id})"
        )
    
    nova_sessao = repo.criar_sessao()
    
    return SessaoResponse(
        id=nova_sessao.id,
        inicio=nova_sessao.inicio,
        status=nova_sessao.status
    )

@router.post("/encerrar")
def encerrar_sessao(db: Session = Depends(get_db)):
    repo = RepositoriosPresenca(db)
    
    sessao_ativa = repo.obter_sessao_ativa()
    if not sessao_ativa:
        raise HTTPException(status_code=404, detail="Nenhuma sessão ativa")
    
    repo.encerrar_sessao(sessao_ativa)
    
    return {
        "sucesso": True,
        "mensagem": f"Sessão {sessao_ativa.id} encerrada"
    }
