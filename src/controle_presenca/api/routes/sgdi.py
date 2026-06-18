from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Dict

# Ajuste os imports conforme a sua estrutura para pegar a dependência do banco
from src.controle_presenca.database.connection import get_db
from src.controle_presenca.services.sgdi_service import SGDiService
from pydantic import BaseModel
from src.controle_presenca.services.google_sheets_service import GoogleSheetsService

router = APIRouter(prefix="/sgdi", tags=["SGDI"])




class SincronizacaoRequest(BaseModel):
    spreadsheet_id: str

@router.post("/sincronizar-forms", status_code=status.HTTP_200_OK)
def sincronizar_forms(payload: SincronizacaoRequest, db: Session = Depends(get_db)):
    """
    Busca todas as respostas direto na planilha do Google Forms.
    (Versão de Teste: Lendo apenas as 3 primeiras questões reais).
    """
    service = GoogleSheetsService(db)
    try:
        resultado = service.sincronizar_dados_forms(spreadsheet_id=payload.spreadsheet_id)
        return {
            "mensagem": "Sincronização com o Google concluída!",
            "detalhes": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- ESQUEMAS DE VALIDAÇÃO (PYDANTIC) ---

class RegistroCandidatoRequest(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    respostas_questionario: Dict[str, str]

# --- ENDPOINTS ---
@router.post("/candidatos", status_code=status.HTTP_201_CREATED)
def inscrever_candidato(payload: RegistroCandidatoRequest, db: Session = Depends(get_db)):
    """
    Endpoint para receber os dados do formulário socioeconômico e registrar o candidato.
    """
    service = SGDiService(db)
    try:
        candidato = service.registrar_novo_candidato(
            nome=payload.nome,
            cpf=payload.cpf,
            email=payload.email,
            respostas_questionario=payload.respostas_questionario
        )
        return {
            "mensagem": "Candidato registrado com sucesso!",
            "dados": {
                "id": candidato.id,
                "nome": candidato.nome,
                "pontuacao": candidato.pontuacao_socioeconomica
            }
        }
    except ValueError as e:
        # Pega nosso erro amigável de "CPF duplicado"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no servidor.")