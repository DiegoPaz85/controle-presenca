import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_import_colors():
    """Teste de importação do módulo colors"""
    from controle_presenca.cli.colors import Colors
    assert Colors.RED == '\033[91m'
    assert Colors.GREEN == '\033[92m'
    assert Colors.RESET == '\033[0m'
    print("✅ Colors importado com sucesso!")

def test_import_settings():
    """Teste de importação do módulo settings"""
    from controle_presenca.config.settings import settings
    assert settings is not None
    print("✅ Settings importado com sucesso!")

def test_import_database():
    """Teste de importação do módulo database"""
    from controle_presenca.database.connection import db
    assert db is not None
    print("✅ Database importado com sucesso!")

def test_import_models():
    """Teste de importação do módulo models"""
    from controle_presenca.database.models import criar_tabelas
    assert criar_tabelas is not None
    print("✅ Models importado com sucesso!")
