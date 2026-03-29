import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from controle_presenca.cli.colors import Colors, print_c, print_success, print_error, print_warning, print_info, print_header

class TestColors:
    
    def test_colors_constants(self):
        """Testa as constantes de cores"""
        assert Colors.RESET == '\033[0m'
        assert Colors.RED == '\033[91m'
        assert Colors.GREEN == '\033[92m'
        assert Colors.YELLOW == '\033[93m'
        assert Colors.CYAN == '\033[96m'
        assert Colors.WHITE == '\033[97m'
    
    def test_print_c(self, capsys):
        """Testa função print_c"""
        print_c("teste", Colors.RED)
        captured = capsys.readouterr()
        assert "\033[91mteste\033[0m" in captured.out
    
    def test_print_success(self, capsys):
        """Testa print_success"""
        print_success("Sucesso!")
        captured = capsys.readouterr()
        assert "✅ Sucesso!" in captured.out
    
    def test_print_error(self, capsys):
        """Testa print_error"""
        print_error("Erro!")
        captured = capsys.readouterr()
        assert "❌ Erro!" in captured.out
    
    def test_print_warning(self, capsys):
        """Testa print_warning"""
        print_warning("Aviso!")
        captured = capsys.readouterr()
        assert "⚠️  Aviso!" in captured.out
    
    def test_print_info(self, capsys):
        """Testa print_info"""
        print_info("Info!")
        captured = capsys.readouterr()
        assert "ℹ️  Info!" in captured.out
    
    def test_print_header(self, capsys):
        """Testa print_header"""
        print_header("Titulo")
        captured = capsys.readouterr()
        assert "Titulo" in captured.out
        assert "=" in captured.out
