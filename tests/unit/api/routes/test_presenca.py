import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_registrar_presenca_sucesso():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.presenca.PresencaService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.processar_leitura.return_value = (True, "ENTRADA registrada")
        
        response = client.post("/presenca/registrar", json={"cartao_id": "123456"})
        assert response.status_code == 200
        assert response.json()["sucesso"] == True

def test_registrar_presenca_falha():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.presenca.PresencaService') as MockService:
        mock_service = MagicMock()
        MockService.return_value = mock_service
        mock_service.processar_leitura.return_value = (False, "Cartão não encontrado")
        
        response = client.post("/presenca/registrar", json={"cartao_id": "999999"})
        assert response.status_code == 400
