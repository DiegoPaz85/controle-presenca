# 📚 ExplicaASO - Sistema Unificado de Presença e Gestão de Alunos

O **ExplicaASO** é um sistema robusto e seguro desenvolvido para unificar o controle de presença e a gestão de alunos do projeto. Ele substitui um ecossistema antigo baseado em planilhas soltas por uma arquitetura de software profissional baseada em microsserviços, conteinerização e banco de dados relacional.

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
│       ├── database/        # Conexão, Modelos e Repositórios
│       ├── services/        # Lógica de Negócio (Presença/SGDi)
│       └── main.py          # Ponto de entrada (CLI)
├── backups/                 # (Ignorado) Backups locais temporários
├── .env                     # (Ignorado) Cofre de senhas e credenciais
├── .gitignore               # Escudo de privacidade para o GitHub
└── requirements.txt         # Dependências do Python (Pandas, SQLAlchemy, etc)




## 🗺️ Arquitetura do Sistema

O diagrama abaixo ilustra o fluxo de dados e a infraestrutura do sistema, desde a interação física do aluno até o backup em nuvem:

```mermaid
graph TD
    %% Entradas Físicas e Usuários
    Aluno((🧑‍🎓 Aluno)) -->|Passa o Cartão| RFID[🔌 Leitor RFID]
    Admin((👨‍💻 Admin)) -->|Terminal / CLI| App

    %% Ambiente Docker Local
    subgraph Host [Servidor Local / Xubuntu]
        RFID -->|Sinal| App
        
        subgraph Docker [🐳 Docker Network - Isolada]
            App[🐍 Aplicação Python<br/>Controle de Presença & SGDi]
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


📖 Entendendo a Evolução
❌ O Problema: A Arquitetura Antiga
Antigamente, o controle de presença e a gestão de alunos funcionavam como "ilhas" isoladas:

Armazenamento Frágil: Os dados ficavam espalhados em arquivos de Excel (BancoDeDados.xlsx e presenca.xlsx).

Falta de Integridade: Era possível ter uma batida de ponto de um aluno que já tinha sido apagado, gerando "dados fantasmas".

Segurança Baixa: As senhas e dados sensíveis ficavam expostos diretamente no código-fonte.

✅ A Solução: A Nova Arquitetura Unificada
O sistema foi completamente reescrito para utilizar as melhores práticas de Engenharia de Software:

🐳 Infraestrutura em Docker: Todo o ecossistema roda dentro de containers. Isso garante que o sistema funcione perfeitamente em qualquer computador, sem o problema de dependências perdidas.

🐘 PostgreSQL (Única Fonte da Verdade): Abolimos as planilhas. O PostgreSQL garante a Integridade Referencial dos dados, impedindo o registro de presença para um cartão não cadastrado.

🐍 Motor Python (SQLAlchemy): A aplicação utiliza o padrão ORM, o que significa que o código Python não precisa escrever SQL na mão, tornando a manutenção simples e o código limpo.

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

Snippet de código
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=explicaaso
DATABASE_URL=postgresql://seu_usuario:sua_senha@db:5432/explicaaso
2. Subindo a Infraestrutura
Na raiz do projeto, execute o comando para baixar as imagens e ligar os containers em segundo plano:

Bash
docker compose -f docker/docker-compose.yml up -d
3. Acessando o Sistema
Para abrir a interface de linha de comando (CLI) do Leitor de Presença, rode:

Bash
docker exec -it explicaaso_app python src/controle_presenca/main.py
4. (Opcional) Migração de Dados Legados
Se precisar importar alunos de planilhas antigas (BancoDeDados.xlsx), coloque o arquivo na raiz do projeto e execute:

Bash
docker exec -it explicaaso_app python scripts/migracao_excel.py
