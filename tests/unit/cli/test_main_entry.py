import pytest
import sys
sys.path.insert(0, '/app/src')

def test_main_has_executar_menu():
    """Testa se main.py tem a função executar_menu"""
    from controle_presenca.main import executar_menu
    assert callable(executar_menu)

def test_main_has_menu_leitor():
    """Testa se main.py tem a função menu_leitor"""
    from controle_presenca.main import menu_leitor
    assert callable(menu_leitor)

def test_main_has_menu_sgdi():
    """Testa se main.py tem a função menu_sgdi"""
    from controle_presenca.main import menu_sgdi
    assert callable(menu_sgdi)

def test_main_has_iniciar_sessao_aula():
    """Testa se main.py tem a função iniciar_sessao_aula"""
    from controle_presenca.main import iniciar_sessao_aula
    assert callable(iniciar_sessao_aula)

def test_main_has_encerrar_sessao_aula():
    """Testa se main.py tem a função encerrar_sessao_aula"""
    from controle_presenca.main import encerrar_sessao_aula
    assert callable(encerrar_sessao_aula)
