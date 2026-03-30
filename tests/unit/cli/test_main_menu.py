import pytest
import sys
sys.path.insert(0, '/app/src')

def test_main_has_executar_menu_function():
    """Testa se main.py tem a função executar_menu"""
    from controle_presenca.main import executar_menu
    assert callable(executar_menu)

def test_main_has_menu_leitor_function():
    """Testa se main.py tem a função menu_leitor"""
    from controle_presenca.main import menu_leitor
    assert callable(menu_leitor)

def test_main_has_menu_sgdi_function():
    """Testa se main.py tem a função menu_sgdi"""
    from controle_presenca.main import menu_sgdi
    assert callable(menu_sgdi)
