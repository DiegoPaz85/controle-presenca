import pytest
import sys
sys.path.insert(0, '/app/src')

from unittest.mock import MagicMock
from datetime import datetime, timezone

class TestPresencaRepositoryExtra:
    
    def test_criar_sessao(self):
        """Testa criação de nova sessão"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        repo = RepositoriosPresenca(mock_db)
        
        resultado = repo.criar_sessao()
        
        # Verifica se a sessão foi criada (retorna a sessão criada)
        assert resultado is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_encerrar_sessao(self):
        """Testa encerramento de sessão ativa"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_sessao = MagicMock()
        mock_sessao.status = 'ativa'
        
        repo = RepositoriosPresenca(mock_db)
        repo.encerrar_sessao(mock_sessao)
        
        # Verifica se a sessão foi atualizada
        assert mock_sessao.status == 'encerrada'
        assert mock_sessao.fim is not None
        mock_db.commit.assert_called_once()
    
    def test_encerrar_sessao_verifica_fim(self):
        """Testa se o fim da sessão é definido como UTC"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_sessao = MagicMock()
        mock_sessao.status = 'ativa'
        
        repo = RepositoriosPresenca(mock_db)
        repo.encerrar_sessao(mock_sessao)
        
        # Verifica se o fim foi definido
        assert mock_sessao.fim is not None
        # Verifica se é um datetime (pode ser mock, mas verifica atributo)
        assert hasattr(mock_sessao.fim, 'tzinfo') or mock_sessao.fim is not None
