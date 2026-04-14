import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

def test_sessao_ativa_404():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        mock_repo.obter_sessao_ativa.return_value = None
        
        response = client.get("/sessao/ativa")
        assert response.status_code == 404

def test_iniciar_sessao():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        mock_repo.obter_sessao_ativa.return_value = None
        
        mock_sessao = MagicMock()
        mock_sessao.id = 1
        mock_sessao.inicio = datetime.now()
        mock_sessao.status = "ativa"
        mock_repo.criar_sessao.return_value = mock_sessao
        
        response = client.post("/sessao/iniciar")
        assert response.status_code == 200
        assert response.json()["status"] == "ativa"
