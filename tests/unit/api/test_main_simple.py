import pytest

def test_api_module_import():
    """Testa se o módulo da API pode ser importado"""
    from controle_presenca.api import main
    assert main is not None

def test_api_app_exists():
    """Testa se o app FastAPI existe"""
    from controle_presenca.api.main import app
    assert app is not None
    assert app.title == "FastAPI" or hasattr(app, 'routes')
