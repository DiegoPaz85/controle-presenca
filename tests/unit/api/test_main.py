import pytest
from fastapi.testclient import TestClient

def test_api_root_endpoint():
    """Testa o endpoint raiz da API"""
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCESSO!"

def test_api_health_check():
    """Testa o health check da API"""
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
