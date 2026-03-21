#!/usr/bin/env python
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from database.models import criar_tabelas, inserir_dados_iniciais
from cli.menu import MenuPrincipal
from cli.colors import print_c, Colors, print_error

def main():
    print_c("🚀 Iniciando Sistema de Controle de Presença...", Colors.CYAN)
    
    # Conectar ao banco
    if not db.connect():
        print_error("Não foi possível conectar ao PostgreSQL!")
        print_c("\nCertifique-se que o PostgreSQL está rodando:", Colors.YELLOW)
        print_c("  sudo service postgresql start", Colors.WHITE)
        sys.exit(1)
    
    # Criar tabelas e dados iniciais
    criar_tabelas()
    inserir_dados_iniciais()
    
    # Iniciar menu
    menu = MenuPrincipal()
    menu.executar()
    
    # Fechar conexão
    db.close()

if __name__ == "__main__":
    main()
