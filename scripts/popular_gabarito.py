import sys
import os

# Garante que o Python encontra a sua pasta src, não importa de onde o script seja rodado
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controle_presenca.database.connection import SessionLocal
import src.controle_presenca.database.models as models

# Aqui está o dicionário completo estruturado para o banco de dados
TABELA_PONTUACAO = {
    "Onde você cursou a maior parte do Ensino Fundamental (1º ao 9º ano)?": {
        "Apenas em escola pública": 10.0,
        "A maior parte em escola pública": 8.0,
        "Metade em escola pública e metade em escola particular (com bolsa)": 6.0,
        "Apenas em escola particular (com bolsa)": 4.0,
        "A maior parte em escola particular (sem bolsa)": 0.0,
        "Apenas em escola particular (sem bolsa)": 0.0
    },
    "Onde você cursou/cursa o Ensino Médio?": {
        "Apenas em escola pública": 10.0,
        "A maior parte em escola pública": 8.0,
        "Metade em escola pública e metade em escola particular (com bolsa)": 6.0,
        "Apenas em escola particular (com bolsa)": 4.0,
        "A maior parte em escola particular (sem bolsa)": 0.0,
        "Apenas em escola particular (sem bolsa)": 0.0
    },
    "Qual é a sua situação de trabalho atual?": {
        "Desempregado(a) e procurando emprego": 10.0,
        "Trabalho informal / Bico": 8.0,
        "Trabalho formal (com carteira assinada)": 4.0,
        "Estagiário(a) / Jovem Aprendiz": 4.0,
        "Não trabalho e não estou procurando": 0.0
    },
    "Qual é a renda bruta mensal da sua família (soma do salário de todos)?": {
        "Até 1 salário mínimo": 10.0,
        "De 1 a 2 salários mínimos": 8.0,
        "De 2 a 3 salários mínimos": 6.0,
        "De 3 a 4 salários mínimos": 4.0,
        "De 4 a 5 salários mínimos": 2.0,
        "Mais de 5 salários mínimos": 0.0
    },
    "Quantas pessoas moram na sua casa (incluindo você)?": {
        "5 pessoas ou mais": 10.0,
        "4 pessoas": 8.0,
        "3 pessoas": 6.0,
        "2 pessoas": 4.0,
        "Moro sozinho(a)": 0.0
    },
    "Qual é a situação da sua moradia?": {
        "Alugada": 10.0,
        "Cedida / Ocupação": 10.0,
        "Financiada": 6.0,
        "Própria": 0.0
    },
    "Qual o meio de transporte que você mais utiliza?": {
        "A pé / Bicicleta": 10.0,
        "Transporte público (ônibus)": 8.0,
        "Transporte fretado (van/ônibus da prefeitura)": 6.0,
        "Carro/Moto próprio ou da família": 0.0,
        "Aplicativo (Uber, 99, etc)": 0.0
    },
    "Você possui dependentes (filhos, parentes que dependem de você financeiramente)?": {
        "Sim, 2 ou mais": 10.0,
        "Sim, 1 dependente": 8.0,
        "Não possuo dependentes": 0.0
    },
    "Como você se declara em relação a cor/raça?": {
        "Preta": 10.0,
        "Parda": 10.0,
        "Indígena": 10.0,
        "Amarela": 2.0,
        "Branca": 0.0,
        "Prefiro não declarar": 0.0
    },
    "Qual o nível de escolaridade da sua mãe (ou responsável do sexo feminino)?": {
        "Nunca estudou / Ensino Fundamental incompleto": 10.0,
        "Ensino Fundamental completo": 8.0,
        "Ensino Médio incompleto": 6.0,
        "Ensino Médio completo": 4.0,
        "Ensino Superior incompleto": 2.0,
        "Ensino Superior completo ou mais": 0.0
    },
    "Qual o nível de escolaridade do seu pai (ou responsável do sexo masculino)?": {
        "Nunca estudou / Ensino Fundamental incompleto": 10.0,
        "Ensino Fundamental completo": 8.0,
        "Ensino Médio incompleto": 6.0,
        "Ensino Médio completo": 4.0,
        "Ensino Superior incompleto": 2.0,
        "Ensino Superior completo ou mais": 0.0
    }
}

def popular_banco():
    db = SessionLocal()
    try:
        # Verifica se já existe para evitar duplicações se você rodar o script sem querer 2 vezes
        questionario_existente = db.query(models.Questionario).filter_by(nome="Socioeconômico 2026").first()
        if questionario_existente:
            print("\n⚠️ O questionário já existe no banco. Cancelando para evitar duplicatas.")
            return

        print("\n🔄 Iniciando a injeção do gabarito de notas no banco de dados...")
        
        # Cria o Questionário
        questionario = models.Questionario(nome="Socioeconômico 2026", ativo=True)
        db.add(questionario)
        db.commit()
        db.refresh(questionario)

        # Insere as Questões e Alternativas no banco
        for texto_pergunta, alternativas in TABELA_PONTUACAO.items():
            nova_questao = models.Questao(questionario_id=questionario.id, texto_pergunta=texto_pergunta)
            db.add(nova_questao)
            db.commit()
            db.refresh(nova_questao)

            for texto_alternativa, peso in alternativas.items():
                nova_alternativa = models.AlternativaPeso(
                    questao_id=nova_questao.id,
                    texto_alternativa=texto_alternativa,
                    peso=float(peso)
                )
                db.add(nova_alternativa)

        db.commit()
        print("✅ INJEÇÃO CONCLUÍDA! As regras do questionário estão a salvo no PostgreSQL.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro crítico ao inserir dados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    popular_banco()
