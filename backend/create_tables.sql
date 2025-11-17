-- Criar tabelas do FLUXO CASH
-- Execute este SQL no SQL Editor do Supabase

-- Tabela de Clientes
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    document VARCHAR(50),
    notes TEXT,
    saldo DECIMAL(15, 2) DEFAULT 0.00,
    total_deposits DECIMAL(15, 2) DEFAULT 0.00,
    total_withdrawals DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Comprovantes
CREATE TABLE proofs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000),
    file_type VARCHAR(100),
    file_size INTEGER,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    description TEXT,
    is_duplicate BOOLEAN DEFAULT FALSE,
    original_proof_id INTEGER REFERENCES proofs(id),
    extracted_value DECIMAL(15, 2),
    extraction_confidence DECIMAL(3, 2) DEFAULT 0.00,
    extraction_status VARCHAR(50) DEFAULT 'UPLOADED',
    beneficiary VARCHAR(255),
    endtoend VARCHAR(255),
    deposited BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Transações
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    proof_id INTEGER REFERENCES proofs(id) ON DELETE SET NULL,
    amount DECIMAL(15, 2) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('DEPOSIT', 'WITHDRAWAL')),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'REJECTED')),
    description TEXT,
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Desativar RLS para desenvolvimento
ALTER TABLE clients DISABLE ROW LEVEL SECURITY;
ALTER TABLE proofs DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
