import pytest
from unittest.mock import patch

def test_connection_raises_error_without_database_url():
    """Testa que connection.py levanta erro sem DATABASE_URL"""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="DATABASE_URL não encontrada"):
            import controle_presenca.database.connection
            import importlib
            importlib.reload(controle_presenca.database.connection)
