from sqlalchemy.orm import Session
from sqlalchemy import func
from src.controle_presenca.database.models import Aluno, Registro, Sessao


class CartolaMagicaService:
    def __init__(self, db: Session):
        self.db = db

    def gerar_relatorio_frequencia(self):
        """
        Calcula o % de presença de cada aluno ativo, cruzando o total de
        sessões (aulas) com as entradas registradas no leitor.
        """
        # 1. Quantas aulas já aconteceram no total?
        total_sessoes = self.db.query(Sessao).count()

        if total_sessoes == 0:
            return {
                "mensagem": "Nenhuma aula foi registrada no sistema ainda.",
                "total_aulas_dadas": 0,
                "estatisticas_alunos": [],
            }

        resultados = []
        # 2. Pega todos os alunos matriculados
        alunos = self.db.query(Aluno).filter(Aluno.status == "ATIVADO").all()

        for aluno in alunos:
            # 3. Conta em quantas sessões DISTINTAS este aluno bateu o cartão de "entrada"
            presencas = (
                self.db.query(func.count(func.distinct(Registro.sessao_id)))
                .filter(Registro.aluno_id == aluno.id)
                .filter(Registro.tipo == "entrada")
                .scalar()
            )

            # Se presencas voltar None por algum motivo, garante que é 0
            presencas = presencas or 0

            porcentagem = (presencas / total_sessoes) * 100

            resultados.append(
                {
                    "cartao_id": aluno.cartao_id,
                    "nome": aluno.nome,
                    "presencas": presencas,
                    "faltas": total_sessoes - presencas,
                    "porcentagem_frequencia": round(porcentagem, 2),
                    "alerta_evasao": porcentagem
                    < 75.0,  # Flag visual para a coordenação agir
                }
            )

        # 4. Ordena o relatório: Quem tem menos frequência aparece primeiro no topo!
        resultados.sort(key=lambda x: x["porcentagem_frequencia"])

        return {"total_aulas_dadas": total_sessoes, "estatisticas_alunos": resultados}
