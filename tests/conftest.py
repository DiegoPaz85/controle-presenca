import sys
import os
import pytest
from unittest.mock import MagicMock

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def mock_db():
    """Fixture que fornece um mock da sessão do banco de dados"""
    mock_session = MagicMock()
    mock_session.query.return_value = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.rollback = MagicMock()
    return mock_session

@pytest.fixture
def sample_aluno_data():
    """Fixture com dados de exemplo para aluno"""
    return {
        "id": 1,
        "nome": "João Silva",
        "cartao_id": 123456,
        "status": "ATIVADO"
    }

@pytest.fixture
def sample_sessao_data():
    """Fixture com dados de exemplo para sessão de aula"""
    return {
        "id": 1,
        "inicio": "2026-03-30T19:00:00",
        "fim": None,
        "status": "ativa"
    }

@pytest.fixture
def sample_registro_data():
    """Fixture com dados de exemplo para registro de presença"""
    return {
        "id": 1,
        "aluno_id": 1,
        "sessao_id": 1,
        "tipo": "entrada",
        "timestamp": "2026-03-30T19:05:00"
    }
