from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

# Ajustando os imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.services.presenca_service import PresencaService

router = APIRouter(prefix="/presenca", tags=["Presença"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LeituraCartao(BaseModel):
    cartao_id: str

class PresencaResponse(BaseModel):
    sucesso: bool
    mensagem: str
    tipo: Optional[str] = None

@router.post("/registrar", response_model=PresencaResponse)
def registrar_presenca(leitura: LeituraCartao, db: Session = Depends(get_db)):
    service = PresencaService(db)
    sucesso, mensagem = service.processar_leitura(leitura.cartao_id)
    
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensagem
        )
    
    tipo = "entrada" if "ENTRADA" in mensagem else "saida" if "SAÍDA" in mensagem else None
    
    return PresencaResponse(
        sucesso=sucesso,
        mensagem=mensagem,
        tipo=tipo
    )
