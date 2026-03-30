import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.controle_presenca.database.connection import SessionLocal
from src.controle_presenca.database.models import Aluno

def realizar_migracao(caminho_arquivo):
    print(f"📊 Lendo a planilha: {caminho_arquivo}")
    
    try:
        df = pd.read_excel(caminho_arquivo, usecols="B,E,AP", header=None, skiprows=1)
        df.columns = ['status_texto_longo', 'nome', 'cartao_id']
        
        # Remove linhas onde o nome ou o cartão estão vazios
        df = df.dropna(subset=['nome', 'cartao_id'])
        
        # Converte o cartão para inteiro
        df['cartao_id'] = pd.to_numeric(df['cartao_id'], errors='coerce').fillna(0).astype(int)
        df = df[df['cartao_id'] > 0]
        
        print(f"✅ Encontrados {len(df)} registros válidos. Iniciando injeção no Banco de Dados...")
        
        with SessionLocal() as db:
            inseridos = 0
            atualizados = 0
            
            for index, row in df.iterrows():
                aluno_bd = db.query(Aluno).filter(Aluno.cartao_id == row['cartao_id']).first()
                
                nome_limpo = str(row['nome']).strip()
                # IGNORAMOS O TEXTO DO EXCEL E FORÇAMOS COMO ATIVADO
                status_limpo = 'ATIVADO'
                
                if aluno_bd:
                    aluno_bd.nome = nome_limpo
                    aluno_bd.status = status_limpo
                    atualizados += 1
                else:
                    novo_aluno = Aluno(cartao_id=row['cartao_id'], nome=nome_limpo, status=status_limpo)
                    db.add(novo_aluno)
                    inseridos += 1
                    
            db.commit()
            print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"📈 Alunos novos inseridos: {inseridos}")
            print(f"🔄 Alunos já existentes atualizados: {atualizados}")

    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    print("="*50)
    print(" MÓDULO DE MIGRAÇÃO - EXCEL PARA POSTGRESQL")
    print("="*50)
    caminho = input("\nDigite o caminho exato do arquivo BancoDeDados.xlsx (ex: /app/BancoDeDados.xlsx): ").strip()
    realizar_migracao(caminho)
