FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y libpq-dev gcc netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Cria um usuário sem privilégios de root para segurança (Exigência SonarCloud)
RUN useradd -m appuser

# Instala pacotes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto e dá permissão ao novo usuário
COPY . .
RUN chown -R appuser:appuser /app

# Define o usuário seguro como o dono do processo
USER appuser
