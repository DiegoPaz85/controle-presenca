import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.presenca_service import PresencaService
from cli.colors import *

class MenuPrincipal:
    def __init__(self):
        self.service = PresencaService()
        self.running = True
    
    def limpar_tela(self):
        os.system('clear')
    
    def executar(self):
        while self.running:
            self.limpar_tela()
            self._exibir_menu()
            opcao = input("\nEscolha: ").strip()
            self._processar(opcao)
    
    def _exibir_menu(self):
        status = self.service.get_status()
        
        print_header("CONTROLE DE PRESENÇA - ExpliCAASO")
        
        print_c(f"\n📊 Sessão: {'🟢 ATIVA' if status['sessao_ativa'] else '⚫ INATIVA'}")
        print_c(f"   Alunos presentes: {status['presentes']}")
        print_c(f"   Alunos ativos: {status['total_ativos']}")
        
        print_c("\n" + "-" * 50)
        print_c("1. 🎓 Área de Presenças", Colors.GREEN)
        print_c("2. 📊 Relatório de Presenças", Colors.GREEN)
        print_c("3. 🚪 Sair", Colors.RED)
        print_c("-" * 50)
    
    def _processar(self, opcao):
        if opcao == '1':
            self._area_presencas()
        elif opcao == '2':
            self._relatorio()
        elif opcao == '3':
            self.running = False
            print_c("\n👋 Até logo!", Colors.YELLOW)
        else:
            print_error("Opção inválida!")
            input("Pressione ENTER...")
    
    def _area_presencas(self):
        while True:
            self.limpar_tela()
            status = self.service.get_status()
            
            print_header("ÁREA DE PRESENÇAS")
            print_c(f"\nSessão: {'🟢 ATIVA' if status['sessao_ativa'] else '⚫ INATIVA'}")
            print_c(f"Presentes: {status['presentes']}\n")
            
            print_c("COMANDOS:")
            print_c("   • Digite a SENHA do cartão (ex: 1, 2, 3...)")
            print_c("   • 's' - Iniciar/Encerrar sessão")
            print_c("   • 'm' - Voltar ao menu principal")
            print_c("\n" + "-" * 50)
            
            comando = input("\n> ").strip().lower()
            
            if comando == 'm':
                break
            elif comando == 's':
                if status['sessao_ativa']:
                    sucesso, msg = self.service.encerrar_sessao()
                else:
                    sucesso, msg = self.service.iniciar_sessao()
                
                if sucesso:
                    print_success(msg)
                else:
                    print_error(msg)
                input("\nPressione ENTER...")
            else:
                sucesso, msg = self.service.registrar_cartao(comando)
                if sucesso:
                    print_success(msg)
                else:
                    print_error(msg)
                input("\nPressione ENTER...")
    
    def _relatorio(self):
        self.limpar_tela()
        print_header("RELATÓRIO DE PRESENÇAS")
        
        alunos = self.service.listar_alunos()
        
        if alunos:
            print_c(f"\n{'Nº':<5} {'Nome':<40} {'Status':<10} {'Horas':<10}")
            print_c("-" * 70)
            
            for aluno in alunos:
                horas = aluno['carga_horaria_total'] / 3600
                status_cor = Colors.GREEN if aluno['status'] == 'ATIVADO' else Colors.RED
                print_c(
                    f"{aluno['cartao_id']:<5} {aluno['nome'][:40]:<40} {aluno['status']:<10} {horas:.2f}h",
                    status_cor
                )
        else:
            print_info("Nenhum aluno cadastrado.")
        
        input("\nPressione ENTER para continuar...")
