import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'controle_presenca')
        self.user = os.getenv('DB_USER', 'presenca_user')
        self.password = os.getenv('DB_PASSWORD', 'presenca_pass')
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("✅ Conectado ao PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    @contextmanager
    def get_cursor(self):
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def execute(self, query, params=None):
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            return cursor.rowcount
    
    def close(self):
        if self.connection:
            self.connection.close()
            print("🔌 Conexão fechada")

db = Database()

