from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Ajustando os imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
from src.controle_presenca.services.presenca_service import PresencaService
from src.controle_presenca.database.models import Aluno

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

    class Config:
        from_attributes = True

class AlunoStatusPresenca(BaseModel):
    id: int
    nome: str
    cartao_id: int
    localizacao: str # 'DENTRO DE SALA' ou 'FORA DE SALA'

class StatusPresencaResponse(BaseModel):
    sessao_ativa: bool
    sessao_id: Optional[int] = None
    intervalo_ativo: bool
    total_alunos: int
    presentes_sala: int
    ausentes_sala: int
    percentual_presentes: float
    alunos: List[AlunoStatusPresenca]

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
    service = PresencaService(db)
    sucesso, mensagem = service.encerrar_sessao()
    
    if not sucesso:
        raise HTTPException(
            status_code=400,
            detail=mensagem
        )
    
    return {
        "sucesso": True,
        "mensagem": mensagem
    }

@router.post("/intervalo/iniciar")
def iniciar_intervalo(db: Session = Depends(get_db)):
    service = PresencaService(db)
    sucesso, mensagem = service.iniciar_intervalo()
    
    if not sucesso:
        raise HTTPException(
            status_code=400,
            detail=mensagem
        )
    
    return {
        "sucesso": True,
        "mensagem": mensagem
    }

@router.post("/intervalo/encerrar")
def encerrar_intervalo(db: Session = Depends(get_db)):
    service = PresencaService(db)
    sucesso, mensagem = service.encerrar_intervalo()
    
    if not sucesso:
        raise HTTPException(
            status_code=400,
            detail=mensagem
        )
    
    return {
        "sucesso": True,
        "mensagem": mensagem
    }

@router.get("/status-presenca", response_model=StatusPresencaResponse)
def get_status_presenca(db: Session = Depends(get_db)):
    repo = RepositoriosPresenca(db)
    sessao = repo.obter_sessao_ativa()
    
    # Busca todos os alunos ativos
    alunos_ativos = db.query(Aluno).filter(Aluno.status == 'ATIVADO').order_by(Aluno.nome.asc()).all()
    total_alunos = len(alunos_ativos)
    
    alunos_status = []
    presentes = 0
    
    sessao_ativa = sessao is not None
    sessao_id = sessao.id if sessao_ativa else None
    intervalo_ativo = False
    
    if sessao_ativa:
        intervalo_ativo = repo.obter_intervalo_ativo(sessao.id) is not None
        
        # Mapeia a localização de cada aluno com base no último registro da sessão ativa
        for aluno in alunos_ativos:
            ultimo_reg = repo.obter_ultimo_registro(aluno.id, sessao.id)
            loc = "DENTRO DE SALA" if (ultimo_reg and ultimo_reg.tipo == 'entrada') else "FORA DE SALA"
            if loc == "DENTRO DE SALA":
                presentes += 1
            
            alunos_status.append(AlunoStatusPresenca(
                id=aluno.id,
                nome=aluno.nome,
                cartao_id=aluno.cartao_id,
                localizacao=loc
            ))
    else:
        # Se não há sessão ativa, todos estão fora de sala
        for aluno in alunos_ativos:
            alunos_status.append(AlunoStatusPresenca(
                id=aluno.id,
                nome=aluno.nome,
                cartao_id=aluno.cartao_id,
                localizacao="FORA DE SALA"
            ))
            
    percentual = round((presentes / total_alunos * 100), 2) if total_alunos > 0 else 0.0
    
    return StatusPresencaResponse(
        sessao_ativa=sessao_ativa,
        sessao_id=sessao_id,
        intervalo_ativo=intervalo_ativo,
        total_alunos=total_alunos,
        presentes_sala=presentes,
        ausentes_sala=total_alunos - presentes,
        percentual_presentes=percentual,
        alunos=alunos_status
    )
