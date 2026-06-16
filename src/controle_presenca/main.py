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
        _, msg = svc.iniciar_sessao()
        print(f"\n{msg}")
    _pausar()

def encerrar_sessao_aula():
    with SessionLocal() as db:
        svc = PresencaService(db)
        _, msg = svc.encerrar_sessao()
        print(f"\n{msg}")
    _pausar()

def iniciar_intervalo_aula():
    with SessionLocal() as db:
        svc = PresencaService(db)
        _, msg = svc.iniciar_intervalo()
        print(f"\n{msg}")
    _pausar()

def encerrar_intervalo_aula():
    with SessionLocal() as db:
        svc = PresencaService(db)
        _, msg = svc.encerrar_intervalo()
        print(f"\n{msg}")
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
            try:
                n_aprovados = svc.aprovar_corte(int(qtd))
                print(f"\n✅ {n_aprovados} candidatos aprovados com sucesso!")
            except ValueError as e:
                print(f"\n❌ Erro: {e}")
    _pausar()

def efetivar_matricula_sgdi():
    cpf = input("\nDigite o CPF do candidato aprovado: ").strip()
    with SessionLocal() as db:
        svc = SGDiService(db)
        _, msg = svc.matricular_candidato(cpf)
        print(f"\n{msg}")
    _pausar()

def importar_candidatos_planilha_cli():
    caminho = input("\nDigite o caminho da planilha de respostas (.xlsx): ").strip()
    if not os.path.exists(caminho):
        print("\n❌ Arquivo não encontrado.")
        _pausar()
        return
    with SessionLocal() as db:
        svc = SGDiService(db)
        inseridos, erros = svc.importar_candidatos_planilha(caminho)
        print(f"\n✅ Importação concluída! {inseridos} candidatos importados, {erros} erros/duplicados.")
    _pausar()

def pesquisar_candidato_aluno_cli():
    termo = input("\nDigite o Nome, CPF ou ID do cartão para busca: ").strip()
    with SessionLocal() as db:
        svc = SGDiService(db)
        cands = svc.pesquisar_candidatos(termo)
        alunos = svc.pesquisar_alunos(termo)
        
        print("\n--- CANDIDATOS ENCONTRADOS ---")
        for c in cands:
            print(f"ID: {c.id} | {c.nome} | CPF: {c.cpf} | Status: {c.status}")
        if not cands:
            print("Nenhum candidato encontrado.")
            
        print("\n--- ALUNOS ENCONTRADOS ---")
        for a in alunos:
            print(f"ID: {a.id} | {a.nome} | Cartão: {a.cartao_id} | Status: {a.status}")
        if not alunos:
            print("Nenhum aluno encontrado.")
    _pausar()

def remover_candidato_aluno_cli():
    print("\n1. Excluir Candidato")
    print("2. Desativar Aluno (Exclusão Lógica)")
    op = input(MSG_ESCOLHA).strip()
    
    with SessionLocal() as db:
        svc = SGDiService(db)
        if op == '1':
            cid = input("ID do Candidato: ").strip()
            if cid.isdigit():
                _, msg = svc.excluir_candidato(int(cid))
                print(f"\n{msg}")
            else:
                print("\n❌ ID inválido.")
        elif op == '2':
            aid = input("ID do Aluno: ").strip()
            if aid.isdigit():
                _, msg = svc.desativar_aluno(int(aid))
                print(f"\n{msg}")
            else:
                print("\n❌ ID inválido.")
    _pausar()

def menu_leitor():
    while True:
        limpar_tela()
        print("--- LEITOR DE PRESENÇA ---")
        print("1. Iniciar Sessão de Aula")
        print("2. Encerrar Sessão de Aula")
        print("3. Iniciar Intervalo")
        print("4. Encerrar Intervalo")
        print("5. Bater Ponto")
        print("6. Voltar")
        
        opcao = input(MSG_ESCOLHA).strip()
        
        match opcao:
            case '1': iniciar_sessao_aula()
            case '2': encerrar_sessao_aula()
            case '3': iniciar_intervalo_aula()
            case '4': encerrar_intervalo_aula()
            case '5': bater_ponto()
            case '6': break

def menu_sgdi():
    while True:
        limpar_tela()
        print("--- SGDi (Gestor de Discentes) ---")
        print("1. Ver Ranking Socioeconômico")
        print("2. Aprovar Candidatos (Linha de Corte)")
        print("3. Efetivar Matrícula (Gerar Aluno)")
        print("4. Importar Candidatos de Planilha")
        print("5. Pesquisar Candidato ou Aluno")
        print("6. Excluir Candidato / Desativar Aluno")
        print("7. Voltar")
        
        opcao = input(MSG_ESCOLHA).strip()
        
        match opcao:
            case '1': exibir_ranking_sgdi()
            case '2': aprovar_candidatos_sgdi()
            case '3': efetivar_matricula_sgdi()
            case '4': importar_candidatos_planilha_cli()
            case '5': pesquisar_candidato_aluno_cli()
            case '6': remover_candidato_aluno_cli()
            case '7': break

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
