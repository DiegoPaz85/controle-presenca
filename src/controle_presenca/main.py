import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.services.presenca_service import PresencaService
from src.controle_presenca.services.sgdi_service import SGDiService

def limpar_tela():
    os.system('clear')

def executar_menu():
    while True:
        limpar_tela()
        print("="*55)
        print(" SISTEMA INTEGRADO EXPLICAASO")
        print("="*55)
        print("\n1. 📍 LEITOR DE PRESENÇA")
        print("2. 📊 SGDi (Gestor de Discentes)")
        print("3. 🚪 SAIR")
        
        opcao = input("\nEscolha: ").strip()
        
        match opcao:
            case '1':
                menu_leitor()
            case '2':
                menu_sgdi()
            case '3':
                print("\n👋 Encerrando o sistema...")
                break
            case _:
                print("\n❌ Opção inválida!")
                input("Pressione ENTER para tentar novamente...")

def menu_leitor():
    while True:
        limpar_tela()
        print("--- LEITOR DE PRESENÇA ---")
        print("1. Iniciar Sessão de Aula")
        print("2. Encerrar Sessão de Aula")
        print("3. Bater Ponto")
        print("4. Voltar")
        
        opt = input("\nEscolha: ").strip()
        
        match opt:
            case '1':
                with SessionLocal() as db:
                    svc = PresencaService(db)
                    if svc.repo.obter_sessao_ativa(): print("\n⚠️ Sessão já ativa!")
                    else: 
                        svc.repo.criar_sessao()
                        print("\n✅ Sessão iniciada!")
                input("\nENTER para voltar...")
            case '2':
                with SessionLocal() as db:
                    svc = PresencaService(db)
                    sess = svc.repo.obter_sessao_ativa()
                    if sess: 
                        svc.repo.encerrar_sessao(sess)
                        print("\n✅ Sessão encerrada!")
                    else: print("\n⚠️ Nenhuma sessão ativa.")
                input("\nENTER para voltar...")
            case '3':
                with SessionLocal() as db:
                    svc = PresencaService(db)
                    if not svc.repo.obter_sessao_ativa():
                        print("\n⚠️ Inicie a sessão primeiro!")
                        input("\nENTER para voltar...")
                        continue
                    print("\n[MODO LEITURA - Digite 'sair' para parar]")
                    while True:
                        c = input("Cartão: ").strip()
                        if c.lower() == 'sair': break
                        s, m = svc.processar_leitura(c)
                        print(f"✅ {m}" if s else f"❌ {m}")
            case '4':
                break

def menu_sgdi():
    while True:
        limpar_tela()
        print("--- SGDi (Gestor de Discentes) ---")
        print("1. Ver Ranking Socioeconômico")
        print("2. Aprovar Candidatos (Linha de Corte)")
        print("3. Efetivar Matrícula (Gerar Aluno)")
        print("4. Voltar")
        
        opt = input("\nEscolha: ").strip()
        
        match opt:
            case '1':
                with SessionLocal() as db:
                    svc = SGDiService(db)
                    ranking = svc.gerar_ranking()
                    print("\n--- RANKING PENDENTES ---")
                    for i, c in enumerate(ranking):
                        print(f"{i+1}º | {c.nome} | CPF: {c.cpf} | Pontos: {c.pontuacao_socioeconomica}")
                    if not ranking: print("Nenhum candidato pendente.")
                input("\nENTER para voltar...")
            case '2':
                qtd = input("\nAprovar quantos candidatos do topo do ranking? ")
                if qtd.isdigit():
                    with SessionLocal() as db:
                        svc = SGDiService(db)
                        n = svc.aprovar_corte(int(qtd))
                        print(f"\n✅ {n} candidatos aprovados com sucesso!")
                input("\nENTER para voltar...")
            case '3':
                cpf = input("\nDigite o CPF do candidato aprovado: ").strip()
                with SessionLocal() as db:
                    svc = SGDiService(db)
                    s, m = svc.matricular_candidato(cpf)
                    print(f"\n{m}")
                input("\nENTER para voltar...")
            case '4':
                break

if __name__ == "__main__":
    executar_menu()
