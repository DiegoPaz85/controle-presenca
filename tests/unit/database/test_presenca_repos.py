import pytest
import sys
sys.path.insert(0, '/app/src')

from unittest.mock import MagicMock, call

class TestPresencaRepository:
    
    def test_repository_initialization(self):
        """Testa inicialização do repositório"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        repo = RepositoriosPresenca(mock_db)
        
        assert repo is not None
        assert repo.db == mock_db
    
    def test_buscar_aluno_com_cartao_valido(self):
        """Testa busca de aluno por cartao_id"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_filter = MagicMock()
        mock_query.filter.return_value = mock_filter
        mock_aluno = MagicMock()
        mock_filter.first.return_value = mock_aluno
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.buscar_aluno(123456)
        
        assert resultado == mock_aluno
        mock_db.query.assert_called_once()
    
    def test_buscar_aluno_com_cartao_invalido(self):
        """Testa busca de aluno com cartão não existente"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.buscar_aluno(999999)
        
        assert resultado is None
    
    def test_obter_sessao_ativa(self):
        """Testa obtenção da sessão ativa"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        sessao_mock = MagicMock()
        mock_db.query().filter().first.return_value = sessao_mock
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.obter_sessao_ativa()
        
        assert resultado == sessao_mock
    
    def test_registrar_ponto(self):
        """Testa registro de ponto - verifica se add e commit são chamados"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.registrar_ponto(aluno_id=1, sessao_id=1, tipo='entrada')
        
        # Verifica se add e commit foram chamados
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        # O método pode retornar None, então não verificamos resultado
    
    def test_obter_ultimo_registro(self):
        """Testa obtenção do último registro de um aluno em uma sessão"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        registro_mock = MagicMock()
        
        # Simula o encadeamento: query().filter().order_by().first()
        # Como o método real pode usar apenas um filter com múltiplas condições
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        
        # O filter pode receber múltiplos argumentos
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        
        mock_ordered = MagicMock()
        mock_filtered.order_by.return_value = mock_ordered
        
        mock_ordered.first.return_value = registro_mock
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.obter_ultimo_registro(aluno_id=1, sessao_id=1)
        
        # Verifica se o resultado é o registro mockado
        assert resultado == registro_mock
        
        # Verifica se os métodos foram chamados
        mock_db.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_filtered.order_by.assert_called_once()
        mock_ordered.first.assert_called_once()
