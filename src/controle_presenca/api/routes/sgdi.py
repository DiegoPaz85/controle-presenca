from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

from ...database.connection import SessionLocal
from ...services.sgdi_service import SGDiService

router = APIRouter(prefix="/sgdi", tags=["SGDi"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CandidatoResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    email: str
    status: str
    pontuacao_socioeconomica: float

    class Config:
        from_attributes = True

class HistoricoStatusResponse(BaseModel):
    id: int
    candidato_id: Optional[int] = None
    candidato_nome: Optional[str] = None
    candidato_cpf: Optional[str] = None
    status_anterior: Optional[str] = None
    status_novo: str
    data_alteracao: datetime
    observacao: Optional[str] = None

    class Config:
        from_attributes = True

class MatrículaRequest(BaseModel):
    cpf: str

class AprovarCorteRequest(BaseModel):
    quantidade: int

@router.get("/ranking", response_model=List[CandidatoResponse])
def get_ranking(limite: Optional[int] = 60, db: Session = Depends(get_db)):
    """Ver ranking socioeconômico de candidatos pendentes"""
    service = SGDiService(db)
    return service.gerar_ranking(limite)

@router.post("/aprovar-corte")
def aprovar_candidatos(req: AprovarCorteRequest, db: Session = Depends(get_db)):
    """Aprova os N primeiros candidatos do ranking socioeconômico"""
    service = SGDiService(db)
    try:
        n_aprovados = service.aprovar_corte(req.quantidade)
        return {"mensagem": f"✅ {n_aprovados} candidatos aprovados com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/matricular")
def matricular(req: MatrículaRequest, db: Session = Depends(get_db)):
    """Efetiva a matrícula de um candidato aprovado por CPF"""
    service = SGDiService(db)
    sucesso, mensagem = service.matricular_candidato(req.cpf)
    if not sucesso:
        raise HTTPException(status_code=400, detail=mensagem)
    return {"mensagem": mensagem}

@router.get("/candidatos", response_model=List[CandidatoResponse])
def buscar_candidatos(termo: Optional[str] = "", db: Session = Depends(get_db)):
    """Pesquisa candidatos por nome ou CPF"""
    service = SGDiService(db)
    return service.pesquisar_candidatos(termo)

@router.delete("/candidatos/{candidato_id}")
def excluir_candidato(candidato_id: int, db: Session = Depends(get_db)):
    """Exclui permanentemente um candidato do banco de dados"""
    service = SGDiService(db)
    sucesso = service.excluir_candidato(candidato_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="❌ Candidato não encontrado.")
    return {"mensagem": "✅ Candidato excluído com sucesso."}

@router.delete("/alunos/{aluno_id}")
def desativar_aluno(aluno_id: int, db: Session = Depends(get_db)):
    """Desativa (exclusão lógica) um aluno do controle de presenças"""
    service = SGDiService(db)
    sucesso, mensagem = service.desativar_aluno(aluno_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail=mensagem)
    return {"mensagem": mensagem}

@router.post("/importar")
async def importar_planilha(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Importa candidatos a partir de uma planilha enviada"""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
        
    service = SGDiService(db)
    try:
        inseridos, erros = service.importar_candidatos_planilha(temp_path)
        return {
            "mensagem": "✅ Importação concluída.",
            "inseridos": inseridos,
            "erros": erros
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/sincronizar-drive")
def sincronizar_drive(db: Session = Depends(get_db)):
    """Sincroniza automaticamente a base de candidatos a partir do Google Drive"""
    service = SGDiService(db)
    try:
        sucesso, mensagem = service.sincronizar_importacao_drive()
        if not sucesso:
            raise HTTPException(status_code=400, detail=mensagem)
        return {"mensagem": mensagem}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")

@router.get("/candidatos/{candidato_id}/historico", response_model=List[HistoricoStatusResponse])
def get_historico_candidato(candidato_id: int, db: Session = Depends(get_db)):
    """Retorna o histórico de status de um candidato específico"""
    service = SGDiService(db)
    return service.obter_historico_candidato(candidato_id)

@router.get("/historico-geral", response_model=List[HistoricoStatusResponse])
def get_historico_geral(db: Session = Depends(get_db)):
    """Retorna todo o histórico de status de candidatos (incluindo deletados)"""
    service = SGDiService(db)
    return service.obter_historico_geral()

