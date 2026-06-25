from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..database.repositories.presenca_repos import RepositoriosPresenca
from ..database.models import Aluno, Registro

class PresencaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RepositoriosPresenca(db)

    def iniciar_sessao(self):
        if self.repo.obter_sessao_ativa():
            return False, "⚠️ Sessão já ativa!"
        self.repo.criar_sessao()
        return True, "✅ Sessão iniciada!"

    def encerrar_sessao(self):
        sessao = self.repo.obter_sessao_ativa()
        if not sessao:
            return False, "⚠️ Nenhuma sessão ativa."
        
        # 1. Se houver intervalo aberto, encerra ele primeiro
        self.repo.encerrar_intervalo(sessao.id)
        
        # 2. Encerra a sessão
        self.repo.encerrar_sessao(sessao)
        
        # 3. Recalcula a presença de todos os alunos ativos
        intervalos = self.repo.obter_intervalos_sessao(sessao.id)
        dif_sessao = self.diferenca_efetiva(sessao.inicio, sessao.fim, intervalos)
        
        alunos = self.repo.obter_alunos_ativos()
        for aluno in alunos:
            tempo_presente = self.calcular_tempo_presente_aluno(aluno.id, sessao, intervalos)
            
            # Carga horária anterior em segundos
            carga_anterior_segundos = aluno.carga_horaria_total * 3600
            percentual_anterior = aluno.percentual_presenca
            
            nova_carga_segundos = carga_anterior_segundos + dif_sessao
            if nova_carga_segundos > 0:
                novo_percentual = (
                    (percentual_anterior * 0.01 * carga_anterior_segundos + tempo_presente)
                    / nova_carga_segundos
                ) * 100
                aluno.percentual_presenca = round(novo_percentual, 2)
            else:
                aluno.percentual_presenca = 0.0
                
            aluno.carga_horaria_total = round(nova_carga_segundos / 3600, 3)
            
        self.db.commit()
        return True, "✅ Sessão encerrada e presenças recalculadas!"

    def iniciar_intervalo(self):
        sessao = self.repo.obter_sessao_ativa()
        if not sessao:
            return False, "⚠️ Nenhuma sessão ativa! Inicie uma sessão primeiro."
        
        ativo = self.repo.obter_intervalo_ativo(sessao.id)
        if ativo:
            return False, "⚠️ Intervalo já está ativo."
            
        self.repo.iniciar_intervalo(sessao.id)
        return True, "🟢 Intervalo iniciado com sucesso!"

    def encerrar_intervalo(self):
        sessao = self.repo.obter_sessao_ativa()
        if not sessao:
            return False, "⚠️ Nenhuma sessão ativa."
            
        ativo = self.repo.obter_intervalo_ativo(sessao.id)
        if not ativo:
            return False, "⚠️ Nenhum intervalo ativo para encerrar."
            
        self.repo.encerrar_intervalo(sessao.id)
        return True, "🔴 Intervalo encerrado com sucesso!"

    def diferenca_efetiva(self, t1: datetime, t2: datetime, intervalos: list) -> int:
        def make_naive(dt):
            if dt is None:
                return None
            if dt.tzinfo is not None:
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        
        t1_naive = make_naive(t1)
        t2_naive = make_naive(t2)
        
        if not t1_naive or not t2_naive:
            return 0
            
        sub_intervalos = []
        for i in intervalos:
            i_inicio = make_naive(i.inicio)
            i_fim = make_naive(i.fim) if i.fim else t2_naive
            
            overlap_start = max(i_inicio, t1_naive)
            overlap_end = min(i_fim, t2_naive)
            
            if overlap_start < overlap_end:
                sub_intervalos.append((overlap_start, overlap_end))
                
        total_segundos = int((t2_naive - t1_naive).total_seconds())
        for start, end in sub_intervalos:
            total_segundos -= int((end - start).total_seconds())
            
        return max(0, total_segundos)

    def calcular_tempo_presente_aluno(self, aluno_id: int, sessao, intervalos: list) -> int:
        registros = self.db.query(Registro).filter(
            Registro.aluno_id == aluno_id,
            Registro.sessao_id == sessao.id
        ).order_by(Registro.timestamp.asc()).all()
        
        tempo_total = 0
        entrada = None
        
        for reg in registros:
            if reg.tipo == 'entrada':
                entrada = reg.timestamp
            elif reg.tipo == 'saida' and entrada:
                tempo_total += self.diferenca_efetiva(entrada, reg.timestamp, intervalos)
                entrada = None
                
        if entrada and sessao.fim:
            tempo_total += self.diferenca_efetiva(entrada, sessao.fim, intervalos)
            
        return tempo_total

    def processar_leitura(self, cartao_id: str):
        cleaned_id = cartao_id.strip()
        if cleaned_id.lower().startswith("usb"):
            cleaned_id = cleaned_id[3:]
            
        try:
            cartao_id_int = int(cleaned_id)
        except ValueError:
            return False, "⚠️ ID do cartão deve ser numérico."

        # 1. Verifica sessão ativa
        sessao = self.repo.obter_sessao_ativa()
        if not sessao:
            return False, "⚠️ Nenhuma aula ativa! Inicie uma sessão primeiro."

        # 2. Verifica o aluno
        aluno = self.repo.buscar_aluno(cartao_id_int)
        if not aluno:
            return False, f"❌ Cartão {cartao_id} não cadastrado."
        if aluno.status != 'ATIVADO':
            return False, f"⚠️ Aluno {aluno.nome} está inativo."

        # 3. Define se é entrada ou saída
        ultimo = self.repo.obter_ultimo_registro(aluno.id, sessao.id)
        tipo = 'saida' if (ultimo and ultimo.tipo == 'entrada') else 'entrada'

        # 4. Grava no banco
        self.repo.registrar_ponto(aluno.id, sessao.id, tipo)
        
        acao = "🟢 ENTRADA" if tipo == 'entrada' else "🔴 SAÍDA"
        return True, f"{acao} de {aluno.nome} registrada com sucesso!"
