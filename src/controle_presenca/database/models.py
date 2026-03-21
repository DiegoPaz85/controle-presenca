CREATE_TABLES_SQL = """
-- Tabela de alunos
CREATE TABLE IF NOT EXISTS alunos (
    id SERIAL PRIMARY KEY,
    cartao_id INTEGER UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    senha VARCHAR(10) UNIQUE NOT NULL,
    status VARCHAR(10) DEFAULT 'ATIVADO',
    carga_horaria_total FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de sessões
CREATE TABLE IF NOT EXISTS sessoes (
    id SERIAL PRIMARY KEY,
    inicio TIMESTAMP NOT NULL,
    fim TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ativa',
    tempo_efetivo FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de intervalos
CREATE TABLE IF NOT EXISTS intervalos (
    id SERIAL PRIMARY KEY,
    sessao_id INTEGER REFERENCES sessoes(id) ON DELETE CASCADE,
    inicio TIMESTAMP NOT NULL,
    fim TIMESTAMP,
    duracao FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de registros
CREATE TABLE IF NOT EXISTS registros (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER REFERENCES alunos(id) ON DELETE CASCADE,
    sessao_id INTEGER REFERENCES sessoes(id) ON DELETE SET NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tempo_presenca FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_alunos_cartao ON alunos(cartao_id);
CREATE INDEX IF NOT EXISTS idx_alunos_senha ON alunos(senha);
CREATE INDEX IF NOT EXISTS idx_registros_aluno ON registros(aluno_id);
CREATE INDEX IF NOT EXISTS idx_registros_sessao ON registros(sessao_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_status ON sessoes(status);
"""

def criar_tabelas():
    from .connection import db
    db.execute(CREATE_TABLES_SQL)
    print("✅ Tabelas criadas/verificadas")

def inserir_dados_iniciais():
    from .connection import db
    
    # Inserir alunos de exemplo
    db.execute("""
        INSERT INTO alunos (cartao_id, nome, senha, status) VALUES
            (1, 'ANA LAURA DE CASTRO RODRIGUES', '1', 'ATIVADO'),
            (2, 'NICOLLY ZANELLI FHAL', '2', 'ATIVADO'),
            (3, 'AMANDA APARECIDA GONÇALO MÁXIMO', '3', 'ATIVADO'),
            (4, 'RODRIGO MARIANO CAMPANER JUNIOR', '4', 'ATIVADO'),
            (5, 'LINDA KETLIN REIS DA SILVA', '5', 'ATIVADO')
        ON CONFLICT (cartao_id) DO NOTHING;
    """)
    print("✅ Dados iniciais inseridos")
