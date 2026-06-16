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

def test_encerrar_sessao():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.sessao.PresencaService') as MockService:
        mock_svc = MagicMock()
        MockService.return_value = mock_svc
        mock_svc.encerrar_sessao.return_value = (True, "Sessão encerrada")
        
        response = client.post("/sessao/encerrar")
        assert response.status_code == 200
        assert response.json()["sucesso"] is True

def test_iniciar_intervalo():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.sessao.PresencaService') as MockService:
        mock_svc = MagicMock()
        MockService.return_value = mock_svc
        mock_svc.iniciar_intervalo.return_value = (True, "Intervalo iniciado")
        
        response = client.post("/sessao/intervalo/iniciar")
        assert response.status_code == 200
        assert response.json()["sucesso"] is True

def test_encerrar_intervalo():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.sessao.PresencaService') as MockService:
        mock_svc = MagicMock()
        MockService.return_value = mock_svc
        mock_svc.encerrar_intervalo.return_value = (True, "Intervalo encerrado")
        
        response = client.post("/sessao/intervalo/encerrar")
        assert response.status_code == 200
        assert response.json()["sucesso"] is True

def test_get_status_presenca():
    from src.controle_presenca.api.main import app
    client = TestClient(app)
    
    with patch('src.controle_presenca.api.routes.sessao.RepositoriosPresenca') as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        
        # Simula sessão ativa
        mock_sessao = MagicMock()
        mock_sessao.id = 1
        mock_repo.obter_sessao_ativa.return_value = mock_sessao
        mock_repo.obter_intervalo_ativo.return_value = None
        
        # Simula aluno no banco de dados mockado
        mock_aluno = MagicMock()
        mock_aluno.id = 1
        mock_aluno.nome = "Joao Silva"
        mock_aluno.cartao_id = 123456
        mock_aluno.status = "ATIVADO"
        
        with patch('src.controle_presenca.api.routes.sessao.SessionLocal') as MockSessionLocal:
            mock_session = MagicMock()
            MockSessionLocal.return_value = mock_session
            # Mock da consulta ao banco
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_filter = MagicMock()
            mock_query.filter.return_value = mock_filter
            mock_order = MagicMock()
            mock_filter.order_by.return_value = mock_order
            mock_order.all.return_value = [mock_aluno]
            
            # Simula que o aluno está dentro de sala (último registro é de entrada)
            mock_reg = MagicMock()
            mock_reg.tipo = "entrada"
            mock_repo.obter_ultimo_registro.return_value = mock_reg
            
            response = client.get("/sessao/status-presenca")
            
            assert response.status_code == 200
            data = response.json()
            assert data["sessao_ativa"] is True
            assert data["presentes_sala"] == 1
            assert data["alunos"][0]["localizacao"] == "DENTRO DE SALA"

