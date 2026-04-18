# 📊 Comparação: SGDI Legado vs SGDI Atual

## 1. Arquitetura

### SGDI Legado (ExpliCAASO)
- **Monolítico**: Código centralizado em `SGDireserva_comentado.py` (~1200 linhas)
- **Baseado em Planilhas**: Toda lógica de dados em arquivos Excel
- **CLI Simples**: Menu interativo baseado em input de texto

### SGDI Atual (controle-presenca)
- **Modular**: Separação de responsabilidades em pacotes
  - `api/` → Endpoints REST
  - `services/` → Lógica de negócio
  - `database/` → Acesso a dados
  - `cli/` → Interface de linha de comando
  - `config/` → Configurações
- **Banco de Dados Relacional**: SQLAlchemy + modelos ORM
- **API REST**: Endpoints estruturados

---

## 2. Funcionalidades - Comparação Detalhada

### 2.1 Gerenciamento de Candidatos

| Funcionalidade | SGDI Legado | SGDI Atual | Status |
|---|---|---|---|
| Adicionar alunos | ✅ Sim (modo manual/automático via Google Forms) | ⚠️ Parcial (apenas BD direto) | **REDUZIDO** |
| Remover alunos | ✅ Sim (exclusão de candidatos) | ❌ Não implementado | **PERDIDO** |
| Pesquisar alunos | ✅ Sim (busca por nome/CPF) | ❌ Não implementado | **PERDIDO** |
| Duplicação de candidatos | ✅ Evita duplicatas (verifica CPF) | ❌ Não há validação | **PERDIDO** |

### 2.2 Ranking e Seleção

| Funcionalidade | SGDI Legado | SGDI Atual | Status |
|---|---|---|---|
| Ranking por pontuação | ✅ Sim (cálculo socioeconômico) | ✅ Sim (`gerar_ranking()`) | **MANTIDO** |
| Corte de candidatos | ✅ Sim (aprovar com base em ranking) | ✅ Sim (`aprovar_corte()`) | **MANTIDO** |
| Limite de 60 alunos | ✅ Sim (validação comentada) | ❌ Não há limite | **PERDIDO** |
| Critérios de pontuação | ✅ Sim (25 questões, 15-34) | ❌ Usando pontuação genérica | **PERDIDO** |

### 2.3 Matrícula

| Funcionalidade | SGDI Legado | SGDI Atual | Status |
|---|---|---|---|
| Converter aprovado em aluno | ✅ Sim (insere em tabela Aluno) | ✅ Sim (`matricular_candidato()`) | **MANTIDO** |
| Gerar cartão | ✅ Sim (ID aleatório 6 dígitos) | ✅ Sim (ID aleatório 6 dígitos) | **MANTIDO** |
| Enviar cartão por email | ✅ Sim (com imagem JPG) | ❌ Não implementado | **PERDIDO** |

### 2.4 Presenças

| Funcionalidade | SGDI Legado | SGDI Atual | Status |
|---|---|---|---|
| Registrar presença | ✅ Sim (% de presença) | ✅ Sim (existem repositórios) | **MANTIDO** |
| Atualizar presenças | ✅ Sim (menu opção 5) | ⚠️ Parcial (estrutura existe) | **REDUZIDO** |
| Gerar relatório de presença | ✅ Sim (planilha "Cartola mágica") | ❌ Não implementado | **PERDIDO** |

### 2.5 Integração e Comunicação

| Funcionalidade | SGDI Legado | SGDI Atual | Status |
|---|---|---|---|
| Envio de emails | ✅ Sim (aprovação/exclusão automática) | ❌ Não implementado | **PERDIDO** |
| Integração Google Forms | ✅ Sim (download automático) | ❌ Não implementado | **PERDIDO** |
| Integração Google Drive | ✅ Sim (autenticação por credenciais) | ❌ Não implementado | **PERDIDO** |
| Confirmação de inscrição | ✅ Sim (verifica CPF em forms) | ❌ Não implementado | **PERDIDO** |

### 2.6 Dados e Documentação

| Funcionalidade | SGDI Legado | SGDI Atual | Status |
|---|---|---|---|
| Validação de dados | ✅ Sim (remove caracteres especiais) | ⚠️ Parcial (validações básicas) | **REDUZIDO** |
| Tratamento de duplicatas | ✅ Sim (por nome/CPF) | ❌ Não há estratégia | **PERDIDO** |
| Geração de listas | ✅ Sim (salvando em planilhas) | ❌ Não implementado | **PERDIDO** |
| Relatórios | ✅ Sim ("Cartola mágica") | ❌ Não implementado | **PERDIDO** |

---

## 3. Funcionalidades Implementadas no SGDI Atual

### ✅ SGDiService

```python
# Método 1: gerar_ranking(limite: int)
- Busca candidatos com status 'pendente'
- Ordena por pontuação_socioeconomica DESC
- Retorna até `limite` candidatos

# Método 2: aprovar_corte(quantidade: int)
- Aprova os `quantidade` primeiros do ranking
- Altera status para 'aprovado'
- Retorna quantidade aprovada

# Método 3: matricular_candidato(cpf: str)
- Valida candidato por CPF
- Verifica se está aprovado
- Cria novo Aluno com cartão aleatório
- Altera status do candidato para 'confirmado'
```

---

## 4. Modelos de Dados

### SGDI Legado
```
Planilhas Excel:
- BancoDeDados.xlsx → Candidatos/Alunos
- Critérios de pontuação.xlsx → Pontuação (25 questões)
- Questionário socioeconômico (respostas).xlsx
- Inscrição de alunos (respostas).xlsx
- Confirmação de entrada (respostas).xlsx
- ListaDeExcluidos.xlsx
```

### SGDI Atual
```
Modelos ORM:
- Candidato (nome, cpf, status, pontuacao_socioeconomica)
- Aluno (cartao_id, nome, status)
```

---

## 5. Funcionalidades Perdidas (Críticas)

| Funcionalidade | Impacto | Prioridade |
|---|---|---|
| ❌ Integração Google Forms | Alto - impossível importar candidatos automaticamente | 🔴 ALTO |
| ❌ Envio de emails | Alto - não notifica aprovação/exclusão | 🔴 ALTO |
| ❌ Validação de duplicatas | Alto - pode ter duplicação de candidatos | 🔴 ALTO |
| ❌ Limite de 60 alunos | Médio - controle de capacidade da turma | 🟡 MÉDIO |
| ❌ Remoção de alunos | Alto - falta operação reverse | 🔴 ALTO |
| ❌ Pesquisa de alunos | Médio - dificuldade em achar candidatos | 🟡 MÉDIO |
| ❌ Geração de relatórios | Médio - sem visibilidade de dados | 🟡 MÉDIO |
| ❌ Critérios de pontuação variáveis | Médio - pontuação hardcoded | 🟡 MÉDIO |

---

## 6. Funcionalidades Novas no SGDI Atual

| Funcionalidade | Descrição |
|---|---|
| ✅ API REST | Interface programática para integração |
| ✅ Banco de dados relacional | Melhor escalabilidade e integridade |
| ✅ ORM (SQLAlchemy) | Abstração do banco de dados |
| ✅ Testes automatizados | Cobertura de testes (unit/integration) |
| ✅ Docker | Containerização da aplicação |
| ✅ Modularização | Separação clara de responsabilidades |

---

## 7. Menu Principal

### SGDI Legado
```
1. Adicionar alunos ao banco de dados (com Google Forms)
2. Excluir alunos do banco de dados
3. Pesquisar alunos no banco de dados
4. Gerar lista de dados
5. Atualizar presenças do leitor
6. Modificar dados de presença dos alunos
7. Sair
```

### SGDI Atual
```
REST API:
- POST   /sgdi/ranking      → gerar ranking
- POST   /sgdi/aprovar-corte → aprovar candidatos
- POST   /sgdi/matricular   → matricular candidato

CLI (estrutura):
- [Menu interativo não implementado no SGDI Service]
```

---

## 8. Fluxo de Adição de Candidatos

### SGDI Legado
1. Escolhe modo: Manual ou Automático
2. Se Automático:
   - Conecta ao Google Drive
   - Baixa planilhas de respostas
3. Se Manual:
   - Espera colocar arquivos em `/Entradas`
4. Processa 3 planilhas:
   - Questionário socioeconômico
   - Inscrição de alunos
   - Confirmação de entrada
5. Remove duplicatas
6. Calcula pontuação (25 questões)
7. Gera ranking
8. Mostra lista de aprovados
9. Envia emails de aprovação
10. Adiciona ao banco de dados

### SGDI Atual
1. API POST `/sgdi/matricular`
2. Valida CPF
3. Cria novo Aluno
4. Retorna resposta JSON

**Diferença**: SGDI atual é **muito mais simples**, mas **não importa candidatos de formulários**.

---

## 9. Fluxo de Matrícula

### SGDI Legado
```
Candidato aprovado + confirmação
    ↓
Insere em BancoDeDados.xlsx
    ↓
Gera ID de cartão (6 dígitos)
    ↓
Envia email com cartão (JPG)
    ↓
Cria histórico de matrícula
```

### SGDI Atual
```
Candidato.cpf aprovado
    ↓
Cria novo Aluno
    ↓
Gera cartao_id aleatório
    ↓
Altera status para 'confirmado'
    ↓
Retorna JSON com dados
```

**Diferência**: SGDI atual não envia email nem mantém histórico.

---

## 10. Estrutura de Armazenamento

### SGDI Legado
```
SGDi/
├── BancoDeDados.xlsx (Alunos + dados)
├── Bancos de dados/
├── Cartola mágica/ (Relatórios)
├── Documentos_auxiliares_nao_mexer/
│   ├── credentials.json (Google API)
│   ├── Cartões/ (JPG)
│   └── ...
└── Entradas/ (Forms baixados)
```

### SGDI Atual
```
controle-presenca/
├── src/controle_presenca/
├── docker/
├── scripts/
├── tests/
└── BancoDeDados.xlsx (importação legada)
```

---

## 11. Conclusão

### ✅ Mantido (Core)
- Ranking por pontuação socioeconômica
- Aprovação de candidatos
- Matrícula com geração de cartão

### ❌ Perdido (Funcionalidades importantes)
- Importação de formulários Google
- Envio de emails
- Métodos de pesquisa e exclusão
- Validação contra duplicatas
- Geração de relatórios
- Integração com Google Drive

### ⚠️ Recomendações
1. **Implementar fila de tarefas** para envio de emails
2. **Adicionar endpoints** para pesquisa e exclusão de candidatos
3. **Implementar validação** contra duplicatas
4. **Restaurar integração** com Google Forms (opcional, mas importante)
5. **Adicionar geração** de relatórios
6. **Escrever testes** para validar funcionalidades críticas
