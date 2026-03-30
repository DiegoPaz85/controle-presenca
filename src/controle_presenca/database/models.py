from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# --- MÓDULO LEITOR DE PRESENÇA ---
class Aluno(Base):
    __tablename__ = 'alunos'
    id = Column(Integer, primary_key=True, index=True)
    cartao_id = Column(Integer, unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    status = Column(String(20), default='ATIVADO')

class Sessao(Base):
    __tablename__ = 'sessoes'
    id = Column(Integer, primary_key=True, index=True)
    inicio = Column(DateTime, default=datetime.utcnow)
    fim = Column(DateTime, nullable=True)
    status = Column(String(20), default='ativa')

class Registro(Base):
    __tablename__ = 'registros'
    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id'))
    sessao_id = Column(Integer, ForeignKey('sessoes.id'))
    tipo = Column(String(10), nullable=False) # 'entrada' ou 'saida'
    timestamp = Column(DateTime, default=datetime.utcnow)

# --- MÓDULO SGDi (NOVO) ---
class Candidato(Base):
    __tablename__ = 'candidatos'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    status = Column(String(20), default='pendente') # pendente, aprovado, confirmado
    pontuacao_socioeconomica = Column(Float, default=0.0)

class PontuacaoQuestionario(Base):
    __tablename__ = 'pontuacoes_questionario'
    id = Column(Integer, primary_key=True, index=True)
    candidato_id = Column(Integer, ForeignKey('candidatos.id'))
    questao = Column(String(255))
    pontos = Column(Float)
