# src/controle_presenca/utils/criterios_sgdi.py

from typing import Dict, Tuple


# Dicionário mapeando as "chaves" das questões (para facilitar a API) 
# e as alternativas com suas respectivas pontuações.
CRITERIOS_PONTUACAO = {
    "q1_residencia": {
        "República": 1.0,
        "Apartamento": 1.0,
        "Mora com a família": 1.0,
        "Alojamento da USP": 2.0
    },
    "q2_escolaridade": {
        "Ensino médio completo": 10.0,
        "Cursando o primeiro ano do ensino médio": 4.0,
        "Cursando o segundo ano do ensino médio": 7.0,
        "Cursando o terceiro ano do ensino médio": 10.0,
        "Superior incompleto": 1.0
    },
    "q3_escola_fundamental": {
        "Escola pública municipal": 10.0,
        "Escola pública estadual": 10.0,
        "Escola pública federal": 5.0,
        "Escola militar": 1.0,
        "Escola particular": 1.0
    },
    "q4_escola_medio": {
        "Escola pública municipal": 10.0,
        "Escola pública estadual": 10.0,
        "Instituto federal/Escola técnica": 8.0,
        "Escola particular": 1.0,
        "Escola militar": 1.0,
        "EJA": 5.0
    },
    "q5_formacao_complementar": {
        "Sim, curso de idiomas (inglês, espanhol, etc.)": 2.0,
        "Sim, curso profissionalizante/capacitação oferecido pela empresa/escola": 4.0,
        "Sim, curso profissionalizante/capacitação gratuita fora da empresa/escola": 4.0,
        "Sim, curso profissionalizante/capacitação paga fora da empresa/escola": 2.0,
        "Sim, intercâmbio gratuito ou com bolsa/auxílio": 3.0,
        "Sim, intercâmbio pago por mim ou familiares/amigos": 1.0,
        "Nenhuma das anteriores": 4.0
    },
    "q6_filhos": {
        "Não tenho filhos": 1.0,
        "Sim, tenho um filho": 2.0,
        "Sim, tenho entre dois e três filhos": 3.0,
        "Tenho mais de três filhos": 4.0
    },
    "q7_pessoas_moram_com_voce": {
        "Moro sozinho": 1.0,
        "Uma a três": 2.0,
        "Quatro a sete": 3.0,
        "Oito a dez": 4.0,
        "Mais de dez": 4.0
    },
    "q8_escolaridade_pai": {
        "Da 1ª à 4ª série do Ensino Fundamental": 3.0,
        "Da 5ª à 8ª série do Ensino Fundamental": 2.0,
        "Ensino Médio (antigo 2º grau)": 2.0,
        "Ensino Superior": 1.0,
        "Especialização": 1.0,
        "Não estudou": 3.0,
        "Não sei": 1.0
    },
    "q9_escolaridade_mae": {
        "Da 1ª à 4ª série do Ensino Fundamental": 3.0,
        "Da 5ª à 8ª série do Ensino Fundamental": 3.0,
        "Ensino Médio (antigo 2º grau)": 2.0,
        "Ensino Superior": 1.0,
        "Especialização": 1.0,
        "Não estudou": 3.0,
        "Não sei": 1.0
    },
    "q10_local_moradia": {
        "Próprio (seu)": 1.0,
        "Próprio (seu), ainda sendo pago": 1.0,
        "Alugado": 2.0,
        "Cedido": 3.0,
        "Moro com os pais ou outros responsáveis": 2.0,
        "Ocupado": 3.0
    },
    "q11_localizacao_moradia": {
        "Zona rural": 4.0,
        "Zona urbana": 3.0,
        "Assentamento rural ou área de retomada": 4.0
    },
    "q12_moradia_sao_carlos": {
        "Sim": 1.0,
        "Não": 1.0
    },
    "q13_servicos_casa": {
        "Coleta de lixo": 4.0,
        "Coleta de lixo, água encanada": 3.0,
        "Coleta de lixo, água encanada, energia elétrica": 2.0,
        "Coleta de lixo, água encanada, energia, telefonia": 2.0,
        "Coleta de lixo, água encanada, energia, telefonia, internet": 1.0,
        "Nenhum dos serviços": 5.0
    },
    "q14_renda_familiar": {
        "Nenhuma renda": 5.0,
        "De até R$ 954,00": 5.0,
        "De R$ 954,01 até R$ 1.908,00": 4.0,
        "De R$ 1.908,01 até R$ 2.862,00": 3.0,
        "De R$ 2.862,01 até R$ 3.816,00": 2.0,
        "De R$ 3.816,01 até R$ 4.770,00": 2.0,
        "Mais de R$ 4.770,00": 1.0
    },
    "q15_renda_individual": {
        "Nenhuma renda": 4.0,
        "Até R$ 954,00": 3.0,
        "De R$ 954,01 até R$ 1.908,00": 2.0,
        "De R$ 1.908,01 até R$ 2.862,00": 2.0,
        "De R$ 2.862,01 até R$ 3.816,00": 1.0,
        "Mais de R$ 3.816,00": 1.0
    },
    "q16_veiculos": {
        "Nenhum": 4.0,
        "Apenas uma motocicleta, motoneta ou similares": 3.0,
        "Apenas um carro": 2.0,
        "Apenas um trator ou outro equipamento agrícola": 2.0,
        "Mais de uma motocicleta": 1.0,
        "Uma motocicleta e outro veículo": 1.0,
        "Dois ou mais carros/equipamentos agrícolas": 1.0,
        "Outros": 1.0
    },
    "q17_computadores": {
        "Nenhum": 3.0,
        "Um": 2.0,
        "Dois": 1.0,
        "Três ou mais": 1.0
    },
    "q18_televisao": {
        "Sim": 1.0,
        "Não": 2.0
    },
    "q19_servicos_domesticos": {
        "Sim, babá ocasionalmente": 2.0,
        "Sim, empregado(a) ocasionalmente": 1.0,
        "Sim, babá frequentemente, sem carteira": 1.0,
        "Sim, empregado(a) frequentemente, sem carteira": 1.0,
        "Sim, babá frequentemente, com carteira": 1.0,
        "Sim, empregado(a) frequentemente, com carteira": 1.0,
        "Sim, firma/negócio individual": 1.0,
        "Não, mas recebo colaboração regular de familiares/vizinhos": 4.0,
        "Não, sou eu quem faz sozinho(a) ou com colaboração ocasional": 4.0
    },
    "q20_procura_emprego": {
        "Sim": 2.0,
        "Não": 1.0
    },
    "q21_necessidades_especiais": {
        "Não": 1.0,
        "Sim, apenas uma": 2.0,
        "Sim, duas": 3.0,
        "Sim, mais de duas": 4.0
    },
    "q22_trabalho_atual": {
        "Agricultura, campo, fazenda ou pesca": 3.0,
        "Indústria": 2.0,
        "Construção civil": 3.0,
        "Comércio, banco, transporte, hotelaria ou outros serviços": 2.0,
        "Funcionário(a) do governo federal, estadual ou municipal": 2.0,
        "Profissional liberal, professora ou técnica de nível médio/superior": 1.0,
        "Trabalho informal fora de casa (pintor, eletricista, feirante, etc.)": 4.0,
        "Trabalho informal em casa (costura, aulas particulares, artesanato)": 3.0,
        "Trabalho doméstico em casa de outras pessoas": 4.0,
        "Trabalho fora de casa como microempresário(a) ou empreendedor(a) individual": 1.0,
        "Não trabalho": 1.0,
        "Recebo pensão ou aposentadoria do INSS": 1.0,
        "Outro": 1.0
    },
    "q23_genero": {
        "Masculino": 1.0,
        "Feminino": 1.0,
        "Gênero neutro": 2.0,
        "Não-binário": 2.0,
        "Outro": 2.0
    },
    "q24_razoes_trabalho": {
        "Ajudar nas despesas com a casa, sustentar minha família": 2.0,
        "Ser independente (ganhar meu próprio dinheiro), adquirir experiência": 1.0,
        "Ser independente (ganhar meu próprio dinheiro)": 1.0,
        "Custear meus estudos ou de alguém próximo": 2.0,
        "Dívidas, empréstimos": 2.0,
        "Outro": 1.0,
        "Não trabalho": 1.0
    },
    "q25_jornada_trabalho": {
        "Não trabalho": 1.0,
        "Sem jornada fixa, até 10 horas semanais": 2.0,
        "De 11 a 20 horas semanais": 2.0,
        "De 21 a 30 horas semanais": 3.0,
        "De 31 a 40 horas semanais": 3.0,
        "Mais de 40 horas semanais": 3.0
    },
    "q26_idade_comecou_trabalhar": {
        "Antes dos 14 anos": 1.0,
        "Entre 14 e 16 anos": 1.0,
        "Entre 17 e 18 anos": 1.0,
        "Após 18 anos": 1.0
    }
}

def calcular_pontuacao(respostas_candidato: Dict[str, str]) -> Tuple[float, list]:
    """
    Calcula a pontuação socioeconômica total do candidato com base nas suas respostas.
    
    Args:
        respostas_candidato: Dicionário contendo a chave da questão e a alternativa escolhida.
                             Ex: {"q1_residencia": "República", "q2_escolaridade": "Superior incompleto"}
                             
    Returns:
        Uma tupla contendo (pontuacao_total, lista_de_registros_validados)
    """
    pontuacao_total = 0.0
    registros_processados = []

    for questao_chave, alternativa_escolhida in respostas_candidato.items():
        # Verifica se a chave da pergunta existe nas regras
        if questao_chave in CRITERIOS_PONTUACAO:
            criterios_da_questao = CRITERIOS_PONTUACAO[questao_chave]
            
            # Verifica se a alternativa existe (strip remove espaços acidentais)
            alternativa_limpa = alternativa_escolhida.strip()
            
            if alternativa_limpa in criterios_da_questao:
                pontos = criterios_da_questao[alternativa_limpa]
                pontuacao_total += pontos
                
                # Guarda o detalhamento para salvar no banco depois (tabela pontuacoes_questionario)
                registros_processados.append({
                    "questao": questao_chave,
                    "resposta": alternativa_limpa,
                    "pontos": pontos
                })
            else:
                # Opcional: tratar alternativa não encontrada (log, ignorar ou levantar erro)
                pass
                
    return pontuacao_total, registros_processados