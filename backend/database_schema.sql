-- ============================================
-- FLUXO CASH - Database Schema for Supabase
-- PostgreSQL Database
-- ============================================

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS clients (
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
CREATE TABLE IF NOT EXISTS proofs (
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

-- Tabela de Transações (Depósitos e Saques)
CREATE TABLE IF NOT EXISTS transactions (
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

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_proofs_client_id ON proofs(client_id);
CREATE INDEX IF NOT EXISTS idx_proofs_file_hash ON proofs(file_hash);
CREATE INDEX IF NOT EXISTS idx_proofs_deposited ON proofs(deposited);
CREATE INDEX IF NOT EXISTS idx_transactions_client_id ON transactions(client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas tabelas
COMMENT ON TABLE clients IS 'Tabela de clientes do sistema';
COMMENT ON TABLE proofs IS 'Tabela de comprovantes enviados pelos clientes';
COMMENT ON TABLE transactions IS 'Tabela de transações (depósitos e saques)';

COMMENT ON COLUMN proofs.deposited IS 'Flag para indicar se o comprovante já foi creditado';
COMMENT ON COLUMN proofs.extraction_status IS 'Status da extração: UPLOADED, EXTRACTING, EXTRACTED, FAILED, MANUAL_ENTRY';
COMMENT ON COLUMN transactions.type IS 'Tipo da transação: DEPOSIT ou WITHDRAWAL';
COMMENT ON COLUMN transactions.status IS 'Status da transação: PENDING, COMPLETED, REJECTED';
