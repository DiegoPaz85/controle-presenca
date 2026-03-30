FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema e cria usuário seguro em uma única instrução RUN
RUN apt-get update && \
    apt-get install -y libpq-dev gcc netcat-openbsd && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Ajusta permissões em uma única instrução RUN
RUN chown -R appuser:appuser /app

USER appuser
