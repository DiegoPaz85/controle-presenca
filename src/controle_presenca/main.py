import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.services.presenca_service import PresencaService
from src.controle_presenca.services.sgdi_service import SGDiService

# Constantes para evitar duplicação de Strings (Exigência do SonarCloud)
MSG_ESCOLHA = "\nEscolha: "
MSG_VOLTAR = "\nENTER para voltar..."

def limpar_tela():
    os.system('clear')

def _pausar():
    input(MSG_VOLTAR)

def iniciar_sessao_aula():
    with SessionLocal() as db:
        svc = PresencaService(db)
        if svc.repo.obter_sessao_ativa():
            print("\n⚠️ Sessão já ativa!")
        else:
            svc.repo.criar_sessao()
            print("\n✅ Sessão iniciada!")
    _pausar()

def encerrar_sessao_aula():
    with SessionLocal() as db:
        svc = PresencaService(db)
        sessao = svc.repo.obter_sessao_ativa()
        if sessao:
            svc.repo.encerrar_sessao(sessao)
            print("\n✅ Sessão encerrada!")
        else:
            print("\n⚠️ Nenhuma sessão ativa.")
    _pausar()

def bater_ponto():
    with SessionLocal() as db:
        svc = PresencaService(db)
        if not svc.repo.obter_sessao_ativa():
            print("\n⚠️ Inicie a sessão primeiro!")
            _pausar()
            return
            
        print("\n[MODO LEITURA - Digite 'sair' para parar]")
        while True:
            cartao = input("Cartão: ").strip()
            if cartao.lower() == 'sair':
                break
            sucesso, msg = svc.processar_leitura(cartao)
            print(f"✅ {msg}" if sucesso else f"❌ {msg}")

def exibir_ranking_sgdi():
    with SessionLocal() as db:
        svc = SGDiService(db)
        ranking = svc.gerar_ranking()
        print("\n--- RANKING PENDENTES ---")
        for i, c in enumerate(ranking):
            print(f"{i+1}º | {c.nome} | CPF: {c.cpf} | Pontos: {c.pontuacao_socioeconomica}")
        if not ranking:
            print("Nenhum candidato pendente.")
    _pausar()

def aprovar_candidatos_sgdi():
    qtd = input("\nAprovar quantos candidatos do topo do ranking? ")
    if qtd.isdigit():
        with SessionLocal() as db:
            svc = SGDiService(db)
            n_aprovados = svc.aprovar_corte(int(qtd))
            print(f"\n✅ {n_aprovados} candidatos aprovados com sucesso!")
    _pausar()

def efetivar_matricula_sgdi():
    cpf = input("\nDigite o CPF do candidato aprovado: ").strip()
    with SessionLocal() as db:
        svc = SGDiService(db)
        _, msg = svc.matricular_candidato(cpf)
        print(f"\n{msg}")
    _pausar()

def menu_leitor():
    while True:
        limpar_tela()
        print("--- LEITOR DE PRESENÇA ---")
        print("1. Iniciar Sessão de Aula")
        print("2. Encerrar Sessão de Aula")
        print("3. Bater Ponto")
        print("4. Voltar")
        
        opcao = input(MSG_ESCOLHA).strip()
        
        match opcao:
            case '1': iniciar_sessao_aula()
            case '2': encerrar_sessao_aula()
            case '3': bater_ponto()
            case '4': break

def menu_sgdi():
    while True:
        limpar_tela()
        print("--- SGDi (Gestor de Discentes) ---")
        print("1. Ver Ranking Socioeconômico")
        print("2. Aprovar Candidatos (Linha de Corte)")
        print("3. Efetivar Matrícula (Gerar Aluno)")
        print("4. Voltar")
        
        opcao = input(MSG_ESCOLHA).strip()
        
        match opcao:
            case '1': exibir_ranking_sgdi()
            case '2': aprovar_candidatos_sgdi()
            case '3': efetivar_matricula_sgdi()
            case '4': break

def executar_menu():
    while True:
        limpar_tela()
        print("="*55)
        print(" SISTEMA INTEGRADO EXPLICAASO")
        print("="*55)
        print("\n1. 📍 LEITOR DE PRESENÇA")
        print("2. 📊 SGDi (Gestor de Discentes)")
        print("3. 🚪 SAIR")
        
        opcao = input(MSG_ESCOLHA).strip()
        
        match opcao:
            case '1': menu_leitor()
            case '2': menu_sgdi()
            case '3':
                print("\n👋 Encerrando o sistema...")
                break
            case _:
                print("\n❌ Opção inválida!")
                input("Pressione ENTER para tentar novamente...")

if __name__ == "__main__":
    executar_menu()
