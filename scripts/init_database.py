import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.controle_presenca.database.connection import engine
from src.controle_presenca.database.models import Base

def inicializar_banco():
    """Cria todas as tabelas definidas nos modelos"""
    print("🔨 Criando estrutura do banco de dados...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        sys.exit(1)

if __name__ == "__main__":
    inicializar_banco()
