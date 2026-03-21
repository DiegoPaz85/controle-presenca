import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'controle_presenca')
    DB_USER = os.getenv('DB_USER', 'presenca_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'presenca_pass')
    
    GOOGLE_CREDENTIALS = Path(os.getenv('GOOGLE_CREDENTIALS', BASE_DIR / 'credentials/service_account.json'))
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    SYNC_ENABLED = os.getenv('SYNC_ENABLED', 'false').lower() == 'true'
    
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    LOCAL_RETENTION_DAYS = int(os.getenv('LOCAL_RETENTION_DAYS', '7'))
    BACKUP_SCHEDULE = os.getenv('BACKUP_SCHEDULE', '23:00')
    
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
