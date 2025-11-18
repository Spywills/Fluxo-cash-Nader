# ⚡ Guia Rápido - Staging do Sistema de Autenticação

## 🎯 Situação Atual

Você está na branch `feature/authentication-system` com:
- ✅ Sistema de autenticação completo implementado
- ✅ Ambiente de staging configurado
- ✅ Documentação completa criada

## 🚀 Como Começar (5 minutos)

### 1. Executar Setup Automático

```bash
./setup-staging.sh
```

Este script vai:
- Verificar arquivos de configuração
- Criar virtual environment (se necessário)
- Instalar dependências
- Mostrar próximos passos

### 2. Configurar Supabase de Staging

**Opção A: Criar Novo Projeto (Recomendado)**

1. Acesse: https://supabase.com/dashboard
2. Clique em "New Project"
3. Nome: `fluxocash-staging`
4. Aguarde criação (2-3 min)
5. Vá em SQL Editor
6. Cole e execute: `backend/database_schema.sql`
7. Vá em Settings > API
8. Copie URL e Key para `backend/.env.staging`

**Opção B: Usar Projeto Existente**

Se quiser usar o mesmo projeto Supabase:
- Execute apenas o SQL no mesmo banco
- Use as mesmas credenciais

### 3. Editar backend/.env.staging

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET_KEY=minha-chave-secreta-staging-123
ENVIRONMENT=staging
```

### 4. Criar Usuário Admin

```bash
cd backend
export $(cat .env.staging | xargs)
python create_admin_user.py
```

Preencha:
```
Username: admin
Email: admin@staging.local
Senha: admin123
Nome completo: Admin Staging
Usuário administrador? s
```

### 5. Iniciar Backend

```bash
cd backend
export $(cat .env.staging | xargs)
uvicorn app.main_supabase:app --reload
```

Deve aparecer:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ FLUXO CASH Backend (Supabase) iniciado com sucesso
```

### 6. Iniciar Frontend (Novo Terminal)

```bash
cd frontend
npm run dev:staging
```

Deve aparecer:
```
VITE v5.0.8  ready in 500 ms
➜  Local:   http://localhost:5174/
```

### 7. Testar

1. Abra: http://localhost:5174
2. Faça login com: `admin` / `admin123`
3. Teste as funcionalidades

## 📋 Checklist de Testes

Teste estas funcionalidades:

### Autenticação
- [ ] Login com credenciais corretas → ✅ Deve entrar
- [ ] Login com senha errada → ❌ Deve mostrar erro
- [ ] Criar nova conta → ✅ Deve criar e pedir login
- [ ] Logout → ✅ Deve voltar para tela de login

### Funcionalidades Existentes
- [ ] Dashboard carrega
- [ ] Criar cliente
- [ ] Editar cliente
- [ ] Deletar cliente
- [ ] Upload de comprovante
- [ ] Criar saque
- [ ] Aprovar saque
- [ ] Ver histórico

## 🔄 Workflow Diário

### Fazer Alterações

```bash
# 1. Certifique-se de estar na branch correta
git checkout feature/authentication-system

# 2. Fazer alterações no código
# ... editar arquivos ...

# 3. Testar localmente
cd backend && export $(cat .env.staging | xargs) && uvicorn app.main_supabase:app --reload
cd frontend && npm run dev:staging

# 4. Commit
git add .
git commit -m "feat: descrição da alteração"

# 5. Push (opcional)
git push origin feature/authentication-system
```

## 📤 Quando Estiver Pronto para Produção

### Pré-requisitos
- [ ] Todos os testes passaram
- [ ] Código revisado
- [ ] Documentação atualizada
- [ ] Backup do banco de produção criado

### Processo de Deploy

```bash
# 1. Voltar para main
git checkout main

# 2. Merge da branch de staging
git merge feature/authentication-system

# 3. Atualizar banco de PRODUÇÃO
# No Supabase de produção, execute: backend/database_schema.sql

# 4. Criar usuário admin de PRODUÇÃO
cd backend
export $(cat .env | xargs)  # .env de PRODUÇÃO!
python create_admin_user.py

# Use credenciais DIFERENTES de staging:
# Username: admin
# Email: admin@fluxocash.com
# Senha: [senha forte e diferente]

# 5. Push para produção
git push origin main

# 6. Deploy automático
# Vercel e Railway vão fazer deploy automaticamente

# 7. Testar em produção
# Acesse a URL de produção e teste login
```

## 🆘 Problemas Comuns

### "Tabela users não existe"
```bash
# Execute o SQL no Supabase
# Vá em SQL Editor e cole backend/database_schema.sql
```

### "SUPABASE_URL não configurado"
```bash
# Verifique o arquivo
cat backend/.env.staging

# Carregue as variáveis
export $(cat backend/.env.staging | xargs)

# Teste
echo $SUPABASE_URL
```

### "Token inválido"
```bash
# Limpe o localStorage do navegador
# Abra DevTools > Application > Local Storage > Clear All
# Faça login novamente
```

### Backend não inicia
```bash
# Verifique dependências
cd backend
pip install -r requirements.txt

# Verifique se porta 8000 está livre
lsof -i :8000
# Se estiver ocupada: kill -9 [PID]
```

### Frontend não conecta
```bash
# Verifique se backend está rodando
curl http://localhost:8000/health

# Deve retornar:
# {"status":"ok","service":"FLUXO CASH","database":"Supabase PostgreSQL"}
```

## 📚 Documentação Completa

- **Sistema de Autenticação**: `AUTENTICACAO.md`
- **Setup Detalhado**: `SETUP_STAGING.md`
- **Guia da Branch**: `README_STAGING.md`

## 🎯 Comandos Úteis

```bash
# Ver branch atual
git branch

# Trocar para staging
git checkout feature/authentication-system

# Trocar para produção
git checkout main

# Ver status
git status

# Ver logs
git log --oneline -5

# Testar endpoint de login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Testar health check
curl http://localhost:8000/health
```

## ✅ Pronto!

Agora você tem:
- ✅ Branch separada para desenvolvimento
- ✅ Ambiente de staging configurado
- ✅ Sistema de autenticação funcionando
- ✅ Documentação completa
- ✅ Processo de deploy definido

**Próximo passo**: Testar tudo em staging antes de fazer merge para produção!

---

**Dúvidas?** Consulte `SETUP_STAGING.md` para mais detalhes.
