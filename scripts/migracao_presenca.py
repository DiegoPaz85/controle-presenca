import pandas as pd
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.database.models import Aluno, Sessao, Registro

def migrar_presencas(caminho_arquivo):
    print(f"📊 Lendo a planilha de presenças: {caminho_arquivo}")
    
    try:
        # Lê a planilha ignorando o cabeçalho
        df = pd.read_excel(caminho_arquivo, header=None, skiprows=1)
        
        with SessionLocal() as db:
            # 1. Cria uma Sessão específica para os dados antigos
            sessao_hist = Sessao(
                inicio=datetime.now(timezone.utc), 
                fim=datetime.now(timezone.utc), 
                status='encerrada' # Já nasce encerrada para não atrapalhar o sistema
            )
            db.add(sessao_hist)
            db.commit()
            
            inseridos = 0
            nao_encontrados = 0
            
            print(f"⏳ Processando {len(df)} registros antigos...")
            
            # 2. Varre a planilha linha por linha
            for index, row in df.iterrows():
                # A Coluna A (índice 0) é o ID do cartão
                cartao_id = pd.to_numeric(row[0], errors='coerce')
                
                if pd.isna(cartao_id):
                    continue
                    
                # Busca o aluno no nosso banco de dados novo
                aluno = db.query(Aluno).filter(Aluno.cartao_id == int(cartao_id)).first()
                
                if aluno:
                    # Registra a presença dele atrelada à Sessão Histórica
                    reg = Registro(
                        aluno_id=aluno.id, 
                        sessao_id=sessao_hist.id, 
                        tipo='entrada' # Conta como uma entrada válida
                    )
                    db.add(reg)
                    inseridos += 1
                else:
                    # Se o cartão não existir no banco novo (ex: aluno desistente), ele ignora
                    nao_encontrados += 1
            
            db.commit()
            print("\n🎉 HISTÓRICO DE PRESENÇAS MIGRADO COM SUCESSO!")
            print(f"📈 Presenças salvas no banco: {inseridos}")
            print(f"⚠️ Registros ignorados (alunos não cadastrados): {nao_encontrados}")

    except FileNotFoundError:
        print("❌ Arquivo Excel não encontrado. Verifique o caminho digitado.")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    print("="*55)
    print(" MÓDULO DE MIGRAÇÃO - HISTÓRICO DE PRESENÇAS")
    print("="*55)
    caminho = input("\nDigite o caminho exato do arquivo presenca.xlsx (ex: /app/presenca.xlsx): ").strip()
    migrar_presencas(caminho)
