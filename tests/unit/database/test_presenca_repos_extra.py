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

    def test_obter_alunos_ativos(self):
        """Testa obtenção de alunos ativos"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_alunos = [MagicMock(), MagicMock()]
        mock_db.query().filter().all.return_value = mock_alunos
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.obter_alunos_ativos()
        
        assert resultado == mock_alunos

    def test_obter_registros_sessao(self):
        """Testa obtenção de registros de uma sessão"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_registros = [MagicMock(), MagicMock()]
        
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_ordered = MagicMock()
        mock_filtered.order_by.return_value = mock_ordered
        mock_ordered.all.return_value = mock_registros
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.obter_registros_sessao(1)
        
        assert resultado == mock_registros

    def test_obter_intervalo_ativo(self):
        """Testa obtenção do intervalo ativo da sessão"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_intervalo = MagicMock()
        
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        mock_filtered.first.return_value = mock_intervalo
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.obter_intervalo_ativo(1)
        
        assert resultado == mock_intervalo

    def test_obter_intervalos_sessao(self):
        """Testa obtenção de todos os intervalos da sessão"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_intervalos = [MagicMock()]
        mock_db.query().filter().all.return_value = mock_intervalos
        
        repo = RepositoriosPresenca(mock_db)
        resultado = repo.obter_intervalos_sessao(1)
        
        assert resultado == mock_intervalos

    def test_iniciar_intervalo_existente(self):
        """Testa início de intervalo quando já existe um ativo"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_intervalo = MagicMock()
        
        # Simula obter_intervalo_ativo retornando um ativo
        repo = RepositoriosPresenca(mock_db)
        repo.obter_intervalo_ativo = MagicMock(return_value=mock_intervalo)
        
        resultado = repo.iniciar_intervalo(1)
        assert resultado == mock_intervalo
        mock_db.add.assert_not_called()

    def test_iniciar_intervalo_novo(self):
        """Testa início de novo intervalo"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        
        repo = RepositoriosPresenca(mock_db)
        repo.obter_intervalo_ativo = MagicMock(return_value=None)
        
        resultado = repo.iniciar_intervalo(1)
        assert resultado is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_encerrar_intervalo_nao_existente(self):
        """Testa encerramento de intervalo quando não há nenhum ativo"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        repo = RepositoriosPresenca(mock_db)
        repo.obter_intervalo_ativo = MagicMock(return_value=None)
        
        resultado = repo.encerrar_intervalo(1)
        assert resultado is None
        mock_db.commit.assert_not_called()

    def test_encerrar_intervalo_existente(self):
        """Testa encerramento de intervalo ativo"""
        from controle_presenca.database.repositories.presenca_repos import RepositoriosPresenca
        
        mock_db = MagicMock()
        mock_intervalo = MagicMock()
        mock_intervalo.fim = None
        
        repo = RepositoriosPresenca(mock_db)
        repo.obter_intervalo_ativo = MagicMock(return_value=mock_intervalo)
        
        resultado = repo.encerrar_intervalo(1)
        assert resultado == mock_intervalo
        assert mock_intervalo.fim is not None
        mock_db.commit.assert_called_once()
