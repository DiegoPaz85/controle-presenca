from sqlalchemy.orm import Session
import secrets
from ..database.models import Candidato, Aluno

class SGDiService:
    def __init__(self, db: Session):
        self.db = db

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
