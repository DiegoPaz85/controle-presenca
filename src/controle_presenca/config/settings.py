import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # A URL completa já vem do Docker/.env. Sem senhas isoladas no código!
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Configurações gerais da aplicação
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()
