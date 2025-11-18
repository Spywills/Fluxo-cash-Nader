# ⚡ Setup Rápido - Staging (Passo a Passo)

## ✅ Credenciais Já Configuradas

O arquivo `backend/.env.staging` já está configurado com:
- ✅ SUPABASE_URL: https://jqisqohwilhtlikwgbdz.supabase.co
- ✅ SUPABASE_KEY: eyJhbGci... (configurado)
- ✅ JWT_SECRET_KEY: configurado

## 📋 Passo 1: Criar Tabelas no Supabase

### 1.1 Acesse o SQL Editor do Supabase

Abra este link:
```
https://supabase.com/dashboard/project/jqisqohwilhtlikwgbdz/sql
```

### 1.2 Clique em "New Query"

### 1.3 Cole o SQL abaixo e execute:

```sql
-- ============================================
-- FLUXO CASH - Database Schema for Supabase
-- PostgreSQL Database
-- ============================================

-- Tabela de Usuários (Sistema de Login)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para usuários
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

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

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas tabelas
COMMENT ON TABLE users IS 'Tabela de usuários do sistema (login/autenticação)';
COMMENT ON TABLE clients IS 'Tabela de clientes do sistema';
COMMENT ON TABLE proofs IS 'Tabela de comprovantes enviados pelos clientes';
COMMENT ON TABLE transactions IS 'Tabela de transações (depósitos e saques)';

COMMENT ON COLUMN proofs.deposited IS 'Flag para indicar se o comprovante já foi creditado';
COMMENT ON COLUMN proofs.extraction_status IS 'Status da extração: UPLOADED, EXTRACTING, EXTRACTED, FAILED, MANUAL_ENTRY';
COMMENT ON COLUMN transactions.type IS 'Tipo da transação: DEPOSIT ou WITHDRAWAL';
COMMENT ON COLUMN transactions.status IS 'Status da transação: PENDING, COMPLETED, REJECTED';
```

### 1.4 Clique em "Run" (ou Ctrl+Enter)

Você deve ver: "Success. No rows returned"

## 📋 Passo 2: Instalar Dependências do Backend

```bash
cd backend

# Criar virtual environment (se não tiver)
python3 -m venv venv

# Ativar virtual environment
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 📋 Passo 3: Criar Usuário Admin

```bash
# Certifique-se de estar no diretório backend com venv ativado
cd backend
source venv/bin/activate

# Carregar variáveis de ambiente
export SUPABASE_URL="https://jqisqohwilhtlikwgbdz.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpxaXNxb2h3aWxodGxpa3dnYmR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0ODY4MzAsImV4cCI6MjA3OTA2MjgzMH0.WWXdugcr77is2XpWQkCcY3bWmmjcK3Gt_Woiqf1PAwg"
export JWT_SECRET_KEY="fluxo-cash-staging-secret-key-2025-change-in-production"

# Criar usuário admin
python create_admin_user.py
```

Preencha quando solicitado:
```
Username: admin
Email: admin@staging.local
Senha: admin123
Nome completo: Admin Staging
Usuário administrador? (s/n): s
```

## 📋 Passo 4: Iniciar Backend

```bash
# No diretório backend com venv ativado
cd backend
source venv/bin/activate

# Carregar variáveis (mesmo comando do passo 3)
export SUPABASE_URL="https://jqisqohwilhtlikwgbdz.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpxaXNxb2h3aWxodGxpa3dnYmR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0ODY4MzAsImV4cCI6MjA3OTA2MjgzMH0.WWXdugcr77is2XpWQkCcY3bWmmjcK3Gt_Woiqf1PAwg"
export JWT_SECRET_KEY="fluxo-cash-staging-secret-key-2025-change-in-production"

# Iniciar servidor
uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
```

Deve aparecer:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ FLUXO CASH Backend (Supabase) iniciado com sucesso
```

## 📋 Passo 5: Instalar Dependências do Frontend

**Em outro terminal:**

```bash
cd frontend

# Instalar dependências (se ainda não instalou)
npm install
```

## 📋 Passo 6: Iniciar Frontend

```bash
# No diretório frontend
cd frontend

# Iniciar em modo staging
npm run dev:staging
```

Deve aparecer:
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:5174/
```

## 📋 Passo 7: Testar

1. Abra o navegador: http://localhost:5174
2. Você verá a tela de login
3. Faça login com:
   - **Username**: `admin`
   - **Password**: `admin123`
4. Teste as funcionalidades

## ✅ Checklist de Testes

- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Criar cliente
- [ ] Editar cliente
- [ ] Deletar cliente
- [ ] Upload de comprovante
- [ ] Criar saque
- [ ] Aprovar saque
- [ ] Ver histórico
- [ ] Logout funciona

## 🆘 Problemas Comuns

### Backend não inicia - "ModuleNotFoundError"
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend não conecta
Verifique se o backend está rodando:
```bash
curl http://localhost:8000/health
```

### "Token inválido"
Limpe o localStorage do navegador:
- Abra DevTools (F12)
- Application > Local Storage
- Clear All
- Recarregue a página

### Porta 8000 ocupada
```bash
# Encontrar processo
lsof -i :8000

# Matar processo
kill -9 [PID]
```

## 📝 Comandos Úteis

### Testar Backend
```bash
# Health check
curl http://localhost:8000/health

# Testar login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Ver Logs
```bash
# Backend mostra logs no terminal onde está rodando
# Frontend mostra logs no navegador (DevTools > Console)
```

## 🎉 Pronto!

Agora você tem o sistema de autenticação rodando em staging!

**Próximo passo**: Testar tudo antes de fazer merge para produção.

---

**Dúvidas?** Consulte `AUTENTICACAO.md` para documentação completa.
