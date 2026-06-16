# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from unittest.mock import MagicMock, patch
# pyrefly: ignore [missing-import]
from datetime import datetime, timezone

# Importar o serviço
try:
    # pyrefly: ignore [missing-import]
    from controle_presenca.services.presenca_service import PresencaService
except ImportError:
    pytest.skip("PresencaService não disponível", allow_module_level=True)

class TestPresencaService:
    
    def test_processar_leitura_sem_sessao_ativa(self):
        """Testa batida de ponto quando não há sessão ativa"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "aula ativa" in mensagem.lower() or "nenhuma aula ativa" in mensagem.lower()
    
    def test_processar_leitura_com_sessao_ativa_e_cartao_valido(self):
        """Testa batida de ponto com sessão ativa e cartão válido"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula que o aluno existe e está ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que não há registro anterior (primeira entrada)
        service.repo.obter_ultimo_registro.return_value = None
        
        # Simula que registro de ponto é salvo
        service.repo.registrar_ponto.return_value = True
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        # Verificações
        assert sucesso is True
        assert "entrada" in mensagem.lower()
        assert "aluno teste" in mensagem.lower()
        
        # Verifica se o método correto foi chamado com os parâmetros certos
        service.repo.registrar_ponto.assert_called_once_with(1, 1, 'entrada')
    
    def test_processar_leitura_com_saida(self):
        """Testa batida de ponto para saída (quando já tem entrada registrada)"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula que o aluno existe e está ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que já tem um registro de entrada
        ultimo_registro = MagicMock()
        ultimo_registro.tipo = 'entrada'
        service.repo.obter_ultimo_registro.return_value = ultimo_registro
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        # Verificações
        assert sucesso is True
        assert "saída" in mensagem.lower()
        service.repo.registrar_ponto.assert_called_once_with(1, 1, 'saida')

    def test_processar_leitura_com_prefixo_usb(self):
        """Testa batida de ponto com leitor enviando prefixo 'usb' (caso comum em leitores físicos)"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Simula uma sessão ativa
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Simula aluno ativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Teste"
        aluno_mock.status = "ATIVADO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        # Simula que não há registro anterior
        service.repo.obter_ultimo_registro.return_value = None
        service.repo.registrar_ponto.return_value = True
        
        # Chamada com prefixo 'usb' (sensitivo a maiúsculas/minúsculas)
        sucesso, mensagem = service.processar_leitura("usb123456")
        
        # Verificações
        assert sucesso is True
        assert "entrada" in mensagem.lower()
        service.repo.buscar_aluno.assert_called_once_with(123456)
    
    def test_processar_leitura_com_cartao_invalido(self):
        """Testa batida de ponto com cartão não numérico"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        sucesso, mensagem = service.processar_leitura("ABC123")
        
        assert sucesso is False
        assert "numérico" in mensagem.lower()
    
    def test_processar_leitura_com_cartao_nao_cadastrado(self):
        """Testa batida de ponto com cartão não cadastrado"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Aluno não encontrado
        service.repo.buscar_aluno.return_value = None
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "não cadastrado" in mensagem.lower()
    
    def test_processar_leitura_com_aluno_inativo(self):
        """Testa batida de ponto com aluno inativo"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        # Sessão ativa existe
        sessao_mock = MagicMock()
        sessao_mock.id = 1
        service.repo.obter_sessao_ativa.return_value = sessao_mock
        
        # Aluno existe mas está inativo
        aluno_mock = MagicMock()
        aluno_mock.id = 1
        aluno_mock.nome = "Aluno Inativo"
        aluno_mock.status = "INATIVO"
        service.repo.buscar_aluno.return_value = aluno_mock
        
        sucesso, mensagem = service.processar_leitura("123456")
        
        assert sucesso is False
        assert "inativo" in mensagem.lower()

    def test_iniciar_sessao_existente(self):
        """Testa iniciar sessão quando já existe uma ativa"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = MagicMock()
        
        sucesso, msg = service.iniciar_sessao()
        assert sucesso is False
        assert "Sessão já ativa" in msg

    def test_iniciar_sessao_nova(self):
        """Testa iniciar sessão com sucesso"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.iniciar_sessao()
        assert sucesso is True
        assert "iniciada" in msg
        service.repo.criar_sessao.assert_called_once()

    def test_encerrar_sessao_inexistente(self):
        """Testa encerrar sessão quando nenhuma está ativa"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.encerrar_sessao()
        assert sucesso is False
        assert "Nenhuma sessão ativa" in msg

    def test_encerrar_sessao_sucesso(self):
        """Testa encerrar sessão com sucesso e recalcular presenças"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        
        sessao = MagicMock()
        sessao.id = 1
        sessao.inicio = datetime(2026, 3, 30, 19, 0, 0, tzinfo=timezone.utc)
        sessao.fim = datetime(2026, 3, 30, 22, 0, 0, tzinfo=timezone.utc)
        service.repo.obter_sessao_ativa.return_value = sessao
        
        # Alunos
        aluno1 = MagicMock()
        aluno1.id = 10
        aluno1.carga_horaria_total = 10.0 # horas
        aluno1.percentual_presenca = 80.0
        
        service.repo.obter_alunos_ativos.return_value = [aluno1]
        
        # Mocks de cálculos
        service.diferenca_efetiva = MagicMock(return_value=10800) # 3 horas da sessão
        service.calcular_tempo_presente_aluno = MagicMock(return_value=10800) # esteve presente 3 horas
        
        sucesso, msg = service.encerrar_sessao()
        assert sucesso is True
        assert "encerrada" in msg
        
        # Verificação do recálculo:
        # Carga anterior = 10.0 horas (36000s) a 80.0% = 28800s presente.
        # Sessão durou 3 horas (10800s), presente 3 horas (10800s).
        # Nova carga = 46800s. Novo presente = 39600s.
        # Novo percentual = 39600 / 46800 = 84.62%
        # Nova carga em horas = 13.0
        assert aluno1.carga_horaria_total == 13.0
        assert aluno1.percentual_presenca == 84.62

    def test_iniciar_intervalo_sem_sessao(self):
        """Testa iniciar intervalo sem sessão ativa"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.iniciar_intervalo()
        assert sucesso is False
        assert "Nenhuma sessão ativa" in msg

    def test_iniciar_intervalo_ativo(self):
        """Testa iniciar intervalo quando um já está ativo"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = MagicMock(id=1)
        service.repo.obter_intervalo_ativo.return_value = MagicMock()
        
        sucesso, msg = service.iniciar_intervalo()
        assert sucesso is False
        assert "Intervalo já está ativo" in msg

    def test_iniciar_intervalo_sucesso(self):
        """Testa iniciar intervalo com sucesso"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao = MagicMock(id=1)
        service.repo.obter_sessao_ativa.return_value = sessao
        service.repo.obter_intervalo_ativo.return_value = None
        
        sucesso, msg = service.iniciar_intervalo()
        assert sucesso is True
        assert "Intervalo iniciado" in msg
        service.repo.iniciar_intervalo.assert_called_once_with(sessao.id)

    def test_encerrar_intervalo_sem_sessao(self):
        """Testa encerrar intervalo sem sessão"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        service.repo.obter_sessao_ativa.return_value = None
        
        sucesso, msg = service.encerrar_intervalo()
        assert sucesso is False
        assert "Nenhuma sessão ativa" in msg

    def test_encerrar_intervalo_inexistente(self):
        """Testa encerrar intervalo quando não há intervalo ativo"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao = MagicMock(id=1)
        service.repo.obter_sessao_ativa.return_value = sessao
        service.repo.obter_intervalo_ativo.return_value = None
        
        sucesso, msg = service.encerrar_intervalo()
        assert sucesso is False
        assert "Nenhum intervalo ativo" in msg

    def test_encerrar_intervalo_sucesso(self):
        """Testa encerrar intervalo com sucesso"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        service.repo = MagicMock()
        sessao = MagicMock(id=1)
        service.repo.obter_sessao_ativa.return_value = sessao
        service.repo.obter_intervalo_ativo.return_value = MagicMock()
        
        sucesso, msg = service.encerrar_intervalo()
        assert sucesso is True
        assert "Intervalo encerrado" in msg
        service.repo.encerrar_intervalo.assert_called_once_with(sessao.id)

    def test_diferenca_efetiva(self):
        """Testa o cálculo da diferença efetiva de tempo descontando intervalos"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        
        t1 = datetime(2026, 3, 30, 19, 0, 0)
        t2 = datetime(2026, 3, 30, 22, 0, 0) # 3 horas = 10800 segundos
        
        # Intervalo de 19:30 até 20:00 (1800 segundos)
        i1 = MagicMock()
        i1.inicio = datetime(2026, 3, 30, 19, 30, 0)
        i1.fim = datetime(2026, 3, 30, 20, 0, 0)
        
        # Intervalo não encerrado (começa às 21:30, vai até t2)
        i2 = MagicMock()
        i2.inicio = datetime(2026, 3, 30, 21, 30, 0)
        i2.fim = None
        
        dif = service.diferenca_efetiva(t1, t2, [i1, i2])
        # 10800 - 1800 (i1) - 1800 (i2 de 21:30 a 22:00) = 7200 segundos
        assert dif == 7200

    def test_calcular_tempo_presente_aluno(self):
        """Testa o cálculo do tempo total de presença de um aluno na sessão"""
        mock_db = MagicMock()
        service = PresencaService(mock_db)
        
        sessao = MagicMock(id=1, fim=datetime(2026, 3, 30, 22, 0, 0))
        
        # Mocks de registros do aluno
        reg1 = MagicMock(tipo='entrada', timestamp=datetime(2026, 3, 30, 19, 0, 0))
        reg2 = MagicMock(tipo='saida', timestamp=datetime(2026, 3, 30, 20, 0, 0))
        reg3 = MagicMock(tipo='entrada', timestamp=datetime(2026, 3, 30, 21, 0, 0))
        # O aluno entrou de novo, mas não registrou saída antes do fim da sessão (será pareado com o fim da sessão)
        
        mock_db.query().filter().order_by().all.return_value = [reg1, reg2, reg3]
        
        # Sem intervalos
        service.diferenca_efetiva = MagicMock(side_effect=lambda start, end, intervals: int((end - start).total_seconds()))
        
        tempo = service.calcular_tempo_presente_aluno(10, sessao, [])
        # 19:00 a 20:00 (3600s) + 21:00 a 22:00 (3600s) = 7200 segundos
        assert tempo == 7200
