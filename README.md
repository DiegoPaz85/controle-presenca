# 📚 ExpliCAASO - Sistema Unificado de Presença e Gestão de Alunos

O **ExpliCAASO** é um sistema robusto e seguro desenvolvido para unificar o controle de presença e a gestão de alunos do projeto. Ele substitui um ecossistema antigo baseado em planilhas soltas por uma arquitetura de software profissional baseada em microsserviços, conteinerização e banco de dados relacional.

---
## 📂 Estrutura do Projeto

Abaixo está a organização do repositório, seguindo padrões de modularização e separação de responsabilidades:

```text
controle-presenca-unificado/
├── docker/                  # Infraestrutura e Receitas Docker
│   ├── Dockerfile           # Imagem da aplicação Python
│   ├── docker-compose.yml   # Orquestração (App + Banco de Dados)
│   └── postgres_data/       # (Ignorado) Dados persistentes do DB
├── scripts/                 # Automações e Migrações
│   ├── backup.sh            # Script de Dump SQL e Upload Cloud
│   ├── migracao_excel.py    # Importação de alunos (BancoDeDados.xlsx)
│   └── migracao_presenca.py # Importação de histórico (presenca.xlsx)
├── src/                     # Código Fonte da Aplicação
│   └── controle_presenca/
│       ├── api/             # API REST (FastAPI)
│       ├── database/        # Conexão, Modelos e Repositórios
│       ├── services/        # Lógica de Negócio (Presença/SGDi)
│       └── main.py          # Ponto de entrada (CLI)
├── frontend/                # Frontend Web
│   ├── index.html           # Interface principal
│   ├── style.css            # Estilos
│   └── app.js               # Lógica do frontend
├── backups/                 # (Ignorado) Backups locais temporários
├── tests/                   # Testes automatizados
├── .env                     # (Ignorado) Cofre de senhas e credenciais
├── .gitignore               # Escudo de privacidade para o GitHub
└── requirements.txt         # Dependências do Python (Pandas, SQLAlchemy, etc)




🗺️ Arquitetura do Sistema

O diagrama abaixo ilustra o fluxo de dados e a infraestrutura do sistema, desde a interação física do aluno até o backup em nuvem:

graph TD
    %% Entradas Físicas e Usuários
    Aluno((🧑‍🎓 Aluno)) -->|Passa o Cartão| RFID[🔌 Leitor RFID]
    Admin((👨‍💻 Admin)) -->|Terminal / CLI| App
    Web((🌐 Usuário Web)) -->|Navegador| Frontend

    %% Ambiente Docker Local
    subgraph Host [Servidor Local / Xubuntu]
        RFID -->|Sinal| App
        Frontend[🖥️ Frontend Web] -->|Consome API| App

        subgraph Docker [🐳 Docker Network - Isolada]
            App[🐍 Aplicação Python<br/>API + Controle de Presença & SGDi]
            DB[(🐘 PostgreSQL<br/>Banco de Dados Central)]
            
            App <-->|SQLAlchemy ORM| DB
        end
        
        %% Segurança e Scripts
        Cofre[🔐 Arquivo .env<br/>Senhas Ocultas] -.-> Docker
        Bash[⚙️ backup.sh] -->|Extração Diária| DB
        Bash -->|Salva local| LocalBackup[📁 Pasta /backups]
    end

    %% Nuvem e Automação
    Cron((⏰ Cron Job)) -->|Meia-noite| Bash
    LocalBackup -->|Rclone / Token Auth| GDrive[☁️ Google Drive<br/>Backups_ExplicaASO]
    
    %% Estilização do Diagrama
    classDef nuvem fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px;
    classDef docker fill:#e3f2fd,stroke:#2196f3,stroke-width:2px;
    classDef database fill:#e8f5e9,stroke:#4caf50,stroke-width:2px;
    
    class GDrive nuvem;
    class Docker docker;
    class DB database;

✅ A arquitetura Unificada

🐳 Infraestrutura em Docker: Todo o ecossistema roda dentro de containers. Isso garante que o sistema funcione perfeitamente em qualquer computador, sem o problema de dependências perdidas.

🐘 PostgreSQL (Única Fonte da Verdade): Abolimos as planilhas. O PostgreSQL garante a Integridade Referencial dos dados, impedindo o registro de presença para um cartão não cadastrado.

🐍 Motor Python (SQLAlchemy + FastAPI): A aplicação utiliza o padrão ORM e oferece uma API REST completa, permitindo integração com frontend web.

🖥️ Frontend Web Moderno: Interface responsiva para registrar presença, gerenciar sessões e cadastrar alunos, tudo em tempo real.

🛡️ Segurança e Proteção de Dados (LGPD)
Como o sistema lida com dados reais (nomes, CPFs, e-mails), a segurança foi elevada a um padrão de produção:

    O Cofre (.env): Nenhuma senha de banco de dados fica escrita no código. Elas ficam num arquivo oculto, injetado no Docker apenas no momento da inicialização.

    O Escudo (.gitignore): O repositório Git foi configurado para ignorar qualquer dado sensível. Os dados dos alunos, os backups e as senhas ficam invisíveis e protegidos localmente.

    Isolamento de Rede: O banco de dados não tem portas abertas para o mundo exterior. Ele fica "trancado" dentro de uma rede virtual do Docker.

☁️ Automação e Resiliência (Disaster Recovery)
Para garantir que nenhuma aula ou batida de ponto seja perdida caso ocorra um problema físico no servidor:

    Extração Diária: Um script Bash entra no banco de dados e gera um pacote .sql com toda a estrutura e dados.

    Envio Seguro (Rclone): Utilizando tokens de autenticação (sem exigir a senha da conta), o pacote é enviado automaticamente para o Google Drive.

    O Despertador (Cron): O relógio interno do Linux executa essa rotina de backup de forma 100% autônoma, todos os dias à meia-noite.

🚀 Como Executar o Sistema
Pré-requisitos

Docker e Docker Compose instalados no servidor/máquina local.
1. Configuração Inicial

Clone o repositório e crie o seu cofre de senhas (.env) na raiz do projeto:

cp .env.example .env
# ou crie manualmente:
cat > .env << 'EOL'
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=explicaaso
DATABASE_URL=postgresql://seu_usuario:sua_senha@db:5432/explicaaso
DEBUG=true
LOG_LEVEL=INFO
EOL

2. Subindo a Infraestrutura

Na raiz do projeto, execute o comando para baixar as imagens e ligar os containers em segundo plano:
docker compose -f docker/docker-compose.yml up -d

3. Acessando o Sistema
Serviço	URL	Credenciais
🌐 Frontend Web	http://localhost:8000/	-
📚 API (Swagger)	http://localhost:8000/docs	-
📖 API (ReDoc)	http://localhost:8000/redoc	-
🐘 PgAdmin	http://localhost:5050/	admin@explicaaso.com / admin
💻 CLI (legado)	docker exec -it explicaaso_app python src/controle_presenca/main.py	-
4. Conectando o PgAdmin ao Banco

    Acesse http://localhost:5050/

    Login: admin@explicaaso.com / admin

    Clique em "Add New Server"

    Na aba "General": Name = Explicaaso DB

    Na aba "Connection":

        Host: explicaaso_db

        Port: 5432

        Username: postgres

        Password: (a senha do seu .env)

5. Criar as tabelas (primeira execução)

docker exec -it explicaaso_app python -c "
from src.controle_presenca.database.connection import engine
from src.controle_presenca.database.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Tabelas criadas!')
"

6. (Opcional) Migração de Dados Legados

Se precisar importar alunos de planilhas antigas (BancoDeDados.xlsx), coloque o arquivo na raiz do projeto e execute:
docker exec -it explicaaso_app python scripts/migracao_excel.py

🧪 Executando os Testes

# Executar todos os testes
docker exec -it explicaaso_app pytest tests/ --cov=src --cov-report=term --ignore=tests/unit/api/

# Ver relatório detalhado de cobertura
docker exec -it explicaaso_app pytest tests/ --cov=src --cov-report=term-missing --ignore=tests/unit/api/

🔧 Comandos Úteis

# Ver logs da API
docker logs explicaaso_app --tail 50

# Reiniciar apenas a API
docker compose -f docker/docker-compose.yml restart app

# Parar todos os containers
docker compose -f docker/docker-compose.yml down

# Parar e remover volumes (apaga dados do banco)
docker compose -f docker/docker-compose.yml down -v

# Acessar terminal do container
docker exec -it explicaaso_app bash

# Acessar PostgreSQL diretamente
docker exec -it explicaaso_db psql -U postgres -d explicaaso

📊 Qualidade do Código
Métrica	Status
SonarCloud Quality Gate	✅ Aprovado
Cobertura de Testes	70%
Testes Passando	61
Vulnerabilidades	0
Code Smells	0

