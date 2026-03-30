import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Lemos estritamente da variável de ambiente. Sem senhas de fallback no código!
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("⚠️ DATABASE_URL não encontrada! Verifique o arquivo .env ou as variáveis de ambiente.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
