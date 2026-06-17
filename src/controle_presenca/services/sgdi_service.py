from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict
import secrets

# Ajuste os imports baseados na sua estrutura de pastas
from src.controle_presenca.database.models import Candidato, Aluno, PontuacaoQuestionario
from src.controle_presenca.utils.criterios_sgdi import calcular_pontuacao

class SGDiService:
    def __init__(self, db: Session):
        self.db = db

    def registrar_novo_candidato(self, nome: str, cpf: str, email: str, respostas_questionario: Dict[str, str]) -> Candidato:
        """
        Registra um novo candidato, calcula sua pontuação e salva o histórico de respostas.
        """
        # 1. Validação de Duplicata
        candidato_existente = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()
        if candidato_existente:
            raise ValueError(f"O CPF {cpf} já está registrado em nosso sistema.")

        # 2. Cálculo da Pontuação usando o motor de critérios
        pontuacao_total, detalhes_pontuacao = calcular_pontuacao(respostas_questionario)

        # 3. Criação do Candidato no banco
        novo_candidato = Candidato(
            nome=nome,
            cpf=cpf,
            email=email,
            pontuacao_socioeconomica=pontuacao_total,
            status='pendente'
        )

        try:
            self.db.add(novo_candidato)
            self.db.flush() # Gera o ID do candidato na transação atual

            # 4. Inserção do detalhamento das respostas
            respostas_db = []
            for detalhe in detalhes_pontuacao:
                nova_resposta = PontuacaoQuestionario(
                    candidato_id=novo_candidato.id,
                    questao=detalhe["questao"],
                    pontos=detalhe["pontos"]
                )
                respostas_db.append(nova_resposta)

            self.db.add_all(respostas_db)
            self.db.commit()
            self.db.refresh(novo_candidato)
            
            return novo_candidato

        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ocorreu um erro de integridade ao salvar no banco de dados. Verifique os dados.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Erro inesperado ao registrar candidato: {str(e)}")

    def gerar_ranking(self, limite: int = 60):
        # Busca candidatos pendentes e ordena da maior pontuação para a menor
        candidatos = self.db.query(Candidato).filter(Candidato.status == 'pendente').order_by(Candidato.pontuacao_socioeconomica.desc()).limit(limite).all()
        return candidatos

    def aprovar_corte(self, quantidade: int):
        aprovados = self.gerar_ranking(quantidade)
        for cand in aprovados:
            cand.status = 'aprovado'
        self.db.commit()
        return len(aprovados)

    def matricular_candidato(self, cpf: str):
        cand = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()
        
        if not cand:
            return False, "❌ Candidato não encontrado."
        if cand.status != 'aprovado':
            return False, f"⚠️ Candidato não está aprovado (Status: {cand.status})."
            
        # Muda status
        cand.status = 'confirmado'
        
        # Gera o aluno com um ID de cartão aleatório (provisório até você entregar o cartão físico)
        novo_cartao = secrets.randbelow(900000) + 100000
        novo_aluno = Aluno(cartao_id=novo_cartao, nome=cand.nome, status='ATIVADO')
        
        self.db.add(novo_aluno)
        self.db.commit()
        
        
        
        
        
        return True, f"✅ Matrícula confirmada! Aluno {cand.nome} gerado com Cartão ID: {novo_cartao}" 