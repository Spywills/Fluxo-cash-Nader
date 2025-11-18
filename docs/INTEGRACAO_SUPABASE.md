# 🗄️ Guia de Integração com Supabase

Guia completo e passo a passo para integrar o FLUXO CASH com Supabase PostgreSQL.

---

## 📋 O que você vai precisar

- ✅ Conta no Supabase (gratuita)
- ✅ 10-15 minutos
- ✅ Acesso à internet

---

## 🚀 PASSO 1: Criar Projeto no Supabase

### 1.1 Criar Conta
1. Acesse: https://supabase.com
2. Clique em **"Start your project"**
3. Faça login com:
   - GitHub (recomendado)
   - Google
   - Email

### 1.2 Criar Novo Projeto
1. No dashboard, clique em **"New Project"**
2. Preencha os dados:

```
┌─────────────────────────────────────────┐
│ Organization: [Sua organização]         │
│ Name: fluxocash                         │
│ Database Password: [senha forte]        │ ← ANOTE ESTA SENHA!
│ Region: South America (São Paulo)       │
│ Pricing Plan: Free                      │
└─────────────────────────────────────────┘
```

3. Clique em **"Create new project"**
4. ⏳ Aguarde 2-3 minutos (o projeto está sendo criado)

---

## 🗃️ PASSO 2: Criar as Tabelas

### 2.1 Abrir SQL Editor
1. No menu lateral, clique em **"SQL Editor"**
2. Clique em **"New query"**

### 2.2 Executar Script SQL
1. Abra o arquivo `backend/database_schema.sql` no seu editor
2. **Copie TODO o conteúdo** (Ctrl+A, Ctrl+C)
3. **Cole no SQL Editor** do Supabase (Ctrl+V)
4. Clique em **"Run"** (ou pressione Ctrl+Enter)

### 2.3 Verificar Sucesso
Você deve ver:
```
✅ Success. No rows returned
```

### 2.4 Verificar Tabelas Criadas
1. No menu lateral, clique em **"Table Editor"**
2. Você deve ver 3 tabelas:
   - ✅ `clients`
   - ✅ `proofs`
   - ✅ `transactions`

---

## 🔑 PASSO 3: Obter Credenciais

### 3.1 Acessar Configurações
1. No menu lateral, clique em **"Settings"** (ícone de engrenagem)
2. Clique em **"API"**

### 3.2 Copiar Credenciais

Você verá duas informações importantes:

```
┌─────────────────────────────────────────────────────────┐
│ Project URL                                             │
│ https://xxxxxxxxxxxxx.supabase.co                       │
│ [Copy]                                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Project API keys                                        │
│                                                         │
│ anon/public                                             │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJz...  │
│ [Copy]                                                  │
└─────────────────────────────────────────────────────────┘
```

**Copie:**
1. ✅ **Project URL** (clique em Copy)
2. ✅ **anon/public key** (clique em Copy)

---

## ⚙️ PASSO 4: Configurar Backend

### 4.1 Instalar Dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar dependências do Supabase
pip install supabase python-dotenv psycopg2-binary
```

### 4.2 Criar Arquivo .env

```bash
cd backend
cp .env.example .env
```

### 4.3 Editar .env com suas Credenciais

Abra o arquivo `backend/.env` e cole suas credenciais:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Application Settings
DEBUG=True
PORT=8000
```

**⚠️ IMPORTANTE:**
- Substitua `xxxxxxxxxxxxx` pela sua URL real
- Substitua a key pela sua chave real (anon/public)
- NÃO compartilhe este arquivo!

---

## ✅ PASSO 5: Testar Conexão

### 5.1 Executar Script de Teste

```bash
cd backend
python -c "from app.database import init_database; print('✅ Conexão OK!' if init_database() else '❌ Erro na conexão')"
```

**Resultado esperado:**
```
✅ Conexão OK!
```

**Se der erro:**
- Verifique se o arquivo `.env` está na pasta `backend/`
- Confirme se as credenciais estão corretas
- Verifique sua conexão com a internet

### 5.2 Executar Migração (Opcional)

Se você já tem dados no sistema em memória:

```bash
cd backend
python migrate_to_supabase.py
```

---

## 🔄 PASSO 6: Atualizar main.py para usar Supabase

Agora precisamos modificar o `backend/app/main.py` para usar o banco de dados ao invés dos dicionários em memória.

**Vou fazer isso no próximo passo!**

---

## 🔒 PASSO 7: Configurar Segurança (RLS)

Por padrão, o Supabase ativa Row Level Security (RLS). Para desenvolvimento, vamos desativar temporariamente:

### 7.1 Desativar RLS (Desenvolvimento)

No SQL Editor do Supabase, execute:

```sql
-- Desativar RLS para desenvolvimento
ALTER TABLE clients DISABLE ROW LEVEL SECURITY;
ALTER TABLE proofs DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
```

**⚠️ IMPORTANTE:** Em produção, configure políticas de segurança adequadas!

---

## 📊 PASSO 8: Verificar Dados no Supabase

### 8.1 Visualizar Tabelas
1. Vá em **"Table Editor"**
2. Clique em cada tabela para ver os dados
3. Você pode adicionar, editar e deletar dados diretamente

### 8.2 Executar Queries
1. Vá em **"SQL Editor"**
2. Execute queries para verificar:

```sql
-- Ver todos os clientes
SELECT * FROM clients;

-- Ver todos os comprovantes
SELECT * FROM proofs;

-- Ver todas as transações
SELECT * FROM transactions;

-- Estatísticas
SELECT 
    COUNT(*) as total_clients,
    SUM(saldo) as saldo_total
FROM clients;
```

---

## 🎯 Resumo dos Arquivos Criados

```
backend/
├── .env                      ← Suas credenciais (NÃO commitar!)
├── .env.example              ← Template
├── database_schema.sql       ← SQL para criar tabelas
├── migrate_to_supabase.py    ← Script de migração
└── app/
    ├── database.py           ← Conexão com Supabase
    └── db_helpers.py         ← Funções auxiliares
```

---

## 🆘 Problemas Comuns

### Erro: "SUPABASE_URL and SUPABASE_KEY must be set"
**Solução:**
- Verifique se o arquivo `.env` existe em `backend/.env`
- Confirme que as variáveis estão corretas
- Reinicie o terminal

### Erro: "relation does not exist"
**Solução:**
- Execute novamente o SQL do `database_schema.sql`
- Verifique se todas as 3 tabelas foram criadas

### Erro: "Failed to connect"
**Solução:**
- Verifique sua conexão com internet
- Confirme se a URL do Supabase está correta
- Verifique se o projeto está ativo no painel

### Erro: "Invalid API key"
**Solução:**
- Use a chave **anon/public**, não a service_role
- Copie novamente do painel do Supabase
- Verifique se não tem espaços extras

---

## 📚 Recursos Úteis

- 📖 Documentação Supabase: https://supabase.com/docs
- 🐍 Supabase Python Client: https://github.com/supabase-community/supabase-py
- 💬 Supabase Discord: https://discord.supabase.com
- 🎓 Tutoriais: https://supabase.com/docs/guides

---

## ✅ Checklist Final

Antes de continuar, confirme:

- [ ] ✅ Projeto criado no Supabase
- [ ] ✅ Tabelas criadas (clients, proofs, transactions)
- [ ] ✅ Credenciais copiadas (URL + Key)
- [ ] ✅ Arquivo `.env` criado e configurado
- [ ] ✅ Dependências instaladas
- [ ] ✅ Teste de conexão passou
- [ ] ✅ RLS desativado (desenvolvimento)

**Se todos os itens estão ✅, você está pronto para o próximo passo!**

---

## 🚀 Próximo Passo

Agora vamos modificar o `main.py` para usar o Supabase ao invés dos dicionários em memória.

**Me avise quando terminar estes passos e eu faço a integração no código!**
