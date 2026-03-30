import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tenta pegar a URL segura injetada pelo Docker. 
# Se não achar, usa um fallback padrão de desenvolvimento.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://explicaaso_user:explicaaso_pass@db:5432/explicaaso")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
