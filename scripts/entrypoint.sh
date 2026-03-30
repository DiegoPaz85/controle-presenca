#!/bin/bash

echo "⏳ Aguardando o banco de dados..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "✅ Banco de dados pronto!"

echo "📊 Criando tabelas no banco de dados..."
# Cria as tabelas diretamente via código Python (ideal para essa fase inicial)
python -c "from src.controle_presenca.database.connection import engine; from src.controle_presenca.database.models import Base; Base.metadata.create_all(bind=engine)"

echo "🚀 Iniciando API..."
# Usa o 'python -m' para garantir que ele ache o uvicorn onde quer que esteja instalado
exec python -m uvicorn src.controle_presenca.api.main:app --host 0.0.0.0 --port 8000 --reload
