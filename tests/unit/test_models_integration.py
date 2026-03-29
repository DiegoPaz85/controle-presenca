import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from controle_presenca.database.models import criar_tabelas, inserir_dados_iniciais
from controle_presenca.database.connection import db

class TestModelsIntegration:
    
    @pytest.fixture
    def setup_database(self):
        """Configura banco de dados para teste"""
        # Limpar tabelas
        db.execute("DROP TABLE IF EXISTS registros CASCADE")
        db.execute("DROP TABLE IF EXISTS intervalos CASCADE")
        db.execute("DROP TABLE IF EXISTS sessoes CASCADE")
        db.execute("DROP TABLE IF EXISTS alunos CASCADE")
        yield
        # Limpar após teste
        db.execute("DROP TABLE IF EXISTS registros CASCADE")
        db.execute("DROP TABLE IF EXISTS intervalos CASCADE")
        db.execute("DROP TABLE IF EXISTS sessoes CASCADE")
        db.execute("DROP TABLE IF EXISTS alunos CASCADE")
    
    def test_criar_tabelas_executa_sem_erro(self, setup_database):
        """Testa se criar_tabelas executa sem erros"""
        try:
            criar_tabelas()
            assert True
        except Exception as e:
            pytest.fail(f"criar_tabelas falhou: {e}")
    
    def test_inserir_dados_iniciais_executa_sem_erro(self, setup_database):
        """Testa se inserir_dados_iniciais executa sem erros"""
        criar_tabelas()
        try:
            inserir_dados_iniciais()
            
            # Verificar se os dados foram inseridos
            alunos = db.execute("SELECT COUNT(*) as total FROM alunos")
            assert alunos[0]['total'] >= 5
            
        except Exception as e:
            pytest.fail(f"inserir_dados_iniciais falhou: {e}")
    
    def test_tabelas_criadas_corretamente(self, setup_database):
        """Testa se as tabelas foram criadas com as colunas corretas"""
        criar_tabelas()
        
        # Verificar tabela alunos
        colunas_alunos = db.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'alunos'
        """)
        
        colunas = [c['column_name'] for c in colunas_alunos]
        assert 'id' in colunas
        assert 'cartao_id' in colunas
        assert 'nome' in colunas
        assert 'senha' in colunas
        assert 'status' in colunas
        
        # Verificar tabela sessoes
        colunas_sessoes = db.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sessoes'
        """)
        
        colunas_s = [c['column_name'] for c in colunas_sessoes]
        assert 'id' in colunas_s
        assert 'inicio' in colunas_s
        assert 'fim' in colunas_s
        assert 'status' in colunas_s
