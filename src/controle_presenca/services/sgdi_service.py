import os
import secrets
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Ajuste os imports baseados na sua estrutura de pastas

from src.controle_presenca.database.models import Candidato, Aluno
from src.controle_presenca.utils.criterios_sgdi import calcular_pontuacao
from src.controle_presenca.services.email_service import EmailService


class SGDiService:
    def __init__(self, db: Session):
        self.db = db
        #  O link da planilha fica centralizado aqui de forma segura para quando formos integrar
        self.url_planilha = os.getenv("PLANILHA_INSCRICAO_URL")

    def registrar_novo_candidato(
        self, nome: str, cpf: str, email: str, respostas_questionario: Dict[str, str]
    ) -> Candidato:
        """
        Registra um novo candidato, calcula sua pontuação e salva o histórico de respostas diretamente no JSON.
        """
        # 1. Validação de Duplicata
        candidato_existente = (
            self.db.query(Candidato).filter(Candidato.cpf == cpf).first()
        )
        if candidato_existente:
            raise ValueError(f"O CPF {cpf} já está registrado em nosso sistema.")

        # 2. Cálculo da Pontuação usando o motor de critérios
        # Como guardamos as respostas brutas no JSON, precisamos apenas da pontuação total!
        pontuacao_total, _ = calcular_pontuacao(respostas_questionario)

        # 3. Criação do Candidato no banco
        novo_candidato = Candidato(
            nome=nome,
            cpf=cpf,
            email=email,
            pontuacao_socioeconomica=pontuacao_total,
            status="pendente",
            respostas=respostas_questionario,  # Salva o questionário completo aqui de forma ultra limpa
        )

        try:
            self.db.add(novo_candidato)
            self.db.commit()  # Salva direto na base de dados
            self.db.refresh(novo_candidato)

            return novo_candidato

        except IntegrityError:
            self.db.rollback()
            raise ValueError(
                "Ocorreu um erro de integridade ao salvar no banco de dados. Verifique os dados."
            )
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Erro inesperado ao registrar candidato: {str(e)}")

    def gerar_ranking(self, limite: int = 60):
        # Busca candidatos pendentes e ordena da maior pontuação para a menor
        candidatos = (
            self.db.query(Candidato)
            .filter(Candidato.status == "pendente")
            .order_by(Candidato.pontuacao_socioeconomica.desc())
            .limit(limite)
            .all()
        )
        return candidatos

    def aprovar_corte(self, quantidade: int):
        aprovados = self.gerar_ranking(quantidade)
        for cand in aprovados:
            cand.status = "aprovado"
        self.db.commit()
        return len(aprovados)

    def matricular_candidato(self, cpf: str):
        cand = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()

        if not cand:
            return False, "❌ Candidato não encontrado."
        if cand.status != "aprovado":
            return False, f"⚠️ Candidato não está aprovado (Status: {cand.status})."

        # Muda status do candidato para confirmado
        cand.status = "confirmado"

        # Gera o aluno com um ID de cartão aleatório
        novo_cartao = secrets.randbelow(900000) + 100000

        #  Passamos o cand.id para o Aluno!
        novo_aluno = Aluno(
            cartao_id=novo_cartao,
            nome=cand.nome,
            status="ATIVADO",
            candidato_id=cand.id,
        )

        self.db.add(novo_aluno)
        self.db.commit()

        #  AQUI: Dispara o e-mail de aprovação
        email_service = EmailService()
        email_enviado = email_service.enviar_email_aprovacao(
            destinatario=cand.email, nome_aluno=cand.nome, cartao_id=novo_cartao
        )

        mensagem_final = f"✅ Matrícula confirmada! Aluno {cand.nome} gerado com Cartão ID: {novo_cartao}."
        if email_enviado:
            mensagem_final += " E-mail de boas-vindas enviado!"
        else:
            mensagem_final += " (Aviso: Falha ao enviar o e-mail)."

        return True, mensagem_final

        return (
            True,
            f"✅ Matrícula confirmada! Aluno {cand.nome} gerado com Cartão ID: {novo_cartao}",
        )

    def buscar_candidato_por_cpf_ou_nome(self, termo: str):
        """Busca candidatos aproximando o nome ou batendo o CPF exato."""
        return (
            self.db.query(Candidato)
            .filter((Candidato.cpf == termo) | (Candidato.nome.ilike(f"%{termo}%")))
            .all()
        )

    def remover_candidato(self, cpf: str):
        """Remove um candidato. Graças ao ON DELETE CASCADE do banco,
        isso também apaga o histórico de respostas dele automaticamente."""
        candidato = self.db.query(Candidato).filter(Candidato.cpf == cpf).first()
        if not candidato:
            raise ValueError("Candidato não encontrado.")

        self.db.delete(candidato)
        self.db.commit()
        return True

    def aprovar_turma_oficial(self, limite_vagas: int = 60):
        """Trava de segurança: Aprova estritamente o limite de vagas definido."""
        aprovados = self.gerar_ranking(limite=limite_vagas)

        if not aprovados:
            return 0

        for cand in aprovados:
            cand.status = "aprovado"

        self.db.commit()
        return len(aprovados)
