# 🔐 Branch: feature/authentication-system

Esta branch contém o desenvolvimento do **Sistema de Autenticação** do FLUXO CASH.

## ⚠️ IMPORTANTE

Esta é uma branch de **desenvolvimento/staging**. Não faça merge para `main` sem antes:

1. ✅ Testar completamente em ambiente de staging
2. ✅ Validar todos os endpoints de autenticação
3. ✅ Verificar compatibilidade com funcionalidades existentes
4. ✅ Criar backup do banco de produção
5. ✅ Revisar código com o time

## 🎯 O que foi implementado

### Backend
- ✅ Tabela `users` no banco de dados
- ✅ Sistema de autenticação JWT
- ✅ Hash de senhas com bcrypt
- ✅ Endpoints: `/auth/login`, `/auth/register`, `/auth/me`, `/auth/logout`
- ✅ Proteção de rotas com middleware de autenticação
- ✅ Script para criar usuário admin

### Frontend
- ✅ Tela de login/registro
- ✅ Gerenciamento de tokens JWT
- ✅ Interceptors axios para autenticação automática
- ✅ Proteção de rotas no frontend
- ✅ Exibição de informações do usuário no header
- ✅ Botão de logout

### Documentação
- ✅ `AUTENTICACAO.md` - Documentação completa do sistema
- ✅ `SETUP_STAGING.md` - Guia de configuração de staging
- ✅ `setup-staging.sh` - Script automatizado de setup

## 🚀 Quick Start - Staging

### 1. Executar Setup Automático

```bash
./setup-staging.sh
```

### 2. Configurar Supabase Staging

1. Crie um novo projeto no Supabase (ou use schema separado)
2. Execute `backend/database_schema.sql` no SQL Editor
3. Configure `backend/.env.staging` com as credenciais

### 3. Criar Usuário Admin

```bash
cd backend
export $(cat .env.staging | xargs)
python create_admin_user.py
```

### 4. Iniciar Servidores

**Backend:**
```bash
cd backend
export $(cat .env.staging | xargs)
uvicorn app.main_supabase:app --reload
```

**Frontend (outro terminal):**
```bash
cd frontend
npm run dev:staging
```

### 5. Acessar

Abra http://localhost:5174 e faça login com as credenciais criadas.

## 📁 Arquivos Modificados

### Novos Arquivos
```
backend/app/auth.py                 # Módulo de autenticação
backend/create_admin_user.py        # Script para criar admin
backend/.env.staging                # Config de staging
frontend/src/pages/Login.jsx        # Tela de login
frontend/.env.staging               # Config frontend staging
AUTENTICACAO.md                     # Documentação
SETUP_STAGING.md                    # Guia de staging
setup-staging.sh                    # Script de setup
```

### Arquivos Modificados
```
backend/database_schema.sql         # + tabela users
backend/requirements.txt            # + dependências auth
backend/app/main_supabase.py        # + endpoints auth
frontend/src/App.jsx                # + lógica de autenticação
frontend/src/components/Header.jsx  # + info usuário e logout
frontend/src/services/api.js        # + interceptors JWT
frontend/package.json               # + scripts staging
```

## 🧪 Testes Necessários

Antes de fazer merge para produção, teste:

### Autenticação
- [ ] Login com credenciais válidas
- [ ] Login com credenciais inválidas
- [ ] Registro de novo usuário
- [ ] Validação de campos (email, senha, etc)
- [ ] Token expira após 24h
- [ ] Logout funciona corretamente

### Proteção de Rotas
- [ ] Endpoints retornam 401 sem token
- [ ] Endpoints funcionam com token válido
- [ ] Redirecionamento automático ao expirar token

### Funcionalidades Existentes
- [ ] Dashboard carrega corretamente
- [ ] CRUD de clientes funciona
- [ ] Upload de comprovantes funciona
- [ ] Criação de saques funciona
- [ ] Aprovação de saques funciona
- [ ] Histórico funciona
- [ ] Resumo bancário funciona

### Segurança
- [ ] Senhas são hasheadas (nunca em texto plano)
- [ ] Tokens JWT são válidos
- [ ] CORS configurado corretamente
- [ ] Validação de entrada funciona

## 📊 Estrutura do Banco - Staging

```sql
-- Nova tabela
users (
    id, username, email, password_hash,
    full_name, is_active, is_admin,
    last_login, created_at, updated_at
)

-- Tabelas existentes (sem alteração)
clients (...)
proofs (...)
transactions (...)
```

## 🔄 Workflow de Desenvolvimento

### Fazer Alterações

```bash
# Certifique-se de estar na branch correta
git checkout feature/authentication-system

# Fazer alterações
# ... editar código ...

# Commit
git add .
git commit -m "feat: descrição da alteração"

# Push
git push origin feature/authentication-system
```

### Testar em Staging

```bash
# Sempre teste antes de fazer merge!
./setup-staging.sh
# ... seguir instruções ...
```

### Merge para Produção (quando pronto)

```bash
# 1. Certifique-se que tudo foi testado
# 2. Faça backup do banco de produção
# 3. Merge

git checkout main
git merge feature/authentication-system

# 4. Atualizar banco de produção
# Execute database_schema.sql no Supabase de produção

# 5. Criar usuário admin de produção
cd backend
export $(cat .env | xargs)
python create_admin_user.py

# 6. Push
git push origin main

# 7. Deploy automático (Vercel + Railway)
```

## 🔐 Credenciais de Staging

**NUNCA** commite credenciais reais. Use valores de exemplo:

```
Username: admin-staging
Email: admin@staging.local
Senha: staging123
```

## 📚 Documentação

- **Sistema de Autenticação**: `AUTENTICACAO.md`
- **Setup de Staging**: `SETUP_STAGING.md`
- **Detecção de Duplicatas**: `DETECCAO_DUPLICATAS.md`
- **Fluxo de Comprovantes**: `FLUXO_COMPROVANTE.md`

## 🆘 Troubleshooting

### Erro: "Tabela users não existe"
Execute o schema atualizado no banco de staging.

### Erro: "Token inválido"
Verifique se o JWT_SECRET_KEY está configurado corretamente.

### Frontend não conecta
Verifique se o backend está rodando em `http://localhost:8000`.

### Mais problemas?
Consulte `SETUP_STAGING.md` seção "Troubleshooting".

## 📞 Contato

Para dúvidas sobre esta branch:
- Consulte a documentação em `AUTENTICACAO.md`
- Revise o código em `backend/app/auth.py`
- Teste os endpoints com Postman/Insomnia

---

**Status**: 🚧 Em Desenvolvimento
**Última Atualização**: 2025-11-18
**Próximo Passo**: Testes completos em staging
