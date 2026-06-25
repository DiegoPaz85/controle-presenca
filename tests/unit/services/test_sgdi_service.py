import pytest
import sys
sys.path.insert(0, '/app/src')

from unittest.mock import MagicMock, patch

def test_sgdi_service_initialization():
    """Testa inicialização do serviço SGDi"""
    from controle_presenca.services.sgdi_service import SGDiService
    
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    
    assert service is not None
    assert service.db == mock_db

def test_sgdi_service_gerar_ranking():
    """Testa geração de ranking de candidatos"""
    from controle_presenca.services.sgdi_service import SGDiService
    
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    mock_order = MagicMock()
    mock_filter.order_by.return_value = mock_order
    mock_limit = MagicMock()
    mock_order.limit.return_value = mock_limit
    mock_candidatos = [MagicMock(), MagicMock()]
    mock_limit.all.return_value = mock_candidatos
    
    service = SGDiService(mock_db)
    resultado = service.gerar_ranking(limite=10)
    
    assert resultado == mock_candidatos
    mock_db.query.assert_called_once()
    mock_query.filter.assert_called_once()
    mock_filter.order_by.assert_called_once()
    mock_order.limit.assert_called_once_with(10)

def test_sgdi_service_aprovar_corte():
    """Testa aprovação de candidatos por corte"""
    from controle_presenca.services.sgdi_service import SGDiService
    
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    
    # Mock do método gerar_ranking
    mock_candidato1 = MagicMock()
    mock_candidato2 = MagicMock()
    mock_candidato1.status = 'pendente'
    mock_candidato2.status = 'pendente'
    service.gerar_ranking = MagicMock(return_value=[mock_candidato1, mock_candidato2])
    
    resultado = service.aprovar_corte(quantidade=2)
    
    assert resultado == 2
    assert mock_candidato1.status == 'aprovado'
    assert mock_candidato2.status == 'aprovado'
    mock_db.commit.assert_called_once()

def test_sgdi_service_matricular_candidato_sucesso():
    """Testa matrícula de candidato aprovado"""
    from controle_presenca.services.sgdi_service import SGDiService
    
    mock_db = MagicMock()
    mock_candidato = MagicMock()
    mock_candidato.status = 'aprovado'
    mock_candidato.nome = 'João Silva'
    mock_db.query().filter().first.return_value = mock_candidato
    
    service = SGDiService(mock_db)
    sucesso, mensagem = service.matricular_candidato(cpf='12345678900')
    
    assert sucesso is True
    assert 'confirmada' in mensagem
    assert 'João Silva' in mensagem
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_sgdi_service_matricular_candidato_nao_encontrado():
    """Testa matrícula de candidato não encontrado"""
    from controle_presenca.services.sgdi_service import SGDiService
    
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    service = SGDiService(mock_db)
    sucesso, mensagem = service.matricular_candidato(cpf='12345678900')
    
    assert sucesso is False
    assert 'não encontrado' in mensagem.lower()
    mock_db.add.assert_not_called()

def test_sgdi_service_matricular_candidato_nao_aprovado():
    """Testa matrícula de candidato não aprovado"""
    from controle_presenca.services.sgdi_service import SGDiService
    
    mock_db = MagicMock()
    mock_candidato = MagicMock()
    mock_candidato.status = 'pendente'
    mock_db.query().filter().first.return_value = mock_candidato
    
    service = SGDiService(mock_db)
    sucesso, mensagem = service.matricular_candidato(cpf='12345678900')
    
    assert sucesso is False
    assert 'não está aprovado' in mensagem.lower()
    mock_db.add.assert_not_called()
