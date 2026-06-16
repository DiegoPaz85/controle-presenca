import pytest
from unittest.mock import MagicMock, patch

try:
    from controle_presenca.services.sgdi_service import SGDiService
    from controle_presenca.database.models import Aluno, Candidato
except ImportError:
    pytest.skip("SGDiService não disponível", allow_module_level=True)

def test_sgdi_service_initialization():
    """Testa inicialização do serviço SGDi"""
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    
    assert service is not None
    assert service.db == mock_db

def test_sgdi_service_gerar_ranking():
    """Testa geração de ranking de candidatos"""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    mock_order = MagicMock()
    mock_filter.order_by.return_value = mock_order
    mock_limit = MagicMock()
    mock_order.limit.return_value = mock_limit
    mock_candidatos = [MagicMock(), MagicMock()]
    mock_limit.all.return_value = mock_candidatos
    
    service = SGDiService(mock_db)
    resultado = service.gerar_ranking(limite=10)
    
    assert resultado == mock_candidatos
    mock_db.query.assert_called_once()

def test_sgdi_service_aprovar_corte_sucesso():
    """Testa aprovação de candidatos por corte dentro do limite"""
    mock_db = MagicMock()
    mock_db.query().filter().count.return_value = 10  # 10 ativos
    
    service = SGDiService(mock_db)
    
    mock_candidato1 = MagicMock()
    mock_candidato2 = MagicMock()
    mock_candidato1.status = 'pendente'
    mock_candidato2.status = 'pendente'
    service.gerar_ranking = MagicMock(return_value=[mock_candidato1, mock_candidato2])
    
    resultado = service.aprovar_corte(quantidade=2)
    
    assert resultado == 2
    assert mock_candidato1.status == 'aprovado'
    assert mock_candidato2.status == 'aprovado'
    mock_db.commit.assert_called_once()

def test_sgdi_service_aprovar_corte_excedendo_limite():
    """Testa se aprovar_corte levanta erro se exceder 60"""
    mock_db = MagicMock()
    mock_db.query().filter().count.return_value = 59  # 59 ativos
    
    service = SGDiService(mock_db)
    
    with pytest.raises(ValueError) as exc:
        service.aprovar_corte(quantidade=2)
        
    assert "excede o limite máximo de 60" in str(exc.value)

def test_sgdi_service_matricular_candidato_sucesso():
    """Testa matrícula de candidato aprovado"""
    mock_db = MagicMock()
    mock_candidato = MagicMock()
    mock_candidato.status = 'aprovado'
    mock_candidato.nome = 'JOAO SILVA'
    mock_db.query().filter().first.return_value = mock_candidato
    
    service = SGDiService(mock_db)
    sucesso, mensagem = service.matricular_candidato(cpf='12345678900')
    
    assert sucesso is True
    assert 'confirmada' in mensagem
    assert 'JOAO SILVA' in mensagem
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()

def test_sgdi_service_matricular_candidato_nao_encontrado():
    """Testa matrícula de candidato não encontrado"""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    service = SGDiService(mock_db)
    sucesso, mensagem = service.matricular_candidato(cpf='12345678900')
    
    assert sucesso is False
    assert 'não encontrado' in mensagem.lower()
    mock_db.add.assert_not_called()

def test_sgdi_service_matricular_candidato_nao_aprovado():
    """Testa matrícula de candidato não aprovado"""
    mock_db = MagicMock()
    mock_candidato = MagicMock()
    mock_candidato.status = 'pendente'
    mock_db.query().filter().first.return_value = mock_candidato
    
    service = SGDiService(mock_db)
    sucesso, mensagem = service.matricular_candidato(cpf='12345678900')
    
    assert sucesso is False
    assert 'não está aprovado' in mensagem.lower()
    mock_db.add.assert_not_called()

def test_cadastrar_candidato_cpf_invalido():
    """Testa cadastro com CPF com tamanho incorreto"""
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    
    sucesso, msg = service.cadastrar_candidato("Joao", "123", "joao@email.com")
    assert sucesso is False
    assert "CPF inválido" in msg

def test_cadastrar_candidato_duplicado():
    """Testa cadastro de candidato com CPF já cadastrado"""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = MagicMock() # Candidato existente
    
    service = SGDiService(mock_db)
    sucesso, msg = service.cadastrar_candidato("Joao", "123.456.789-00", "joao@email.com")
    assert sucesso is False
    assert "já cadastrado" in msg

def test_cadastrar_candidato_sucesso():
    """Testa cadastro de candidato com sucesso e pontuação calculada"""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    service = SGDiService(mock_db)
    
    with patch('controle_presenca.utils.score_calculator.ScoreCalculator.calcular_score', return_value=15.5) as mock_calc:
        sucesso, msg = service.cadastrar_candidato(
            nome="Joao Silva  ",
            cpf="123.456.789-00",
            email="joao@email.com",
            respostas={10: "Sim"}
        )
        assert sucesso is True
        assert "cadastrado com sucesso" in msg
        mock_calc.assert_called_once_with({10: "Sim"})
        assert mock_db.add.call_count == 2
        mock_db.commit.assert_called_once()

def test_pesquisar_candidatos_por_nome():
    """Testa busca de candidatos por nome"""
    mock_db = MagicMock()
    mock_cands = [MagicMock()]
    mock_db.query().filter().all.return_value = mock_cands
    
    service = SGDiService(mock_db)
    res = service.pesquisar_candidatos("Joao")
    assert res == mock_cands

def test_pesquisar_candidatos_por_cpf():
    """Testa busca de candidatos por CPF"""
    mock_db = MagicMock()
    mock_cands = [MagicMock()]
    mock_db.query().filter().all.return_value = mock_cands
    
    service = SGDiService(mock_db)
    res = service.pesquisar_candidatos("123.456.789-00")
    assert res == mock_cands

def test_excluir_candidato_inexistente():
    """Testa exclusão de candidato inexistente"""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    service = SGDiService(mock_db)
    sucesso, msg = service.excluir_candidato(99)
    assert sucesso is False
    assert "não encontrado" in msg

def test_excluir_candidato_sucesso():
    """Testa exclusão de candidato existente com sucesso"""
    mock_db = MagicMock()
    mock_cand = MagicMock()
    mock_db.query().filter().first.return_value = mock_cand
    
    service = SGDiService(mock_db)
    sucesso, msg = service.excluir_candidato(1)
    assert sucesso is True
    assert "excluído com sucesso" in msg
    mock_db.delete.assert_called_once_with(mock_cand)
    mock_db.commit.assert_called_once()

def test_pesquisar_alunos():
    """Testa busca de alunos por nome e cartao_id"""
    mock_db = MagicMock()
    mock_db.query().filter().all.return_value = [MagicMock()]
    
    service = SGDiService(mock_db)
    res1 = service.pesquisar_alunos("Joao")
    assert len(res1) == 1
    
    res2 = service.pesquisar_alunos("123456")
    assert len(res2) == 1

def test_desativar_aluno_inexistente():
    """Testa desativação de aluno inexistente"""
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None
    
    service = SGDiService(mock_db)
    sucesso, msg = service.desativar_aluno(99)
    assert sucesso is False
    assert "não encontrado" in msg

def test_desativar_aluno_sucesso():
    """Testa desativação (exclusão lógica) de aluno existente com sucesso"""
    mock_db = MagicMock()
    mock_aluno = MagicMock()
    mock_aluno.status = 'ATIVADO'
    mock_db.query().filter().first.return_value = mock_aluno
    
    service = SGDiService(mock_db)
    sucesso, msg = service.desativar_aluno(1)
    assert sucesso is True
    assert "desativado com sucesso" in msg
    assert mock_aluno.status == 'DESATIVADO'
    mock_db.commit.assert_called_once()

@patch('openpyxl.load_workbook')
def test_importar_candidatos_planilha(mock_load):
    """Testa importação de candidatos a partir de planilha"""
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    
    # Mocks do openpyxl
    mock_wb = MagicMock()
    mock_sheet = MagicMock()
    mock_load.return_value = mock_wb
    mock_wb.active = mock_sheet
    
    mock_sheet.max_row = 2
    
    # Células da linha 2
    # E=5 (Nome), D=4 (Email), I=9 (CPF), K=11 (Q10)...
    cell_values = {
        (2, 5): "Candidato Importado",
        (2, 4): "importado@email.com",
        (2, 9): "98765432100",
        (2, 11): "Opção A"
    }
    
    def side_effect(row, column):
        cell = MagicMock()
        cell.value = cell_values.get((row, column), None)
        return cell
    mock_sheet.cell.side_effect = side_effect
    
    # Mock do cadastrar_candidato
    service.cadastrar_candidato = MagicMock(return_value=(True, ""))
    
    inseridos, erros = service.importar_candidatos_planilha("fake_path.xlsx")
    
    assert inseridos == 1
    assert erros == 0
    service.cadastrar_candidato.assert_called_once()
    mock_wb.close.assert_called_once()

def test_sgdi_service_obter_historico_candidato():
    """Testa obtenção do histórico de status de um candidato"""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    mock_order = MagicMock()
    mock_filter.order_by.return_value = mock_order
    
    mock_historico = [MagicMock(), MagicMock()]
    mock_order.all.return_value = mock_historico
    
    service = SGDiService(mock_db)
    res = service.obter_historico_candidato(candidato_id=1)
    
    assert res == mock_historico
    mock_db.query.assert_called_once()

@patch('controle_presenca.utils.google_drive.GoogleDriveDownloader.baixar_planilha_forms')
def test_sgdi_service_sincronizar_importacao_drive_sucesso(mock_baixar):
    """Testa sincronização e importação do Google Drive com sucesso"""
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    service.importar_candidatos_planilha = MagicMock(return_value=(5, 0))
    
    sucesso, mensagem = service.sincronizar_importacao_drive()
    
    assert sucesso is True
    assert "Sincronização concluída" in mensagem
    assert "5 candidatos importados" in mensagem
    mock_baixar.assert_called_once_with("temp_drive_import.xlsx")
    service.importar_candidatos_planilha.assert_called_once_with("temp_drive_import.xlsx")

@patch('controle_presenca.utils.google_drive.GoogleDriveDownloader.baixar_planilha_forms')
def test_sgdi_service_sincronizar_importacao_drive_erro(mock_baixar):
    """Testa falha ao sincronizar com Google Drive"""
    mock_db = MagicMock()
    service = SGDiService(mock_db)
    mock_baixar.side_effect = Exception("Erro na API do Drive")
    
    sucesso, mensagem = service.sincronizar_importacao_drive()
    
    assert sucesso is False
    assert "Erro na sincronização" in mensagem
    assert "Erro na API do Drive" in mensagem

