# 🚀 Setup de Ambiente de Staging - FLUXO CASH

## Visão Geral

Este guia explica como configurar um ambiente de staging separado para testar o sistema de autenticação antes de ir para produção.

## Estrutura de Branches

```
main (produção)
  └── feature/authentication-system (desenvolvimento/staging)
```

## 1. Criar Banco de Dados de Staging no Supabase

### Opção A: Criar Novo Projeto Supabase (Recomendado)

1. Acesse https://supabase.com/dashboard
2. Clique em "New Project"
3. Configure:
   - **Name**: `fluxocash-staging`
   - **Database Password**: Escolha uma senha forte
   - **Region**: Mesma da produção
4. Aguarde a criação (2-3 minutos)

### Opção B: Usar Schema Separado no Mesmo Banco

Se preferir usar o mesmo projeto Supabase:

```sql
-- Criar schema de staging
CREATE SCHEMA IF NOT EXISTS staging;

-- Definir search_path para staging
SET search_path TO staging, public;

-- Executar todo o database_schema.sql dentro do schema staging
```

## 2. Configurar Banco de Staging

### Executar Schema no Supabase

1. Acesse o SQL Editor do projeto staging
2. Cole o conteúdo de `backend/database_schema.sql`
3. Execute o script
4. Verifique se as tabelas foram criadas:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';
```

Você deve ver:
- `users`
- `clients`
- `proofs`
- `transactions`

## 3. Configurar Variáveis de Ambiente

### Backend - Staging

Edite `backend/.env.staging`:

```env
# Supabase - Staging
SUPABASE_URL=https://seu-projeto-staging.supabase.co
SUPABASE_KEY=sua-chave-anon-staging

# JWT Secret (diferente da produção!)
JWT_SECRET_KEY=staging-secret-key-muito-segura-aqui

# Ambiente
ENVIRONMENT=staging
```

Para obter as credenciais do Supabase:
1. Vá em Settings > API
2. Copie:
   - **Project URL** → `SUPABASE_URL`
   - **anon/public key** → `SUPABASE_KEY`

### Frontend - Staging

Edite `frontend/.env.staging`:

```env
VITE_API_URL=http://localhost:8000
VITE_ENV=staging
```

## 4. Criar Usuário Admin de Staging

```bash
# Usar o arquivo .env.staging
export $(cat backend/.env.staging | xargs)

# Criar usuário admin
python backend/create_admin_user.py
```

Exemplo de credenciais para staging:
```
Username: admin-staging
Email: admin@staging.fluxocash.com
Senha: staging123
Nome completo: Admin Staging
Usuário administrador? s
```

## 5. Executar Ambiente de Staging

### Backend

```bash
cd backend

# Carregar variáveis de staging
export $(cat .env.staging | xargs)

# Instalar dependências (se ainda não instalou)
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências (se ainda não instalou)
npm install

# Iniciar com configuração de staging
npm run dev -- --mode staging
```

Ou adicione um script no `package.json`:

```json
{
  "scripts": {
    "dev": "vite",
    "dev:staging": "vite --mode staging",
    "build": "vite build",
    "build:staging": "vite build --mode staging"
  }
}
```

Então execute:
```bash
npm run dev:staging
```

## 6. Testar o Sistema

### Checklist de Testes

- [ ] **Login**
  - [ ] Login com credenciais corretas
  - [ ] Login com credenciais incorretas
  - [ ] Mensagens de erro apropriadas

- [ ] **Registro**
  - [ ] Criar novo usuário
  - [ ] Validação de campos obrigatórios
  - [ ] Validação de senha (mínimo 6 caracteres)
  - [ ] Verificar duplicação de username/email

- [ ] **Autenticação**
  - [ ] Token é salvo no localStorage
  - [ ] Token é enviado nas requisições
  - [ ] Redirecionamento ao expirar token
  - [ ] Logout funciona corretamente

- [ ] **Proteção de Rotas**
  - [ ] Endpoints protegidos retornam 401 sem token
  - [ ] Endpoints funcionam com token válido
  - [ ] Usuário não-admin não acessa rotas admin

- [ ] **Funcionalidades Existentes**
  - [ ] Dashboard carrega corretamente
  - [ ] CRUD de clientes funciona
  - [ ] Upload de comprovantes funciona
  - [ ] Saques funcionam
  - [ ] Histórico funciona

## 7. Workflow de Desenvolvimento

### Fazer Alterações

```bash
# Certifique-se de estar na branch correta
git checkout feature/authentication-system

# Fazer alterações
# ... editar arquivos ...

# Commit
git add .
git commit -m "feat: adicionar funcionalidade X"
```

### Testar em Staging

```bash
# Backend
cd backend
export $(cat .env.staging | xargs)
uvicorn app.main_supabase:app --reload

# Frontend (outro terminal)
cd frontend
npm run dev:staging
```

### Quando Estiver Pronto para Produção

```bash
# 1. Certifique-se que todos os testes passaram
# 2. Merge na main
git checkout main
git merge feature/authentication-system

# 3. Atualizar banco de produção
# Execute database_schema.sql no Supabase de produção

# 4. Criar usuário admin de produção
export $(cat backend/.env | xargs)
python backend/create_admin_user.py

# 5. Deploy
git push origin main
```

## 8. Diferenças entre Ambientes

| Aspecto | Staging | Produção |
|---------|---------|----------|
| **Branch** | `feature/authentication-system` | `main` |
| **Banco** | Supabase Staging | Supabase Produção |
| **URL Backend** | `localhost:8000` | URL do Railway/Render |
| **URL Frontend** | `localhost:5174` | Vercel URL |
| **JWT Secret** | Chave de staging | Chave de produção |
| **Dados** | Dados de teste | Dados reais |

## 9. Boas Práticas

### Dados de Teste

Crie dados de teste realistas em staging:

```bash
# Script para popular staging com dados de teste
python backend/scripts/seed_staging_data.py
```

### Não Misturar Ambientes

- ❌ Nunca use banco de produção em staging
- ❌ Nunca use JWT secret de produção em staging
- ✅ Mantenha credenciais separadas
- ✅ Use prefixos claros (admin-staging vs admin)

### Backup Antes de Merge

```bash
# Backup do banco de produção antes de aplicar mudanças
# No Supabase: Database > Backups > Create Backup
```

## 10. Troubleshooting

### Erro: "Tabela users não existe"

Execute o schema atualizado no banco de staging:
```sql
-- No SQL Editor do Supabase
-- Cole e execute backend/database_schema.sql
```

### Erro: "SUPABASE_URL não configurado"

Verifique se o `.env.staging` está configurado e carregado:
```bash
cat backend/.env.staging
export $(cat backend/.env.staging | xargs)
echo $SUPABASE_URL
```

### Frontend não conecta ao backend

Verifique se o backend está rodando:
```bash
curl http://localhost:8000/health
```

Verifique o `.env.staging` do frontend:
```bash
cat frontend/.env.staging
```

### Token expira muito rápido

Ajuste em `backend/app/auth.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
```

## 11. Próximos Passos

Após validar em staging:

1. [ ] Todos os testes passaram
2. [ ] Documentação atualizada
3. [ ] Backup do banco de produção criado
4. [ ] Merge para main
5. [ ] Deploy em produção
6. [ ] Criar usuário admin de produção
7. [ ] Testar em produção
8. [ ] Monitorar logs

## Comandos Rápidos

```bash
# Trocar para branch de staging
git checkout feature/authentication-system

# Iniciar staging completo
cd backend && export $(cat .env.staging | xargs) && uvicorn app.main_supabase:app --reload &
cd frontend && npm run dev:staging

# Ver logs do backend
tail -f backend/logs/app.log

# Criar backup do banco
# Fazer no dashboard do Supabase

# Merge para produção (quando pronto)
git checkout main
git merge feature/authentication-system
git push origin main
```

## Suporte

Para dúvidas:
- Consulte `AUTENTICACAO.md` para detalhes do sistema
- Verifique logs do backend e frontend
- Teste endpoints com Postman/Insomnia
