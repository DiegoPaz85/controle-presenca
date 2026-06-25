from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# --- MÓDULO LEITOR DE PRESENÇA ---
class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    cartao_id = Column(Integer, unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    status = Column(String(20), default="ATIVADO")

    # Relacionamentos
    registros = relationship("Registro", back_populates="aluno")
    candidato_id = Column(Integer, ForeignKey("candidatos.id"))


class Sessao(Base):
    __tablename__ = "sessoes"

    id = Column(Integer, primary_key=True, index=True)
    inicio = Column(DateTime, default=datetime.utcnow)
    fim = Column(DateTime, nullable=True)
    status = Column(String(20), default="ativa")

    # Relacionamentos
    registros = relationship("Registro", back_populates="sessao")


class IntervaloSessao(Base):
    __tablename__ = 'intervalos_sessao'
    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey('sessoes.id'), nullable=False)
    inicio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fim = Column(DateTime, nullable=True)

class Registro(Base):
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"))
    sessao_id = Column(Integer, ForeignKey("sessoes.id"))
    tipo = Column(String(10), nullable=False)  # 'entrada' ou 'saida'
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    aluno = relationship("Aluno", back_populates="registros")
    sessao = relationship("Sessao", back_populates="registros")


# --- MÓDULO SGDi (NOVO) ---
class Candidato(Base):
    __tablename__ = "candidatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    status = Column(String(20), default="pendente")  # pendente, aprovado, confirmado
    pontuacao_socioeconomica = Column(Float, default=0.0)
    respostas = Column(JSON, nullable=True)


class Questionario(Base):
    __tablename__ = "questionarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)  # Ex: "Socioeconômico 2026"
    ativo = Column(Boolean, default=True)

    # Relação: Um questionário tem várias questões
    questoes = relationship(
        "Questao", back_populates="questionario", cascade="all, delete-orphan"
    )


class Questao(Base):
    __tablename__ = "questoes"

    id = Column(Integer, primary_key=True, index=True)
    questionario_id = Column(Integer, ForeignKey("questionarios.id"), nullable=False)
    texto_pergunta = Column(
        String, nullable=False
    )  # Ex: "Qual é seu nível de escolaridade?"

    questionario = relationship("Questionario", back_populates="questoes")

    # Relação: Uma questão tem várias alternativas
    alternativas = relationship(
        "AlternativaPeso", back_populates="questao", cascade="all, delete-orphan"
    )


class AlternativaPeso(Base):
    __tablename__ = "alternativas_pesos"

    id = Column(Integer, primary_key=True, index=True)
    questao_id = Column(Integer, ForeignKey("questoes.id"), nullable=False)
    texto_alternativa = Column(String, nullable=False)  # Ex: "Ensino médio completo"
    peso = Column(Float, nullable=False)  # Ex: 10.0
    questao = relationship("Questao", back_populates="alternativas")
