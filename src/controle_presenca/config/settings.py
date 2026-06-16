import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # A URL completa já vem do Docker/.env. Sem senhas isoladas no código!
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Configurações gerais da aplicação
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Configurações SMTP
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465")) if os.getenv("SMTP_PORT") else 465
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    # Configurações Google Drive
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "1vg-QF86GNfO_1gS7KtIhrIDGwGuxtnIG")
    GOOGLE_DRIVE_FILE_NAME = os.getenv("GOOGLE_DRIVE_FILE_NAME", "Formulário de inscrição ExpliCAASO-2026 (respostas)")
    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json"))

settings = Settings()

