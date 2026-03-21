import sys
import os
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import db

class PresencaService:
    def __init__(self):
        self.sessao_id = None
        self._carregar_sessao_ativa()
    
    def _carregar_sessao_ativa(self):
        """Carrega sessão ativa se existir"""
        result = db.execute("SELECT id FROM sessoes WHERE status = 'ativa' LIMIT 1")
        if result and len(result) > 0:
            self.sessao_id = result[0]['id']
    
    def iniciar_sessao(self):
        if self.sessao_id:
            return False, "Já existe uma sessão em andamento"
        
        agora = datetime.now()
        
        # Inserir nova sessão e pegar o ID
        db.execute(
            "INSERT INTO sessoes (inicio, status) VALUES (%s, 'ativa')",
            (agora,)
        )
        
        # Buscar o ID da sessão criada
        result = db.execute("SELECT id FROM sessoes WHERE status = 'ativa' ORDER BY inicio DESC LIMIT 1")
        if result and len(result) > 0:
            self.sessao_id = result[0]['id']
            return True, f"Sessão iniciada às {agora.strftime('%H:%M:%S')}"
        else:
            return False, "Erro ao criar sessão"
    
    def encerrar_sessao(self):
        if not self.sessao_id:
            return False, "Nenhuma sessão em andamento"
        
        agora = datetime.now()
        
        # Calcular tempo efetivo (simplificado)
        result = db.execute("SELECT inicio FROM sessoes WHERE id = %s", (self.sessao_id,))
        if result and len(result) > 0:
            inicio = result[0]['inicio']
            tempo_total = (agora - inicio).total_seconds()
        else:
            tempo_total = 0
        
        db.execute("""
            UPDATE sessoes 
            SET fim = %s, status = 'finalizada', tempo_efetivo = %s 
            WHERE id = %s
        """, (agora, tempo_total, self.sessao_id))
        
        self.sessao_id = None
        return True, f"Sessão encerrada às {agora.strftime('%H:%M:%S')}"
    
    def registrar_cartao(self, senha):
        if not self.sessao_id:
            return False, "Sessão não iniciada. Digite 's' para iniciar."
        
        # Buscar aluno pela senha
        alunos = db.execute("SELECT * FROM alunos WHERE senha = %s", (senha,))
        if not alunos or len(alunos) == 0:
            return False, "Cartão não cadastrado"
        
        aluno = alunos[0]
        if aluno['status'] != 'ATIVADO':
            return False, "Cartão desativado"
        
        agora = datetime.now()
        
        # Verificar último registro do aluno nesta sessão
        ultimo = db.execute("""
            SELECT tipo FROM registros 
            WHERE aluno_id = %s AND sessao_id = %s 
            ORDER BY timestamp DESC LIMIT 1
        """, (aluno['id'], self.sessao_id))
        
        if not ultimo or len(ultimo) == 0 or ultimo[0]['tipo'] == 'saida':
            # Registrar entrada
            db.execute("""
                INSERT INTO registros (aluno_id, sessao_id, tipo, timestamp)
                VALUES (%s, %s, 'entrada', %s)
            """, (aluno['id'], self.sessao_id, agora))
            return True, f"✅ Entrada de {aluno['nome']} registrada"
        else:
            # Registrar saída
            db.execute("""
                INSERT INTO registros (aluno_id, sessao_id, tipo, timestamp, tempo_presenca)
                VALUES (%s, %s, 'saida', %s, 0)
            """, (aluno['id'], self.sessao_id, agora))
            return True, f"✅ Saída de {aluno['nome']} registrada"
    
    def get_status(self):
        total_ativos = db.execute("SELECT COUNT(*) as total FROM alunos WHERE status = 'ATIVADO'")
        total_ativos = total_ativos[0]['total'] if total_ativos and len(total_ativos) > 0 else 0
        
        if self.sessao_id:
            presentes = db.execute("""
                SELECT COUNT(DISTINCT aluno_id) as total
                FROM registros 
                WHERE sessao_id = %s AND tipo = 'entrada'
                AND NOT EXISTS (
                    SELECT 1 FROM registros r2 
                    WHERE r2.aluno_id = registros.aluno_id 
                    AND r2.sessao_id = %s 
                    AND r2.tipo = 'saida'
                    AND r2.timestamp > registros.timestamp
                )
            """, (self.sessao_id, self.sessao_id))
            total_presentes = presentes[0]['total'] if presentes and len(presentes) > 0 else 0
        else:
            total_presentes = 0
        
        return {
            'sessao_ativa': self.sessao_id is not None,
            'presentes': total_presentes,
            'total_ativos': total_ativos
        }
    
    def listar_alunos(self):
        return db.execute("""
            SELECT id, cartao_id, nome, senha, status, carga_horaria_total
            FROM alunos ORDER BY cartao_id
        """)
