FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema necessárias para o banco (psycopg2) e para o nc (netcat)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copia as dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Impede o Python de gerar arquivos inúteis (.pyc)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expõe a porta do FastAPI
EXPOSE 8000

# Executa o script de inicialização via bash para evitar problemas de permissão
CMD ["bash", "/app/scripts/entrypoint.sh"]
