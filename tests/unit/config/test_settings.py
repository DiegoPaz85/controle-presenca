import pytest
import os
from unittest.mock import patch
import sys
sys.path.insert(0, '/app/src')

def test_settings_import():
    """Testa se o módulo de configurações pode ser importado"""
    from controle_presenca.config import settings
    assert settings is not None

def test_settings_has_database_url():
    """Testa se o settings tem DATABASE_URL"""
    from controle_presenca.config.settings import settings
    
    # Verifica se DATABASE_URL existe (pode ser None se não estiver no .env)
    assert hasattr(settings, 'DATABASE_URL')
    # Em ambiente de teste, pode ser None, mas o atributo existe

def test_settings_has_debug_flag():
    """Testa se o settings tem a flag DEBUG"""
    from controle_presenca.config.settings import settings
    
    assert hasattr(settings, 'DEBUG')
    assert isinstance(settings.DEBUG, bool)

def test_settings_has_log_level():
    """Testa se o settings tem LOG_LEVEL"""
    from controle_presenca.config.settings import settings
    
    assert hasattr(settings, 'LOG_LEVEL')
    assert isinstance(settings.LOG_LEVEL, str)

def test_settings_debug_default():
    """Testa se DEBUG default é False quando não definido"""
    with patch.dict(os.environ, {}, clear=True):
        import importlib
        import controle_presenca.config.settings
        importlib.reload(controle_presenca.config.settings)
        
        from controle_presenca.config.settings import settings
        assert settings.DEBUG is False

def test_settings_debug_true():
    """Testa se DEBUG é True quando definido"""
    with patch.dict(os.environ, {'DEBUG': 'true'}):
        import importlib
        import controle_presenca.config.settings
        importlib.reload(controle_presenca.config.settings)
        
        from controle_presenca.config.settings import settings
        assert settings.DEBUG is True

def test_settings_load_database_url_from_env():
    """Testa se DATABASE_URL carrega do ambiente"""
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:pass@localhost:5432/testdb'}):
        import importlib
        import controle_presenca.config.settings
        importlib.reload(controle_presenca.config.settings)
        
        from controle_presenca.config.settings import settings
        assert settings.DATABASE_URL == 'postgresql://test:pass@localhost:5432/testdb'
