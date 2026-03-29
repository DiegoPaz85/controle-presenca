import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from controle_presenca.database.models import criar_tabelas, inserir_dados_iniciais, CREATE_TABLES_SQL

class TestModels:
    
    def test_create_tables_sql_exists(self):
        """Testa se a SQL de criação de tabelas existe"""
        assert CREATE_TABLES_SQL is not None
        assert "CREATE TABLE IF NOT EXISTS alunos" in CREATE_TABLES_SQL
        assert "CREATE TABLE IF NOT EXISTS sessoes" in CREATE_TABLES_SQL
        assert "CREATE TABLE IF NOT EXISTS registros" in CREATE_TABLES_SQL
    
    def test_criar_tabelas_function(self):
        """Testa se a função criar_tabelas existe"""
        assert callable(criar_tabelas)
    
    def test_inserir_dados_iniciais_function(self):
        """Testa se a função inserir_dados_iniciais existe"""
        assert callable(inserir_dados_iniciais)
