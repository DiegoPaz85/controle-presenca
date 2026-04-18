# 📊 Comparação: Sistema Legado vs. Nova Arquitetura ExpliCAASO

## 📋 Visão Geral

Este documento compara as funcionalidades de gestão de presença entre o **Sistema Legado** (baseado em Excel + Google Drive) e o **Sistema Novo** (API REST + PostgreSQL + Docker).

**Data da análise:** Abril 2026  
**Sistema Legado:** `LeitorDePresenca.py` (528 linhas)  
**Sistema Novo:** Arquitetura modular com API REST

---

## 1. ARQUITETURA GERAL

| Aspecto | Sistema Legado | Sistema Novo |
|---------|---|---|
| **Tipo** | Script Python puro + arquivos Excel | API REST + CLI + Banco de Dados |
| **Persistência** | Excel (xlsx) local | PostgreSQL (banco relacional) |
| **Acesso remoto** | Google Drive (download/upload manual) | HTTP API REST + Interface Web (PgAdmin) |
| **Segurança** | Credenciais em arquivo (menos seguro) | Variáveis de ambiente + .env isolado |
| **Deploy** | Local/Manual | Docker (conteinerizado) |

---

## 2. FUNCIONALIDADES DE GESTÃO DE PRESENÇA

### ✅ Implementadas nos DOIS
- ✔️ Leitura de cartões (ID do aluno)
- ✔️ Registro de entrada/saída
- ✔️ Estado do aluno: `ATIVADO` / `DESATIVADO`
- ✔️ Cálculo de tempo de presença
- ✔️ Marcação de "dentro de sala" / "fora de sala"
- ✔️ Histórico de eventos (entrada/saída)
- ✔️ Tratamento de intervalos
- ✔️ Importação de alunos (Excel)

### ⚠️ Implementadas APENAS no Legado
- ⚠️ **Cálculo de porcentagem de presença** (coluna C na planilha)
  - Média ponderada baseada em carga horária
  - Fórmula: `100 * ((% anterior × carga_anterior + tempo_sessão) / (carga_anterior + tempo_sessão))`
- ⚠️ **Carga horária total acumulada** (coluna D)
  - Soma de todas as horas em todas as sessões
- ⚠️ **Múltiplas sessões** gerenciadas dentro do mesmo arquivo
  - Estrutura: `S = [inicio_sessao, fim_sessao]`
  - Recalcula tudo por sessão
- ⚠️ **Sincronização com Google Drive**
  - Download automático de `presenca.xlsx`
  - Upload automático de backup
  - Exclusão do arquivo após uso (sync)

### ✨ Implementadas APENAS no Novo
- ✨ **Banco de dados relacional** (PostgreSQL)
  - Integridade referencial
  - Impossível registrar presença de aluno não cadastrado
- ✨ **API REST** para acesso remoto
  - Acesso via HTTP (integração com outros sistemas)
  - Suporte a diferentes clientes (web, mobile, etc.)
- ✨ **CLI interativa** com menu
  - Interface colorida com feedback visual
  - Navegação estruturada por menus
- ✨ **Modelos de banco de dados** estruturados
  - `Aluno`: id, cartao_id, nome, status
  - `Sessao`: id, inicio, fim, status
  - `Registro`: id, aluno_id, sessao_id, tipo (entrada/saída), timestamp
- ✨ **Backup automático** (script bash com Cron)
  - Agendamento diário à meia-noite
  - Upload para Google Drive via Rclone
- ✨ **Containerização Docker**
  - Roda em qualquer sistema sem dependências
  - PgAdmin para visualização do banco (web UI)
- ✨ **Testes automatizados**
  - Unit tests
  - Integration tests
  - CI/CD ready

---

## 3. GERENCIAMENTO DE DADOS

| Aspecto | Legado | Novo |
|---------|--------|------|
| **Formato armazenamento** | Excel (.xlsx) | PostgreSQL (ACID) |
| **Integridade dados** | Manual | Automática (constraints FK) |
| **Escalabilidade** | Limitada (Excel lento com muitos dados) | Alta (Postgres suporta milhões de registros) |
| **Concorrência** | ❌ Não (arquivo único) | ✅ Sim (múltiplos usuários simultâneos) |
| **Backup** | Manual + Google Drive | Automático + Cloud |
| **Consultas** | Leitura sequencial | SQL otimizado |

---

## 4. GESTÃO DE SESSÕES

| Aspecto | Legado | Novo |
|---------|--------|------|
| **Múltiplas sessões** | ✅ Sim (dentro do mesmo arquivo) | ✅ Sim (tabela separada) |
| **Duração sessão** | Definida pelo usuário (S[0] e S[1]) | Rastreada no DB (inicio/fim) |
| **Intervalo dentro sessão** | ✅ Sim (descontado do tempo) | ⚠️ A implementar |
| **Recalculo pós-sessão** | ✅ Automático (após fechar) | ⚠️ A implementar |

---

## 5. FUNCIONALIDADES CRÍTICAS FALTANDO NO NOVO

| Funcionalidade | Prioridade | Complexidade |
|---|---|---|
| 🔴 **Cálculo de % presença ponderada** | ALTA | Média |
| 🔴 **Carga horária acumulada por aluno** | ALTA | Baixa |
| 🟡 **Recalculo automático pós-sessão** | MÉDIA | Média |
| 🟡 **Tratamento de intervalos na sessão** | MÉDIA | Baixa |
| 🟢 **Relatório de presenças** | BAIXA | Alta |

---

## 6. CÓDIGO LEGADO - DETALHES TÉCNICOS

**Arquivo principal:** `LeitorDePresenca.py` (528 linhas)

**Estrutura de dados (matriz M):**
```
M[i][0] = ID do aluno
M[i][1] = Status ('ATIVADO' ou 'DESATIVADO')
M[i][2] = Localização ('DENTRO DE SALA' ou 'FORA DE SALA')
M[i][3] = Contador evento (entrada/saída)
M[i][4] = Flag entrada ('início' ou 'f')
M[i][5] = Flag saída ('fim' ou 'f')
M[i][6] = ?
M[i][7] = Tempo acumulado da sessão atual
M[i][8] = Nome do aluno
M[i][9] = Carga horária total GLOBAL
```

**Funções principais:**
- `diferençaefetiva()`: Calcula tempo sem intervalos
- Sincronização com Google Drive (download/delete)
- Loop principal: lê cartão → atualiza estado → calcula tempo

---

## 🎯 RECOMENDAÇÕES PARA MIGRAÇÃO

### Prioritários (Sprint 1):
- [ ] Implementar cálculo de % presença ponderada
- [ ] Implementar carga horária total por aluno
- [ ] Adicionar campos na tabela `Aluno`: `percentual_presenca`, `carga_horaria_total`

### Importantes (Sprint 2):
- [ ] Tratamento de intervalos dentro da sessão
- [ ] Recalculo automático ao fechar sessão
- [ ] Endpoints de relatório (CSV export)

### Melhorias (Sprint 3+):
- [ ] Dashboard de visualização
- [ ] Alertas para alunos desativados
- [ ] Histórico de mudanças de status

---

## 📈 Benefícios da Nova Arquitetura

1. **Escalabilidade**: Suporte a milhares de alunos simultâneos
2. **Confiabilidade**: Dados ACID, backups automáticos
3. **Integração**: API REST para sistemas externos
4. **Manutenibilidade**: Código modular, testes automatizados
5. **Segurança**: Isolamento de rede, criptografia de senhas
6. **Disponibilidade**: Containerização garante funcionamento em qualquer ambiente

---

## ⚠️ Riscos de Migração

1. **Perda de funcionalidades**: % presença e carga horária não implementadas
2. **Curva de aprendizado**: Equipe precisa aprender Docker e APIs
3. **Dependências**: PostgreSQL e Docker aumentam complexidade inicial
4. **Migração de dados**: Importação de históricos antigos pode ser complexa

---

*Este documento foi gerado automaticamente através da análise comparativa dos sistemas legado e novo.*