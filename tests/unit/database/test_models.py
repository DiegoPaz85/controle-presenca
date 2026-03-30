import pytest
import sys
sys.path.insert(0, '/app/src')

class TestModels:
    """Testes para os modelos SQLAlchemy"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Configuração que carrega os modelos"""
        from controle_presenca.database import models
        self.models = models
    
    def test_aluno_model_exists(self):
        """Verifica se o modelo Aluno existe e tem atributos"""
        Aluno = self.models.Aluno
        assert hasattr(Aluno, '__tablename__')
        assert Aluno.__tablename__ == 'alunos'
    
    def test_sessao_model_exists(self):
        """Verifica se o modelo Sessao existe"""
        Sessao = self.models.Sessao
        assert hasattr(Sessao, '__tablename__')
        assert Sessao.__tablename__ == 'sessoes'
    
    def test_registro_model_exists(self):
        """Verifica se o modelo Registro existe"""
        Registro = self.models.Registro
        assert hasattr(Registro, '__tablename__')
        assert Registro.__tablename__ == 'registros'
    
    def test_candidato_model_exists(self):
        """Verifica se o modelo Candidato existe (SGDi)"""
        Candidato = self.models.Candidato
        assert hasattr(Candidato, '__tablename__')
        assert Candidato.__tablename__ == 'candidatos'
    
    def test_pontuacao_questionario_model_exists(self):
        """Verifica se o modelo PontuacaoQuestionario existe"""
        PontuacaoQuestionario = self.models.PontuacaoQuestionario
        assert hasattr(PontuacaoQuestionario, '__tablename__')
        assert PontuacaoQuestionario.__tablename__ == 'pontuacoes_questionario'
    
    def test_aluno_has_required_columns(self):
        """Verifica se Aluno tem as colunas necessárias"""
        Aluno = self.models.Aluno
        required_attrs = ['id', 'cartao_id', 'nome', 'status']
        for attr in required_attrs:
            assert hasattr(Aluno, attr), f"Aluno não tem atributo {attr}"
    
    def test_sessao_has_required_columns(self):
        """Verifica se Sessao tem as colunas necessárias"""
        Sessao = self.models.Sessao
        required_attrs = ['id', 'inicio', 'fim', 'status']
        for attr in required_attrs:
            assert hasattr(Sessao, attr), f"Sessao não tem atributo {attr}"
    
    def test_registro_has_required_columns(self):
        """Verifica se Registro tem as colunas necessárias"""
        Registro = self.models.Registro
        required_attrs = ['id', 'aluno_id', 'sessao_id', 'tipo', 'timestamp']
        for attr in required_attrs:
            assert hasattr(Registro, attr), f"Registro não tem atributo {attr}"
