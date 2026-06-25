# 📚 ExpliCAASO - Sistema Unificado de Presença e Gestão de Alunos

O **ExpliCAASO** é um sistema robusto e seguro desenvolvido para unificar o controle de presença e a gestão de alunos do cursinho. Ele substitui um ecossistema antigo baseado em planilhas soltas por uma arquitetura de software profissional baseada em microsserviços, conteinerização e banco de dados relacional.

---
## 📂 Estrutura do Projeto

Abaixo está a organização principal do repositório, seguindo padrões de modularização (Clean Architecture) e separação de responsabilidades:

```text
controle-presenca/
├── alembic/                 # Ferramenta de migração e versionamento de banco (Alembic)
├── docker/                  # Infraestrutura e Receitas Docker (App + DB + PgAdmin)
├── frontend/                # Interfaces Web Isoladas
│   ├── gestor.html / .js    # Painel Administrativo (Processo Seletivo, Relatórios)
│   ├── leitor.html / .js    # Terminal Kiosk (Leitor de Código de Barras)
│   └── style.css            # Estilos globais
├── scripts/                 # Automações e Migrações
│   ├── backup.sh            # Script de extração e upload para nuvem
│   └── popular_gabarito.py  # Injeta pesos e critérios do processo seletivo
├── src/                     # Código Fonte da Aplicação (FastAPI)
│   └── controle_presenca/
│       ├── api/             # Roteadores REST (Sessão, Presença, SGDI, Alunos, Relatórios)
│       ├── database/        # Conexão, Modelos (SQLAlchemy)
│       └── services/        # Regras de Negócio (SGDiService, CartolaMagicaService, etc)
├── tests/                   # Cobertura de testes unitários e de integração
├── Makefile                 # Orquestrador de comandos rápidos
└── .env                     # (Ignorado no Git) Cofre de senhas e credenciais


	🗺️ Arquitetura do Sistema

O fluxo de dados foi projetado para ser assíncrono e à prova de falhas:

graph TD
    %% Entradas
    Aluno((🧑‍🎓 Aluno)) -->|Passa o Cartão| RFID[🔌 Leitor RFID]
    Admin((👨‍💻 Admin)) -->|Terminal Web| Gestor[🖥️ Painel do Gestor]
    
    RFID -->|Bip / Enter| Leitor[🖥️ Terminal do Leitor]

    %% Ambiente Local
    subgraph Host [Servidor Local]
        Leitor -->|Consome API| App
        Gestor -->|Consome API| App

        subgraph Docker [🐳 Docker Network - Isolada]
            App[🐍 Aplicação FastAPI<br/>Sessões, Presença e SGDI]
            DB[(🐘 PostgreSQL<br/>Banco Central)]
            
            App <-->|SQLAlchemy ORM| DB
        end
    end

    %% Background Tasks
    App -.->|Background Task| Email[📧 Disparo Automático de E-mails]
    
    
    🚀 Como Executar o Sistema (Primeira Vez)
Pré-requisitos

    Docker e Docker Compose instalados.

    Make instalado (Nativamente disponível no Linux/Mac).

1. Configuração do Cofre de Senhas (.env)

Clone o repositório e crie o seu arquivo de credenciais na raiz do projeto:

cat > .env << 'EOL'
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=explicaaso
DATABASE_URL=postgresql://seu_usuario:sua_senha@explicaaso_db:5432/explicaaso
PLANILHA_INSCRICAO_URL=sua_url_do_google_forms_aqui
DEBUG=true
EOL


2. Subindo a Infraestrutura com Mágica (Makefile)

Esqueça comandos longos. O projeto possui um Makefile que constrói os contêineres, sobe o banco de dados, roda as migrações do Alembic e injeta os gabaritos de forma 100% automatizada.

Na raiz do projeto, rode:

make up

3. Acessando as Interfaces

Com o sistema rodando, os seguintes portais estarão disponíveis no seu navegador:

Serviço	URL de Acesso	Descrição:
📍 Terminal do Leitor	http://localhost:8000/static/leitor.html	Tela para a porta da sala de aula.
📊 Painel do Gestor	http://localhost:8000/static/gestor.html	Tela administrativa (SGDI e Frequência).
⚙️ API (Swagger)	http://localhost:8000/docs	Documentação interativa dos endpoints.
🐘 Banco (PgAdmin)	http://localhost:5051/	Interface de gestão do banco de dados.

(Nota: O login padrão do PgAdmin está configurado no docker-compose.yml e a conexão interna deve usar o host explicaaso_db).



🔧 Comandos Úteis do Dia a Dia

O Makefile concentra tudo o que você precisa para gerenciar o projeto:

make logs       # Abre o monitor de logs em tempo real do FastAPI
make down       # Derruba os contêineres com segurança
make restart    # Executa o make down e o make up em sequência

Se precisar criar uma nova tabela no banco de dados, basta adicionar o modelo no Python e rodar a migração via Alembic pelo contêiner:

docker exec -it explicaaso_app alembic revision --autogenerate -m "nome_da_alteracao"
docker exec -it explicaaso_app alembic upgrade head





