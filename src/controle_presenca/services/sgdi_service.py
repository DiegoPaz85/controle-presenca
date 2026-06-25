import os
import secrets
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# O HistoricoStatusCandidato foi removido desta linha!
from src.controle_presenca.database.models import Candidato, Aluno
from src.controle_presenca.utils.criterios_sgdi import calcular_pontuacao
from src.controle_presenca.services.email_service import EmailService


class SGDiService:
    def __init__(self, db: Session):
        self.db = db
        self.url_planilha = os.getenv("PLANILHA_INSCRICAO_URL")

    def registrar_novo_candidato(
        self, nome: str, cpf: str, email: str, respostas_questionario: Dict[str, str]
    ) -> Candidato:
        # 1. Validação de Duplicata
        candidato_existente = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()
        if candidato_existente:
            raise ValueError(f"O CPF {cpf} já está registrado em nosso sistema.")

        # 2. Cálculo da Pontuação usando o motor de critérios
        pontuacao_total, _ = calcular_pontuacao(respostas_questionario)

        # 3. Criação do Candidato no banco
        novo_candidato = Candidato(
            nome=nome,
            cpf=cpf,
            email=email,
            pontuacao_socioeconomica=pontuacao_total,
            status="pendente",
            respostas=respostas_questionario,
        )

        try:
            self.db.add(novo_candidato)
            self.db.commit()
            self.db.refresh(novo_candidato)
            return novo_candidato
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Ocorreu um erro de integridade ao salvar no banco de dados.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Erro inesperado ao registrar candidato: {str(e)}")

    def cadastrar_candidato(self, nome: str, cpf: str, email: str, respostas: dict = None):
        cpf_limpo = ''.join(c for c in cpf if c.isdigit())
        if len(cpf_limpo) != 11:
            return False, "❌ CPF inválido. Deve conter 11 dígitos."

        nome_limpo = nome.strip().upper()

        c_existente = self.db.query(Candidato).filter(Candidato.cpf == cpf_limpo).first()
        if c_existente:
            return False, f"❌ Candidato com CPF {cpf_limpo} já cadastrado."

        pontos = 0.0
        if respostas:
            from src.controle_presenca.utils.score_calculator import ScoreCalculator
            pontos = ScoreCalculator.calcular_score(respostas)

        novo_cand = Candidato(
            nome=nome_limpo,
            cpf=cpf_limpo,
            email=email.strip(),
            status='pendente',
            pontuacao_socioeconomica=pontos
        )
        self.db.add(novo_cand)
        self.db.commit()
        return True, f"✅ Candidato {nome_limpo} cadastrado com sucesso!"

    def gerar_ranking(self, limite: int = 60):
        candidatos = (
            self.db.query(Candidato)
            .filter(Candidato.status == "pendente")
            .order_by(Candidato.pontuacao_socioeconomica.desc())
            .limit(limite)
            .all()
        )
        return candidatos

    def aprovar_corte(self, quantidade: int):
        total_ativos = self.db.query(Aluno).filter(Aluno.status == 'ATIVADO').count()
        if total_ativos + quantidade > 60:
            vagas = max(0, 60 - total_ativos)
            raise ValueError(
                f"⚠️ O corte de {quantidade} excede o limite máximo de 60 discentes ativos! "
                f"(Atuais: {total_ativos}, Vagas restantes: {vagas})"
            )

        aprovados = self.gerar_ranking(quantidade)
        for cand in aprovados:
            cand.status = "aprovado"
        self.db.commit()
        return len(aprovados)

    def matricular_candidato(self, cpf: str, background_tasks=None):
        cand = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()

        if not cand:
            return False, "❌ Candidato não encontrado."
        if cand.status != "aprovado":
            return False, f"⚠️ Candidato não está aprovado (Status: {cand.status})."

        cand.status = "confirmado"
        novo_cartao = secrets.randbelow(900000) + 100000

        novo_aluno = Aluno(
            cartao_id=novo_cartao,
            nome=cand.nome,
            status="ATIVADO",
            candidato_id=cand.id,
        )
        self.db.add(novo_aluno)
        self.db.commit()

        email_service = EmailService()

        # Otimização com processamento em segundo plano (super rápido!)
        if background_tasks:
            background_tasks.add_task(
                email_service.enviar_email_aprovacao,
                destinatario=cand.email,
                nome_aluno=cand.nome,
                cartao_id=novo_cartao
            )
            mensagem_final = f"✅ Matrícula confirmada! Aluno {cand.nome} gerado com Cartão ID: {novo_cartao}. O e-mail está sendo enviado em segundo plano."
        else:
            email_enviado = email_service.enviar_email_aprovacao(
                destinatario=cand.email, nome_aluno=cand.nome, cartao_id=novo_cartao
            )
            mensagem_final = f"✅ Matrícula confirmada! Aluno {cand.nome} gerado com Cartão ID: {novo_cartao}."
            if email_enviado:
                mensagem_final += " E-mail de boas-vindas enviado!"
            else:
                mensagem_final += " (Aviso: Falha ao enviar o e-mail)."

        return True, mensagem_final

    def buscar_candidato_por_cpf_ou_nome(self, termo: str):
        return (
            self.db.query(Candidato)
            .filter((Candidato.cpf == termo) | (Candidato.nome.ilike(f"%{termo}%")))
            .all()
        )

    def remover_candidato(self, cpf: str):
        candidato = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()
        if not candidato:
            raise ValueError("Candidato não encontrado.")

        self.db.delete(candidato)
        self.db.commit()
        return True

    def aprovar_turma_oficial(self, limite_vagas: int = 60):
        aprovados = self.gerar_ranking(limite=limite_vagas)
        if not aprovados:
            return 0

        for cand in aprovados:
            cand.status = "aprovado"

        self.db.commit()
        return len(aprovados)
