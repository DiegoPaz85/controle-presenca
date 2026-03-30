import pytest
import sys
sys.path.insert(0, '/app/src')

from unittest.mock import patch, MagicMock

def test_main_import():
    """Testa se main.py pode ser importado"""
    import controle_presenca.main
    assert controle_presenca.main is not None

def test_main_has_menu_functions():
    """Testa se main.py tem as funções de menu"""
    from controle_presenca.main import iniciar_sessao_aula, encerrar_sessao_aula, limpar_tela, _pausar
    
    assert callable(iniciar_sessao_aula)
    assert callable(encerrar_sessao_aula)
    assert callable(limpar_tela)
    assert callable(_pausar)

def test_limpar_tela_execution():
    """Testa se limpar_tela executa sem erro"""
    from controle_presenca.main import limpar_tela
    
    with patch('os.system') as mock_system:
        limpar_tela()
        mock_system.assert_called_once_with('clear')

def test_pausar_execution():
    """Testa se _pausar aguarda input"""
    from controle_presenca.main import _pausar
    
    with patch('builtins.input') as mock_input:
        _pausar()
        mock_input.assert_called_once()

def test_iniciar_sessao_aula_sem_sessao_ativa():
    """Testa iniciar sessão quando não há sessão ativa"""
    from controle_presenca.main import iniciar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = None
        mock_repo.criar_sessao.return_value = True
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input:
                iniciar_sessao_aula()
                
                mock_repo.obter_sessao_ativa.assert_called_once()
                mock_repo.criar_sessao.assert_called_once()

def test_iniciar_sessao_aula_com_sessao_ativa():
    """Testa iniciar sessão quando já existe sessão ativa"""
    from controle_presenca.main import iniciar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.obter_sessao_ativa.return_value = MagicMock()  # Sessão existe
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input:
                with patch('builtins.print') as mock_print:
                    iniciar_sessao_aula()
                    
                    mock_repo.obter_sessao_ativa.assert_called_once()
                    mock_repo.criar_sessao.assert_not_called()
                    # Verifica se a mensagem de aviso foi impressa
                    mock_print.assert_any_call("\n⚠️ Sessão já ativa!")

def test_encerrar_sessao_aula():
    """Testa encerrar sessão de aula"""
    from controle_presenca.main import encerrar_sessao_aula
    
    with patch('controle_presenca.main.SessionLocal') as MockSessionLocal:
        mock_db = MagicMock()
        MockSessionLocal.return_value.__enter__.return_value = mock_db
        
        mock_repo = MagicMock()
        mock_repo.encerrar_sessao.return_value = True
        
        with patch('controle_presenca.main.PresencaService') as MockService:
            MockService.return_value.repo = mock_repo
            
            with patch('builtins.input') as mock_input:
                with patch('builtins.print') as mock_print:
                    encerrar_sessao_aula()
                    
                    mock_repo.encerrar_sessao.assert_called_once()
                    mock_print.assert_any_call("\n✅ Sessão encerrada!")
