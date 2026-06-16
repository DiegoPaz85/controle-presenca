import os
import secrets
from sqlalchemy.orm import Session
from ..database.models import Candidato, Aluno, HistoricoStatusCandidato
from ..utils.score_calculator import ScoreCalculator
from ..utils.google_drive import GoogleDriveDownloader

class SGDiService:
    def __init__(self, db: Session):
        self.db = db

    def cadastrar_candidato(self, nome: str, cpf: str, email: str, respostas: dict = None):
        """
        Cadastra um novo candidato limpando dados (CPF e Nome) e evitando duplicatas.
        Opcionalmente calcula a pontuação socioeconômica real baseada no questionário.
        """
        cpf_limpo = ''.join(c for c in cpf if c.isdigit())
        if len(cpf_limpo) != 11:
            return False, "❌ CPF inválido. Deve conter 11 dígitos."

        nome_limpo = nome.strip().upper()

        # Evita duplicidade por CPF
        c_existente = self.db.query(Candidato).filter(Candidato.cpf == cpf_limpo).first()
        if c_existente:
            return False, f"❌ Candidato com CPF {cpf_limpo} já cadastrado."

        # Calcula a pontuação real caso as respostas do formulário tenham sido informadas
        pontos = 0.0
        if respostas:
            pontos = ScoreCalculator.calcular_score(respostas)

        novo_cand = Candidato(
            nome=nome_limpo,
            cpf=cpf_limpo,
            email=email.strip(),
            status='pendente',
            pontuacao_socioeconomica=pontos
        )
        self.db.add(novo_cand)
        self.db.flush()

        # Registrar no histórico
        historico = HistoricoStatusCandidato(
            candidato_id=novo_cand.id,
            candidato_nome=novo_cand.nome,
            candidato_cpf=novo_cand.cpf,
            status_anterior=None,
            status_novo='pendente',
            observacao="Cadastro inicial do candidato."
        )
        self.db.add(historico)
        self.db.commit()
        return True, f"✅ Candidato {nome_limpo} cadastrado com sucesso!"

    def gerar_ranking(self, limite: int = 60):
        """Busca candidatos pendentes ordenados por pontuação decrescente"""
        return self.db.query(Candidato).filter(
            Candidato.status == 'pendente'
        ).order_by(Candidato.pontuacao_socioeconomica.desc()).limit(limite).all()

    def aprovar_corte(self, quantidade: int):
        """
        Aprova candidatos do topo do ranking, respeitando o limite rígido de 60 discentes ativos.
        """
        total_ativos = self.db.query(Aluno).filter(Aluno.status == 'ATIVADO').count()
        if total_ativos + quantidade > 60:
            vagas = max(0, 60 - total_ativos)
            raise ValueError(
                f"⚠️ O corte de {quantidade} excede o limite máximo de 60 discentes ativos! "
                f"(Atuais: {total_ativos}, Vagas restantes: {vagas})"
            )

        aprovados = self.gerar_ranking(quantidade)
        for cand in aprovados:
            status_anterior = cand.status
            cand.status = 'aprovado'
            
            # Registrar no histórico
            historico = HistoricoStatusCandidato(
                candidato_id=cand.id,
                candidato_nome=cand.nome,
                candidato_cpf=cand.cpf,
                status_anterior=status_anterior,
                status_novo='aprovado',
                observacao="Aprovado no corte socioeconômico."
            )
            self.db.add(historico)
            
        self.db.commit()
        return len(aprovados)

    def matricular_candidato(self, cpf: str):
        """Efetiva a matrícula de um candidato aprovado, gerando o discente ativo"""
        cpf_limpo = ''.join(c for c in cpf if c.isdigit())
        cand = self.db.query(Candidato).filter(Candidato.cpf == cpf_limpo).first()
        
        if not cand:
            return False, "❌ Candidato não encontrado."
        if cand.status != 'aprovado':
            return False, f"⚠️ Candidato não está aprovado (Status: {cand.status})."
            
        # Muda status do candidato
        status_anterior = cand.status
        cand.status = 'confirmado'
        
        # Gera o aluno com cartão aleatório de 6 dígitos
        novo_cartao = secrets.randbelow(900000) + 100000
        novo_aluno = Aluno(cartao_id=novo_cartao, nome=cand.nome, status='ATIVADO')
        
        self.db.add(novo_aluno)
        
        # Registrar no histórico
        historico = HistoricoStatusCandidato(
            candidato_id=cand.id,
            candidato_nome=cand.nome,
            candidato_cpf=cand.cpf,
            status_anterior=status_anterior,
            status_novo='confirmado',
            observacao=f"Matrícula efetuada. Aluno gerado com Cartão ID: {novo_cartao}"
        )
        self.db.add(historico)
        
        self.db.commit()
        
        return True, f"✅ Matrícula confirmada! Aluno {cand.nome} gerado com Cartão ID: {novo_cartao}"

    def pesquisar_candidatos(self, termo: str):
        """Busca candidatos por nome ou CPF"""
        termo_limpo = termo.strip()
        termo_digits = ''.join(c for c in termo_limpo if c.isdigit())
        
        query = self.db.query(Candidato)
        if termo_digits:
            return query.filter(Candidato.cpf.like(f"%{termo_digits}%")).all()
        return query.filter(Candidato.nome.ilike(f"%{termo_limpo}%")).all()

    def excluir_candidato(self, candidato_id: int):
        """Remove fisicamente um candidato do banco de dados"""
        cand = self.db.query(Candidato).filter(Candidato.id == candidato_id).first()
        if not cand:
            return False, "❌ Candidato não encontrado."
            
        # Registrar exclusão no histórico (ID ficará nulo pela FK ondelete SET NULL, mas preservamos auditoria)
        historico = HistoricoStatusCandidato(
            candidato_id=None,
            candidato_nome=cand.nome,
            candidato_cpf=cand.cpf,
            status_anterior=cand.status,
            status_novo='excluido',
            observacao="Candidato excluído fisicamente do sistema."
        )
        self.db.add(historico)
        
        self.db.delete(cand)
        self.db.commit()
        return True, f"✅ Candidato {cand.nome} excluído com sucesso."

    def pesquisar_alunos(self, termo: str):
        """Busca alunos ativos ou desativados por nome ou ID do cartão"""
        termo_limpo = termo.strip()
        if termo_limpo.isdigit():
            return self.db.query(Aluno).filter(Aluno.cartao_id == int(termo_limpo)).all()
        return self.db.query(Aluno).filter(Aluno.nome.ilike(f"%{termo_limpo}%")).all()

    def desativar_aluno(self, aluno_id: int):
        """Exclui logicamente (desativa) um aluno do controle de presenças"""
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not aluno:
            return False, "❌ Aluno não encontrado."
        aluno.status = 'DESATIVADO'
        self.db.commit()
        return True, f"✅ Aluno {aluno.nome} desativado com sucesso!"

    def importar_candidatos_planilha(self, caminho_xlsx: str):
        """
        Importa candidatos a partir de uma planilha de respostas do Google Forms.
        Estrutura de colunas esperada (baseada no legado):
        - Nome: Coluna E (5)
        - CPF: Coluna I (9)
        - Email: Coluna D (4)
        - Respostas do questionário socioeconômico: Colunas K (11) a AI (35) -> Questões 10 a 34 (25 questões)
        """
        import openpyxl
        wb = openpyxl.load_workbook(caminho_xlsx, data_only=True)
        sheet = wb.active

        inseridos = 0
        erros = 0

        for row in range(2, sheet.max_row + 1):
            nome = sheet.cell(row=row, column=5).value
            email = sheet.cell(row=row, column=4).value
            cpf = sheet.cell(row=row, column=9).value

            if not nome or not cpf:
                continue

            respostas = {}
            for col_idx in range(11, 36):
                q_num = col_idx - 1  # K(11) -> q=10
                val = sheet.cell(row=row, column=col_idx).value
                respostas[q_num] = str(val) if val is not None else ""

            # Converte CPF e email para string
            cpf_str = str(cpf).split('.')[0].strip()
            email_str = str(email).strip() if email else ""

            sucesso, _ = self.cadastrar_candidato(str(nome), cpf_str, email_str, respostas)
            if sucesso:
                inseridos += 1
            else:
                erros += 1

        wb.close()
        return inseridos, erros

    def obter_historico_candidato(self, candidato_id: int):
        """Busca o histórico de transições de status de um candidato específico"""
        return self.db.query(HistoricoStatusCandidato).filter(
            HistoricoStatusCandidato.candidato_id == candidato_id
        ).order_by(HistoricoStatusCandidato.data_alteracao.asc()).all()

    def obter_historico_geral(self):
        """Retorna todo o histórico de status de candidatos (incluindo deletados)"""
        return self.db.query(HistoricoStatusCandidato).order_by(
            HistoricoStatusCandidato.data_alteracao.desc()
        ).all()

    def sincronizar_importacao_drive(self):
        """
        Baixa automaticamente o arquivo de respostas do Google Drive
        e executa a importação dos candidatos.
        """
        temp_path = "temp_drive_import.xlsx"
        try:
            # Baixa do Google Drive
            GoogleDriveDownloader.baixar_planilha_forms(temp_path)
            
            # Importa os candidatos
            inseridos, erros = self.importar_candidatos_planilha(temp_path)
            return True, f"✅ Sincronização concluída! {inseridos} candidatos importados, {erros} erros/duplicados."
        except Exception as e:
            return False, f"❌ Erro na sincronização com o Google Drive: {e}"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
