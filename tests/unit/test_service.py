import sys
import os
import pytest

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from controle_presenca.services.presenca_service import PresencaService
from controle_presenca.database.connection import db

class TestPresencaService:
    
    @pytest.fixture
    def service(self):
        """Fixture que cria uma instância limpa do serviço para cada teste"""
        # Limpar dados de teste
        db.execute("DELETE FROM registros")
        db.execute("DELETE FROM sessoes")
        return PresencaService()
    
    def test_service_initialization(self, service):
        """Testa inicialização do serviço"""
        assert service is not None
        assert service.sessao_id is None
    
    def test_iniciar_sessao(self, service):
        """Testa iniciar sessão"""
        sucesso, msg = service.iniciar_sessao()
        assert sucesso == True
        assert "Sessão iniciada" in msg
        assert service.sessao_id is not None
    
    def test_encerrar_sessao(self, service):
        """Testa encerrar sessão"""
        service.iniciar_sessao()
        sucesso, msg = service.encerrar_sessao()
        assert sucesso == True
        assert "Sessão encerrada" in msg
        assert service.sessao_id is None
    
    def test_nao_pode_encerrar_sessao_inexistente(self, service):
        """Testa encerrar sessão que não existe"""
        sucesso, msg = service.encerrar_sessao()
        assert sucesso == False
        assert "Nenhuma sessão" in msg
    
    def test_registrar_cartao_sem_sessao(self, service):
        """Testa registrar cartão sem sessão ativa"""
        sucesso, msg = service.registrar_cartao("1")
        assert sucesso == False
        assert "Sessão não iniciada" in msg
    
    def test_registrar_cartao_invalido(self, service):
        """Testa cartão inválido"""
        service.iniciar_sessao()
        sucesso, msg = service.registrar_cartao("999")
        assert sucesso == False
        assert "Cartão não cadastrado" in msg
    
    def test_registrar_entrada_aluno_1(self, service):
        """Testa entrada do aluno 1"""
        service.iniciar_sessao()
        sucesso, msg = service.registrar_cartao("1")
        assert sucesso == True
        assert "Entrada" in msg
        assert "ANA LAURA" in msg
        
        status = service.get_status()
        assert status['presentes'] == 1
    
    def test_registrar_saida_aluno_1(self, service):
        """Testa saída do aluno 1"""
        service.iniciar_sessao()
        service.registrar_cartao("1")  # entrada
        sucesso, msg = service.registrar_cartao("1")  # saída
        assert sucesso == True
        assert "Saída" in msg
        assert "ANA LAURA" in msg
        
        status = service.get_status()
        assert status['presentes'] == 0
    
    def test_multiplos_alunos(self, service):
        """Testa múltiplos alunos"""
        service.iniciar_sessao()
        
        # Entradas
        service.registrar_cartao("1")
        service.registrar_cartao("2")
        service.registrar_cartao("3")
        
        status = service.get_status()
        assert status['presentes'] == 3
        
        # Saídas
        service.registrar_cartao("1")
        service.registrar_cartao("2")
        
        status = service.get_status()
        assert status['presentes'] == 1
    
    def test_get_status_sem_sessao(self, service):
        """Testa status sem sessão"""
        status = service.get_status()
        assert status['sessao_ativa'] == False
        assert status['presentes'] == 0
        assert status['total_ativos'] >= 5
    
    def test_get_status_com_sessao(self, service):
        """Testa status com sessão"""
        service.iniciar_sessao()
        status = service.get_status()
        assert status['sessao_ativa'] == True
        assert 'presentes' in status
        assert 'total_ativos' in status
