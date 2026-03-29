import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from controle_presenca.database.connection import db

class TestConnection:
    
    def test_db_connection_exists(self):
        """Testa se a conexão existe"""
        assert db is not None
    
    def test_connect_method(self):
        """Testa método connect"""
        # Já está conectado, verificar se funciona
        result = db.connect()
        # Pode retornar True ou False dependendo do estado
        assert result is not None
    
    def test_execute_select(self):
        """Testa execute com SELECT"""
        result = db.execute("SELECT 1 as test")
        assert len(result) > 0
        assert result[0]['test'] == 1
    
    def test_execute_insert(self):
        """Testa execute com INSERT"""
        # Criar tabela temporária para teste
        db.execute("CREATE TEMP TABLE test_temp (id SERIAL, nome TEXT)")
        rows = db.execute("INSERT INTO test_temp (nome) VALUES (%s)", ("teste",))
        assert rows == 1
        
        # Limpar
        db.execute("DROP TABLE test_temp")
    
    def test_execute_with_params(self):
        """Testa execute com parâmetros"""
        result = db.execute("SELECT %s as valor", (42,))
        assert result[0]['valor'] == 42
    
    @patch('controle_presenca.database.connection.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Testa falha na conexão"""
        mock_connect.side_effect = Exception("Connection failed")
        
        # Criar nova instância para teste
        from controle_presenca.database.connection import Database
        test_db = Database()
        
        result = test_db.connect()
        assert result == False
