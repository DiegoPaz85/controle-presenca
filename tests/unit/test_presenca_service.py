import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

# Importar o serviço
try:
    from controle_presenca.services.presenca_service import PresencaService
except ImportError:
    pytest.skip("PresencaService não disponível", allow_module_level=True)

class TestPresencaService:
    
    def test_processar_leitura_sem_sessao_ativa(self):
        """Testa batida de ponto quando não há sessão ativa"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "aula ativa" in mensagem.lower() or "nenhuma aula ativa" in mensagem.lower()
    
    def test_processar_leitura_com_sessao_ativa_e_cartao_valido(self):
        """Testa batida de ponto com sessão ativa e cartão válido"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula que o aluno existe e está ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que não há registro anterior (primeira entrada)
        service.repo.obter_ultimo_registro.return_value = None
        
        # Simula que registro de ponto é salvo
        service.repo.registrar_ponto.return_value = True
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        # Verificações
        assert sucesso is True
        assert "entrada" in mensagem.lower()
        assert "aluno teste" in mensagem.lower()
        
        # Verifica se o método correto foi chamado com os parâmetros certos
        service.repo.registrar_ponto.assert_called_once_with(1, 1, 'entrada')
    
    def test_processar_leitura_com_saida(self):
        """Testa batida de ponto para saída (quando já tem entrada registrada)"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula que o aluno existe e está ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que já tem um registro de entrada
        ultimo_registro = MagicMock()
        ultimo_registro.tipo = 'entrada'
        service.repo.obter_ultimo_registro.return_value = ultimo_registro
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        # Verificações
        assert sucesso is True
        assert "saída" in mensagem.lower()
        service.repo.registrar_ponto.assert_called_once_with(1, 1, 'saida')
    
    def test_processar_leitura_com_cartao_invalido(self):
        """Testa batida de ponto com cartão não numérico"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        sucesso, mensagem = service.processar_leitura("ABC123")
        
        assert sucesso is False
        assert "numérico" in mensagem.lower()
    
    def test_processar_leitura_com_cartao_nao_cadastrado(self):
        """Testa batida de ponto com cartão não cadastrado"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Aluno não encontrado
        service.repo.buscar_aluno.return_value = None
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "não cadastrado" in mensagem.lower()
    
    def test_processar_leitura_com_aluno_inativo(self):
        """Testa batida de ponto com aluno inativo"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Aluno existe mas está inativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Inativo"
        aluno_mock.status = "INATIVO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "inativo" in mensagem.lower()
