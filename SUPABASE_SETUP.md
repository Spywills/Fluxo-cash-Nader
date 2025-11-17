# 🗄️ Configuração do Supabase

Guia passo a passo para configurar o banco de dados PostgreSQL no Supabase.

## 📋 Pré-requisitos

- Conta no Supabase (gratuita): https://supabase.com

## 🚀 Passo 1: Criar Projeto no Supabase

1. Acesse https://supabase.com e faça login
2. Clique em "New Project"
3. Preencha:
   - **Name**: fluxocash (ou nome de sua preferência)
   - **Database Password**: Crie uma senha forte
   - **Region**: Escolha a região mais próxima
4. Clique em "Create new project"
5. Aguarde alguns minutos até o projeto ser criado

## 🗃️ Passo 2: Criar as Tabelas

1. No painel do Supabase, vá em **SQL Editor** (menu lateral)
2. Clique em "New query"
3. Copie todo o conteúdo do arquivo `backend/database_schema.sql`
4. Cole no editor SQL
5. Clique em "Run" (ou pressione Ctrl+Enter)
6. Verifique se apareceu "Success. No rows returned"

## 🔑 Passo 3: Obter as Credenciais

1. No painel do Supabase, vá em **Settings** > **API**
2. Copie as seguintes informações:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## ⚙️ Passo 4: Configurar o Backend

1. Crie um arquivo `.env` na pasta `backend/`:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edite o arquivo `.env` e adicione suas credenciais:
   ```env
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_KEY=sua-anon-key-aqui
   DEBUG=True
   PORT=8000
   ```

## 📦 Passo 5: Instalar Dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar dependências atualizadas
pip install -r backend/requirements.txt
```

## ✅ Passo 6: Testar a Conexão

```bash
cd backend
python -c "from app.database import init_database; print('✅ Conexão OK!' if init_database() else '❌ Erro na conexão')"
```

## 🔄 Passo 7: Migrar Dados (Opcional)

Se você já tem dados no sistema em memória e quer migrar para o Supabase, execute:

```bash
cd backend
python migrate_to_supabase.py
```

## 📊 Verificar Tabelas Criadas

No Supabase, vá em **Table Editor** e você deve ver:
- ✅ `clients` - Tabela de clientes
- ✅ `proofs` - Tabela de comprovantes
- ✅ `transactions` - Tabela de transações

## 🔒 Segurança (Row Level Security)

Por padrão, o Supabase ativa RLS (Row Level Security). Para desenvolvimento, você pode desativar temporariamente:

1. Vá em **Authentication** > **Policies**
2. Para cada tabela (clients, proofs, transactions):
   - Clique em "New Policy"
   - Escolha "Enable access to all users"
   - Salve

**⚠️ IMPORTANTE**: Em produção, configure políticas de segurança adequadas!

## 🎯 Próximos Passos

Após configurar o Supabase:
1. Reinicie o backend
2. O sistema agora usará o banco de dados PostgreSQL
3. Todos os dados serão persistidos
4. Você pode acessar e gerenciar os dados pelo painel do Supabase

## 🆘 Problemas Comuns

### Erro: "SUPABASE_URL and SUPABASE_KEY must be set"
- Verifique se o arquivo `.env` existe na pasta `backend/`
- Confirme que as variáveis estão corretas

### Erro: "relation does not exist"
- Execute novamente o script SQL no SQL Editor
- Verifique se todas as tabelas foram criadas

### Erro de conexão
- Verifique sua conexão com a internet
- Confirme se a URL do Supabase está correta
- Verifique se o projeto está ativo no painel do Supabase

## 📚 Recursos

- Documentação Supabase: https://supabase.com/docs
- Supabase Python Client: https://github.com/supabase-community/supabase-py
