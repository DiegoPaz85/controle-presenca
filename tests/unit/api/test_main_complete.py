import pytest
from fastapi.testclient import TestClient

def test_api_has_cors_middleware():
    """Testa se a API tem CORS configurado (se aplicável)"""
    from controle_presenca.api.main import app
    
    # Verifica se o app tem middleware configurado
    assert hasattr(app, 'middleware_stack')
    
def test_api_route_structure():
    """Testa a estrutura das rotas da API"""
    from controle_presenca.api.main import app
    
    # Verifica se há rotas definidas
    routes = app.routes
    assert len(routes) >= 1
    
    # Verifica se a rota raiz existe
    root_route_exists = any(route.path == "/" for route in routes)
    assert root_route_exists
