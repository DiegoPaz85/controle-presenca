#  Testes do Sistema ExpliCAASO

##  Status Atual dos testes

| Métrica | Valor |
|---------|-------|
| **Cobertura Total** | 70% |
| **Testes Passando** | 61 |
| **Arquivos com 100%** | 13 |
| **Quality Gate** | ✅ Aprovado |

---

## 🚀 Executando os Testes

### Pré-requisitos

Certifique-se de que o container está rodando:

```bash
docker ps

Executar todos os testes

bash
docker exec -it explicaaso_app pytest tests/ --cov=src --cov-report=term-missing -v --ignore=tests/unit/api/

Executar testes específicos
bash
# Apenas testes de serviços
docker exec -it explicaaso_app pytest tests/unit/services/ -v

# Apenas testes de banco de dados
docker exec -it explicaaso_app pytest tests/unit/database/ -v

# Apenas testes de CLI
docker exec -it explicaaso_app pytest tests/unit/cli/ -v
Gerar relatório de cobertura
bash
# Relatório no terminal
docker exec -it explicaaso_app pytest tests/ --cov=src --cov-report=term --ignore=tests/unit/api/

# Relatório em XML (para SonarCloud)
docker exec -it explicaaso_app pytest tests/ --cov=src --cov-report=xml:coverage.xml --ignore=tests/unit/api/


📁 Estrutura dos Testes
text
tests/
├── conftest.py                 # Fixtures compartilhadas
├── unit/
│   ├── api/                    # Testes da API (⚠️ skippados)
│   │   ├── test_main.py
│   │   ├── test_main_complete.py
│   │   └── test_main_simple.py
│   ├── cli/                    # Testes do CLI
│   │   ├── test_main_cli.py    # Funções do menu principal
│   │   ├── test_main_entry.py  # Verificação de funções
│   │   └── test_main_menu.py   # Estrutura do menu
│   ├── config/                 # Testes de configuração
│   │   └── test_settings.py    # Configurações do sistema
│   ├── database/               # Testes de banco de dados
│   │   ├── test_connection.py
│   │   ├── test_connection_error.py
│   │   ├── test_models.py
│   │   ├── test_presenca_repos.py
│   │   └── test_presenca_repos_extra.py
│   ├── services/               # Testes de serviços
│   │   └── test_sgdi_service.py
│   ├── test_colors.py          # Testes de cores do CLI
│   └── test_presenca_service.py # Testes do serviço de presença



🧪 Testes por Módulo
1. Configurações (config/test_settings.py)
Teste	Descrição
test_settings_import	Verifica se o módulo pode ser importado
test_settings_has_database_url	Verifica se DATABASE_URL existe
test_settings_has_debug_flag	Verifica se DEBUG existe
test_settings_has_log_level	Verifica se LOG_LEVEL existe
test_settings_debug_default	Verifica se DEBUG padrão é False
test_settings_debug_true	Verifica se DEBUG pode ser True
test_settings_load_database_url_from_env	Testa carregamento de variável de ambiente
2. Banco de Dados - Models (database/test_models.py)
Teste	Descrição
test_aluno_model_exists	Verifica modelo Aluno
test_sessao_model_exists	Verifica modelo Sessao
test_registro_model_exists	Verifica modelo Registro
test_candidato_model_exists	Verifica modelo Candidato
test_pontuacao_questionario_model_exists	Verifica modelo PontuacaoQuestionario
test_aluno_has_required_columns	Verifica colunas do Aluno
test_sessao_has_required_columns	Verifica colunas da Sessao
test_registro_has_required_columns	Verifica colunas do Registro
3. Banco de Dados - Repositórios (database/test_presenca_repos.py)
Teste	Descrição
test_repository_initialization	Inicialização do repositório
test_buscar_aluno_com_cartao_valido	Busca aluno por cartão
test_buscar_aluno_com_cartao_invalido	Busca cartão inválido
test_obter_sessao_ativa	Obter sessão ativa
test_registrar_ponto	Registrar ponto
test_obter_ultimo_registro	Obter último registro
test_criar_sessao	Criar nova sessão
test_encerrar_sessao	Encerrar sessão
4. Serviço de Presença (test_presenca_service.py)
Teste	Descrição
test_processar_leitura_sem_sessao_ativa	Leitura sem sessão ativa
test_processar_leitura_com_sessao_ativa_e_cartao_valido	Leitura válida
test_processar_leitura_com_saida	Registro de saída
test_processar_leitura_com_cartao_invalido	Cartão não numérico
test_processar_leitura_com_cartao_nao_cadastrado	Cartão não cadastrado
test_processar_leitura_com_aluno_inativo	Aluno inativo
5. Serviço SGDi (services/test_sgdi_service.py)
Teste	Descrição
test_sgdi_service_initialization	Inicialização do serviço
test_sgdi_service_gerar_ranking	Geração de ranking
test_sgdi_service_aprovar_corte	Aprovação por corte
test_sgdi_service_matricular_candidato_sucesso	Matrícula bem-sucedida
test_sgdi_service_matricular_candidato_nao_encontrado	Candidato não encontrado
test_sgdi_service_matricular_candidato_nao_aprovado	Candidato não aprovado
6. CLI (cli/)
Teste	Descrição
test_main_import	Importação do módulo
test_main_has_menu_functions	Verifica funções do menu
test_limpar_tela_execution	Limpeza de tela
test_pausar_execution	Pausa com input
test_iniciar_sessao_aula_sem_sessao_ativa	Iniciar sessão sem ativa
test_iniciar_sessao_aula_com_sessao_ativa	Iniciar sessão com ativa
test_encerrar_sessao_aula	Encerrar sessão
test_main_has_executar_menu	Verifica função principal
7. Cores (test_colors.py)
Teste	Descrição
test_colors_constants	Constantes de cor
test_print_c	Função print com cor
test_print_success	Mensagem de sucesso
test_print_error	Mensagem de erro
test_print_warning	Mensagem de aviso
test_print_info	Mensagem de informação
test_print_header	Cabeçalho formatado
🔧 Fixtures (conftest.py)
Fixture	Descrição
mock_db	Mock da sessão do banco de dados
sample_aluno_data	Dados de exemplo para aluno
sample_sessao_data	Dados de exemplo para sessão
sample_registro_data	Dados de exemplo para registro
📈 Cobertura por Arquivo
bash
docker exec -it explicaaso_app pytest tests/ --cov=src --cov-report=term --ignore=tests/unit/api/
Resultado atual:

Arquivo	Cobertura
cli/colors.py	100%
config/settings.py	100%
database/connection.py	100%
database/models.py	100%
database/repositories/presenca_repos.py	100%
services/presenca_service.py	100%
services/sgdi_service.py	100%
main.py	30%
TOTAL	70%
⚠️ Testes Skippados
Testes da API: Problema com TestClient e versão do Starlette

Testes interativos: Testes que aguardam input do usuário

🎯 Melhorias Futuras
Testar o menu principal (main.py) com monkeypatch para simular inputs

Corrigir testes da API atualizando versões do Starlette/httpx

Adicionar testes de integração com banco real

📚 Referências
Pytest Documentation

Pytest Coverage

SonarCloud Quality Gates
