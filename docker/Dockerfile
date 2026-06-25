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

# Define o usuário seguro
USER appuser

# Expõe a porta que a API vai usar
EXPOSE 8000

# Comando padrão de inicialização (versão de produção)
CMD ["uvicorn", "src.controle_presenca.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
