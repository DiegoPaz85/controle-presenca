import pytest
from unittest.mock import patch, MagicMock
from src.controle_presenca.utils.score_calculator import ScoreCalculator

def test_score_calculator_no_file():
    """Testa o comportamento do calculador quando a planilha não existe"""
    with patch('os.path.exists', return_value=False):
        # Limpa o cache estático para forçar recarregamento
        ScoreCalculator._criterios = None
        criterios = ScoreCalculator._carregar_criterios()
        assert criterios == {}

@patch('openpyxl.load_workbook')
def test_score_calculator_load_success(mock_load):
    """Testa o carregamento e parsing correto da planilha de critérios"""
    ScoreCalculator._criterios = None
    
    # Mock do workbook e planilha
    mock_wb = MagicMock()
    mock_sheet = MagicMock()
    mock_load.return_value = mock_wb
    mock_wb.active = mock_sheet
    
    # Simula o número de linhas
    mock_sheet.max_row = 6
    
    # Configura células do mock
    # Linha 3: Questão 10, Alternativa "Sim", 10 pontos
    # Linha 4: Questão 10 (None no col 1), Alternativa "Não", 0 pontos
    # Linha 5: Questão 11, Alternativa "Casado", 5 pontos
    # Linha 6: Questão 11 (None no col 1), Alternativa "Solteiro", 3 pontos
    cell_values = {
        (3, 1): 10.0, (3, 2): "Sim", (3, 3): 10.0,
        (4, 1): None, (4, 2): "Não", (4, 3): 0.0,
        (5, 1): 11.0, (5, 2): "Casado", (5, 3): 5.0,
        (6, 1): None, (6, 2): "Solteiro", (6, 3): 3.0,
    }
    
    def side_effect(row, column):
        cell = MagicMock()
        cell.value = cell_values.get((row, column), None)
        return cell
        
    mock_sheet.cell.side_effect = side_effect
    
    with patch('os.path.exists', return_value=True):
        criterios = ScoreCalculator._carregar_criterios()
        
        assert 10 in criterios
        assert criterios[10]["Sim"] == 10.0
        assert criterios[10]["Não"] == 0.0
        assert 11 in criterios
        assert criterios[11]["Casado"] == 5.0
        assert criterios[11]["Solteiro"] == 3.0

def test_calcular_score():
    """Testa o cálculo final com base nas alternativas fornecidas"""
    # Injeta um dicionário de critérios mockado diretamente no cache
    ScoreCalculator._criterios = {
        10: {"Sim": 10.0, "Não": 2.0},
        11: {"Opção A": 5.0, "Opção B": 0.0}
    }
    
    # Caso 1: Match exato
    respostas1 = {10: "Sim", 11: "Opção A"}
    assert ScoreCalculator.calcular_score(respostas1) == 15.0
    
    # Caso 2: Case-insensitive e espaços adicionais
    respostas2 = {10: "  sim ", 11: "opção b"}
    assert ScoreCalculator.calcular_score(respostas2) == 10.0
    
    # Caso 3: Resposta não existente no critério
    respostas3 = {10: "Inexistente", 11: None}
    assert ScoreCalculator.calcular_score(respostas3) == 0.0
