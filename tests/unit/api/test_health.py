import pytest
from fastapi.testclient import TestClient

def test_health_endpoint():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "servico": "ExpliCAASO API"}

def test_root_endpoint():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    response = client.get("/api")
    assert response.status_code == 200
    assert "status" in response.json()
