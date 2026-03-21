#!/bin/bash
set -e

echo "🚀 Instalando Sistema..."

# Verificar Python
if ! command -v python3 &>/dev/null; then
  sudo apt update
  sudo apt install python3 python3-pip python3-venv -y
fi

# Verificar PostgreSQL
if ! command -v psql &>/dev/null; then
  sudo apt install postgresql postgresql-contrib -y
  sudo systemctl start postgresql
fi

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Criar .env
if [ ! -f .env ]; then
  cp .env.example .env
fi

# Configurar PostgreSQL
sudo -u postgres psql <<EOF
CREATE USER IF NOT EXISTS presenca_user WITH PASSWORD 'presenca_pass';
CREATE DATABASE IF NOT EXISTS controle_presenca OWNER presenca_user;
GRANT ALL PRIVILEGES ON DATABASE controle_presenca TO presenca_user;
EOF

echo ""
echo "✅ Instalação concluída!"
echo "Para iniciar: source venv/bin/activate && python src/controle_presenca/main.py"
