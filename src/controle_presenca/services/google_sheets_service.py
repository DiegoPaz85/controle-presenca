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

                # 4. Monta o dicionário dinâmico com as 26 perguntas REAIS
                # O método .get() procura a coluna exata e retorna "" se o candidato não respondeu
                respostas_questionario = {
                    "q1_residencia": str(linha.get("Situação de residência", "")).strip(),
                    "q2_escolaridade": str(linha.get("Qual é seu nível de escolaridade?", "")).strip(),
                    "q3_escola_fundamental": str(linha.get("Em que tipo de escola você cursou o ensino fundamental?", "")).strip(),
                    "q4_escola_medio": str(linha.get("Em que tipo de escola você cursou (ou cursa) o ensino médio?", "")).strip(),
                    "q5_formacao_complementar": str(linha.get("Você possui ou realiza alguma espécie de formação complementar ? (Caso se enquadre em mais de uma opção, assinale a que você considera mais relevante na sua jornada educacional)", "")).strip(),
                    "q6_filhos": str(linha.get("Você tem filhos? Se sim, quantos?", "")).strip(),
                    "q7_pessoas_moram_com_voce": str(linha.get("Quantas pessoas moram com você? (incluindo filhos, irmãos, parentes, amigos e agregados)", "")).strip(),
                    "q8_escolaridade_pai": str(linha.get("Qual é o nível de escolaridade do seu pai?", "")).strip(),
                    "q9_escolaridade_mae": str(linha.get("Qual é o nível de escolaridade da sua mãe?", "")).strip(),
                    "q10_local_moradia": str(linha.get("O local onde você mora é", "")).strip(),
                    "q11_localizacao_moradia": str(linha.get("Sua moradia está localizada em", "")).strip(),
                    "q12_moradia_sao_carlos": str(linha.get("A sua moradia está localizada em São Carlos?", "")).strip(),
                    "q13_servicos_casa": str(linha.get("Assinale a alternativa que melhor corresponde aos serviços disponíveis em sua casa", "")).strip(),
                    "q14_renda_familiar": str(linha.get("Somando a sua renda com a renda das pessoas que moram com você, quanto é, aproximadamente, a renda familiar mensal? (Marque apenas uma resposta)", "")).strip(),
                    "q15_renda_individual": str(linha.get("Qual é a SUA renda mensal individual, aproximadamente?", "")).strip(),
                    "q16_veiculos": str(linha.get("Com quais e quantos veículos automotores (carros, motocicletas, tratores entre outros) conta você e os outros moradores da sua residência", "")).strip(),
                    "q17_computadores": str(linha.get("Descreva o número de computadores, tablets, notebooks ou similares que são e propriedade sua ou dos membros de sua residência", "")).strip(),
                    "q18_televisao": str(linha.get("Você possui dois ou mais aparelhos de televisão em sua residência?", "")).strip(),
                    "q19_servicos_domesticos": str(linha.get("Você emprega ou contratou, em algum momento da sua vida, pessoa ou firma para executar serviços domésticos (babá, faxineiro(a), caseiro(a), lavanderia, etc) em sua residência ou imóvel de sua propriedade", "")).strip(),
                    "q20_procura_emprego": str(linha.get("Você trabalha, já trabalhou ou esteve SERIAMENTE à procura de emprego nos últimos seis meses?", "")).strip(),
                    "q21_necessidades_especiais": str(linha.get("Na sua casa, existem pessoas com necessidades especiais?", "")).strip(),
                    "q22_trabalho_atual": str(linha.get("Em que você trabalha atualmente? (Marque apenas a sua atividade principal)", "")).strip(),
                    "q23_genero": str(linha.get("Qual é o seu gênero?", "")).strip(),
                    "q24_razoes_trabalho": str(linha.get("Assinale a alternativa cujo conteúdo melhor corresponde às razões pelas quais você começou a trabalhar", "")).strip(),
                    "q25_jornada_trabalho": str(linha.get("De quantas horas é sua jornada semanal de trabalho?", "")).strip(),
                    "q26_idade_comecou_trabalhar": str(linha.get("Com que idade você começou a trabalhar?", "")).strip()
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








