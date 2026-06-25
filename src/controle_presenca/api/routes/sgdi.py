from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Dict

# Ajuste os imports conforme a sua estrutura para pegar a dependência do banco
from src.controle_presenca.database.connection import get_db
from src.controle_presenca.services.sgdi_service import SGDiService
from src.controle_presenca.services.google_sheets_service import GoogleSheetsService
from src.controle_presenca.services.cartola_magica_service import CartolaMagicaService

router = APIRouter(prefix="/sgdi", tags=["SGDI"])

# 🗑️ A classe SincronizacaoRequest foi removida! O link agora é secreto e vem do .env.


@router.post("/sincronizar-forms", status_code=status.HTTP_200_OK)
def sincronizar_forms(db: Session = Depends(get_db)):
    """
    Busca todas as respostas direto na planilha do Google Forms usando a URL do .env.
    Lê as respostas reais e injeta no banco de dados.
    """
    service = GoogleSheetsService(db)
    try:
        # Sem parâmetros! O serviço lê do .env e resolve sozinho.
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


# --- ESQUEMAS DE VALIDAÇÃO (PYDANTIC) ---


class RegistroCandidatoRequest(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    respostas_questionario: Dict[str, str]


# --- ENDPOINTS ---
@router.post("/candidatos", status_code=status.HTTP_201_CREATED)
def inscrever_candidato(
    payload: RegistroCandidatoRequest, db: Session = Depends(get_db)
):
    """
    Endpoint para receber os dados de um candidato manualmente e registrá-lo.
    """
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
        # Pega erro de "CPF duplicado"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor.",
        )


@router.get("/candidatos/busca", status_code=status.HTTP_200_OK)
def buscar_candidato(termo: str, db: Session = Depends(get_db)):
    """
    Pesquisa candidatos por CPF exato ou parte do nome.
    Exemplo: /sgdi/candidatos/busca?termo=João
    """
    service = SGDiService(db)
    resultados = service.buscar_candidato_por_cpf_ou_nome(termo)

    if not resultados:
        raise HTTPException(
            status_code=404, detail="Nenhum candidato encontrado com esse termo."
        )

    return {"resultados": resultados}


@router.delete("/candidatos/{cpf}", status_code=status.HTTP_200_OK)
def remover_candidato(cpf: str, db: Session = Depends(get_db)):
    """
    Remove um candidato do sistema pelo CPF. Operação irreversível.
    """
    service = SGDiService(db)
    try:
        service.remover_candidato(cpf)
        return {"mensagem": f"Candidato com CPF {cpf} removido com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover: {str(e)}")


@router.post("/fechar-turma", status_code=status.HTTP_200_OK)
def fechar_turma_e_aprovar(vagas: int = 60, db: Session = Depends(get_db)):
    """
    Roda o algoritmo de corte e aprova estritamente o número de vagas estipulado (Padrão: 60).
    """
    service = SGDiService(db)
    qtd_aprovados = service.aprovar_turma_oficial(limite_vagas=vagas)

    return {
        "mensagem": "Processo de seleção finalizado!",
        "vagas_preenchidas": qtd_aprovados,
    }


# Aqui rota para criação de relatorios

router = APIRouter(prefix="/relatorios", tags=["Relatórios (Cartola Mágica)"])


@router.get("/frequencia", status_code=status.HTTP_200_OK)
def obter_frequencia_geral(db: Session = Depends(get_db)):
    """
    Gera o relatório completo de presenças e faltas da turma,
    já ordenado para identificar alunos em risco de evasão (< 75%).
    """
    service = CartolaMagicaService(db)
    return service.gerar_relatorio_frequencia()
