cat > Makefile << 'EOF'
.PHONY: install run test clean

install:
	@echo "Instalando dependências..."
	pip install -r requirements.txt
	@echo "✅ Instalação concluída!"

run:
	@echo "Iniciando sistema..."
	python src/controle_presenca/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Limpeza concluída!"

help:
	@echo "Comandos disponíveis:"
	@echo "  make install  - Instala dependências"
	@echo "  make run      - Executa o sistema"
	@echo "  make clean    - Limpa arquivos temporários"
EOF
