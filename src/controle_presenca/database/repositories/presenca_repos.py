from sqlalchemy.orm import Session
from ..models import Aluno, Sessao, Registro, IntervaloSessao
from datetime import datetime, timezone

class RepositoriosPresenca:
    def __init__(self, db: Session):
        self.db = db

    def buscar_aluno(self, cartao_id: int):
        return self.db.query(Aluno).filter(Aluno.cartao_id == cartao_id).first()

    def obter_sessao_ativa(self):
        return self.db.query(Sessao).filter(Sessao.status == 'ativa').first()

    def criar_sessao(self):
        nova_sessao = Sessao()
        self.db.add(nova_sessao)
        self.db.commit()
        return nova_sessao

    def encerrar_sessao(self, sessao: Sessao):
        sessao.fim = datetime.now(timezone.utc)
        sessao.status = 'encerrada'
        self.db.commit()

    def obter_ultimo_registro(self, aluno_id: int, sessao_id: int):
        return self.db.query(Registro).filter(
            Registro.aluno_id == aluno_id,
            Registro.sessao_id == sessao_id
        ).order_by(Registro.timestamp.desc()).first()

    def registrar_ponto(self, aluno_id: int, sessao_id: int, tipo: str):
        novo = Registro(aluno_id=aluno_id, sessao_id=sessao_id, tipo=tipo)
        self.db.add(novo)
        self.db.commit()

    def obter_alunos_ativos(self):
        return self.db.query(Aluno).filter(Aluno.status == 'ATIVADO').all()

    def obter_registros_sessao(self, sessao_id: int):
        return self.db.query(Registro).filter(
            Registro.sessao_id == sessao_id
        ).order_by(Registro.timestamp.asc()).all()

    def obter_intervalo_ativo(self, sessao_id: int):
        return self.db.query(IntervaloSessao).filter(
            IntervaloSessao.sessao_id == sessao_id,
            IntervaloSessao.fim == None
        ).first()

    def obter_intervalos_sessao(self, sessao_id: int):
        return self.db.query(IntervaloSessao).filter(
            IntervaloSessao.sessao_id == sessao_id
        ).all()

    def iniciar_intervalo(self, sessao_id: int):
        ativo = self.obter_intervalo_ativo(sessao_id)
        if ativo:
            return ativo
        novo = IntervaloSessao(sessao_id=sessao_id, inicio=datetime.now(timezone.utc))
        self.db.add(novo)
        self.db.commit()
        return novo

    def encerrar_intervalo(self, sessao_id: int):
        ativo = self.obter_intervalo_ativo(sessao_id)
        if not ativo:
            return None
        ativo.fim = datetime.now(timezone.utc)
        self.db.commit()
        return ativo
