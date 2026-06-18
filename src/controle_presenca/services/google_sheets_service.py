import os
import gspread
from sqlalchemy.orm import Session
from src.controle_presenca.services.sgdi_service import SGDiService

class GoogleSheetsService:
    def __init__(self, db: Session):
        self.db = db
        self.sgdi_service = SGDiService(db)

    def sincronizar_dados_forms(self, spreadsheet_id: str):
        # O arquivo credentials.json deve estar na pasta raiz do projeto
        path_to_json = "credentials.json"
        
        if not os.path.exists(path_to_json):
            raise FileNotFoundError("⚠️ Arquivo credentials.json não encontrado na raiz!")

        # 1. Autentica no Google
        gc = gspread.service_account(filename=path_to_json)
        
        # 2. Abre a planilha pelo ID
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.get_worksheet(0) # Pega a primeira aba (Respostas do formulário 1)
        
        # 3. Lê todas as linhas
        registros = worksheet.get_all_records()
        
        sucessos = 0
        erros = []

        for linha in registros:
            try:
                # Puxa os dados pessoais básicos
                nome = str(linha.get("Nome Completo", "")).strip()
                cpf = str(linha.get("CPF", "")).strip()
                email = str(linha.get("E-mail", "")).strip()

                # Se a linha estiver vazia (ex: o Google puxou uma linha em branco), pula
                if not nome or not cpf:
                    continue

                # Puxa as 3 respostas reais que vieram do Google Forms
                q1 = str(linha.get("1. Onde você mora atualmente?", ""))
                q2 = str(linha.get("2. Qual a sua escolaridade?", ""))
                q3 = str(linha.get("3. Onde cursou o ensino fundamental?", ""))

                # Monta o dicionário. Usamos as 3 reais e "mockamos" as outras 23 para a matemática não quebrar
                respostas_questionario = {
                    "q1_residencia": q1,
                    "q2_escolaridade": q2,
                    "q3_escola_fundamental": q3,
                    "q4_escola_medio": "Escola pública estadual",
                    "q5_formacao_complementar": "Nenhuma das anteriores",
                    "q6_filhos": "Não tenho filhos",
                    "q7_pessoas_moram_com_voce": "Moro sozinho",
                    "q8_escolaridade_pai": "Ensino Médio (antigo 2º grau)",
                    "q9_escolaridade_mae": "Ensino Médio (antigo 2º grau)",
                    "q10_local_moradia": "Alugado",
                    "q11_localizacao_moradia": "Zona urbana",
                    "q12_moradia_sao_carlos": "Sim",
                    "q13_servicos_casa": "Coleta de lixo, água encanada",
                    "q14_renda_familiar": "De R$ 954,01 até R$ 1.908,00",
                    "q15_renda_individual": "Nenhuma renda",
                    "q16_veiculos": "Nenhum",
                    "q17_computadores": "Um",
                    "q18_televisao": "Não",
                    "q19_servicos_domesticos": "Não, sou eu quem faz sozinho(a)",
                    "q20_procura_emprego": "Sim",
                    "q21_necessidades_especiais": "Não",
                    "q22_trabalho_atual": "Não trabalho",
                    "q23_genero": "Masculino",
                    "q24_razoes_trabalho": "Não trabalho",
                    "q25_jornada_trabalho": "Não trabalho",
                    "q26_idade_comecou_trabalhar": "Após 18 anos"
                }

                # Chama o seu motor que já está pronto e testado
                self.sgdi_service.registrar_novo_candidato(
                    nome=nome,
                    cpf=cpf,
                    email=email,
                    respostas_questionario=respostas_questionario
                )
                sucessos += 1
            except ValueError as e:
                erros.append({"cpf": cpf, "erro": str(e)}) # CPF duplicado, por exemplo
            except Exception as e:
                erros.append({"linha": nome, "erro": str(e)})

        return {"processados_com_sucesso": sucessos, "falhas_ou_duplicados": erros}