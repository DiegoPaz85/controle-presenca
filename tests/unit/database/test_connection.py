import pytest
from unittest.mock import patch, MagicMock

def test_connection_has_session_factory():
    """Testa se a connection tem SessionLocal ou similar"""
    from controle_presenca.database import connection
    
    # Verifica se existe SessionLocal ou get_db
    assert hasattr(connection, 'SessionLocal') or hasattr(connection, 'get_db') or hasattr(connection, 'engine')
    
    # Se tiver engine, verifica se está configurado
    if hasattr(connection, 'engine'):
        assert connection.engine is not None

def test_engine_initialization():
    """Testa se o engine é inicializado"""
    from controle_presenca.database.connection import engine
    
    assert engine is not None
    assert hasattr(engine, 'url')
