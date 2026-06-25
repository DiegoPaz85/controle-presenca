from fastapi import APIRouter, Depends, HTTPException, status,BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Dict

from src.controle_presenca.database.connection import get_db
from src.controle_presenca.services.sgdi_service import SGDiService
from src.controle_presenca.services.google_sheets_service import GoogleSheetsService
from src.controle_presenca.services.cartola_magica_service import CartolaMagicaService

# 1. Roteador exclusivo do SGDI
router_sgdi = APIRouter(prefix="/sgdi", tags=["SGDI"])

@router_sgdi.post("/sincronizar-forms", status_code=status.HTTP_200_OK)
def sincronizar_forms(db: Session = Depends(get_db)):
    """
    Busca todas as respostas direto na planilha do Google Forms usando a URL do .env.
    Lê as respostas reais e injeta no banco de dados.
    """
    service = GoogleSheetsService(db)
    try:
        resultado = service.sincronizar_dados_forms()
        return {
            "mensagem": "Sincronização com o Google concluída!",
            "detalhes": resultado,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}",
        )

class RegistroCandidatoRequest(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    respostas_questionario: Dict[str, str]

@router_sgdi.post("/candidatos", status_code=status.HTTP_201_CREATED)
def inscrever_candidato(payload: RegistroCandidatoRequest, db: Session = Depends(get_db)):
    """Endpoint para receber os dados de um candidato manualmente e registrá-lo."""
    service = SGDiService(db)
    try:
        candidato = service.registrar_novo_candidato(
            nome=payload.nome,
            cpf=payload.cpf,
            email=payload.email,
            respostas_questionario=payload.respostas_questionario,
        )
        return {
            "mensagem": "Candidato registrado com sucesso!",
            "dados": {
                "id": candidato.id,
                "nome": candidato.nome,
                "pontuacao": candidato.pontuacao_socioeconomica,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor.",
        )

@router_sgdi.get("/candidatos/busca", status_code=status.HTTP_200_OK)
def buscar_candidato(termo: str, db: Session = Depends(get_db)):
    """Pesquisa candidatos por CPF exato ou parte do nome."""
    service = SGDiService(db)
    resultados = service.buscar_candidato_por_cpf_ou_nome(termo)
    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhum candidato encontrado com esse termo.")
    return {"resultados": resultados}

@router_sgdi.delete("/candidatos/{cpf}", status_code=status.HTTP_200_OK)
def remover_candidato(cpf: str, db: Session = Depends(get_db)):
    """Remove um candidato do sistema pelo CPF."""
    service = SGDiService(db)
    try:
        service.remover_candidato(cpf)
        return {"mensagem": f"Candidato com CPF {cpf} removido com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover: {str(e)}")

@router_sgdi.post("/fechar-turma", status_code=status.HTTP_200_OK)
def fechar_turma_e_aprovar(vagas: int = 60, db: Session = Depends(get_db)):
    """Roda o algoritmo de corte e aprova estritamente o número de vagas estipulado."""
    service = SGDiService(db)
    qtd_aprovados = service.aprovar_turma_oficial(limite_vagas=vagas)
    return {
        "mensagem": "Processo de seleção finalizado!",
        "vagas_preenchidas": qtd_aprovados,
    }


# 2. Roteador exclusivo dos Relatórios
router_relatorios = APIRouter(prefix="/relatorios", tags=["Relatórios (Cartola Mágica)"])

@router_relatorios.get("/frequencia", status_code=status.HTTP_200_OK)
def obter_frequencia_geral(db: Session = Depends(get_db)):
    """Gera o relatório completo de presenças e faltas da turma."""
    service = CartolaMagicaService(db)
    return service.gerar_relatorio_frequencia()


@router_sgdi.post("/candidatos/{cpf}/matricular", status_code=status.HTTP_200_OK)
def matricular_candidato(cpf: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Efetiva a matrícula instantaneamente no banco de dados e
    agenda a geração do cartão e o envio do e-mail para o segundo plano.
    """
    service = SGDiService(db)
    try:
        # Se o seu serviço já faz tudo interno, podemos passar as tarefas em segundo plano para ele
        # Ou podemos rodar a função pesada de e-mail aqui.
        
        # Exemplo se o seu service aceitar background_tasks:
        sucesso, mensagem = service.matricular_candidato(cpf, background_tasks=background_tasks)
        
        if not sucesso:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=mensagem)
            
        return {
            "status": "sucesso", 
            "mensagem": "Matrícula efetuada! O e-mail com o cartão está a ser enviado em segundo plano."
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
