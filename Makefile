.PHONY: install clean setup-db up logs down

install:
	@echo "Instalando dependências localmente..."
	pip install -r requirements.txt
	@echo "✅ Instalação concluída!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Limpeza concluída!"

setup-db:
	@echo "🔄 Atualizando tabelas no banco de dados..."
	sudo docker exec explicaaso_app alembic upgrade head
	@echo "📝 Injetando gabarito de notas..."
	sudo docker exec explicaaso_app python scripts/popular_gabarito.py
	@echo "✅ Banco de dados pronto para produção!"

up:
	@echo "🐳 Construindo e subindo os contêineres do Docker em segundo plano..."
	sudo docker compose -f docker/docker-compose.yml up -d --build
	@echo "⏳ Aguardando 5 segundos para o banco iniciar..."
	@sleep 30
	@make setup-db
	@echo "🚀 Sistema ExpliCAASO rodando com segurança! Use 'make logs' para ver as atividades."

logs:
	@echo "📋 Exibindo os logs da aplicação (Pressione Ctrl+C para sair da tela, o sistema continuará rodando!)..."
	sudo docker logs -f explicaaso_app

down:
	@echo "🛑 Desligando o sistema e o banco de dados..."
	sudo docker compose -f docker/docker-compose.yml down
