# 📁 Organização do Projeto - FLUXO CASH

## 🎯 Estrutura Recomendada

Para manter o projeto organizado e separar ambientes de desenvolvimento/staging da produção, recomendamos a seguinte estrutura:

```
~/Documents/
├── FLUXOCASH-PRODUCAO/          # Projeto principal (branch main)
│   ├── backend/
│   ├── frontend/
│   ├── .git/
│   └── ...
│
└── FLUXOCASH-STAGING/           # Clone separado para staging
    ├── backend/
    ├── frontend/
    ├── .git/
    └── ...
```

## 🚀 Como Configurar

### 1. Renomear Pasta Atual (Opcional)

```bash
cd ~/Documents
mv FLUXOCASH-master FLUXOCASH-PRODUCAO
```

### 2. Criar Clone para Staging

```bash
cd ~/Documents
git clone https://github.com/Spywills/Fluxo-cash-Nader.git FLUXOCASH-STAGING
cd FLUXOCASH-STAGING
git checkout feature/authentication-system
```

### 3. Configurar Cada Ambiente

#### Produção (FLUXOCASH-PRODUCAO)
```bash
cd ~/Documents/FLUXOCASH-PRODUCAO

# Sempre usar branch main
git checkout main

# Backend usa .env (produção)
cd backend
# Configurar backend/.env com credenciais de PRODUÇÃO

# Frontend usa .env.production
cd ../frontend
# Configurar frontend/.env.production
```

#### Staging (FLUXOCASH-STAGING)
```bash
cd ~/Documents/FLUXOCASH-STAGING

# Sempre usar branch feature/authentication-system
git checkout feature/authentication-system

# Backend usa .env.staging
cd backend
# Já configurado com credenciais de staging

# Frontend usa .env.staging
cd ../frontend
# Já configurado para staging
```

## 📋 Workflow de Desenvolvimento

### Trabalhar em Staging

```bash
# 1. Ir para pasta de staging
cd ~/Documents/FLUXOCASH-STAGING

# 2. Garantir que está na branch correta
git checkout feature/authentication-system

# 3. Puxar últimas alterações
git pull origin feature/authentication-system

# 4. Fazer alterações
# ... editar código ...

# 5. Testar localmente
cd backend
./start_staging.sh &

cd ../frontend
npm run dev:staging

# 6. Commit e push
git add .
git commit -m "feat: descrição"
git push origin feature/authentication-system
```

### Promover para Produção

```bash
# 1. Ir para pasta de produção
cd ~/Documents/FLUXOCASH-PRODUCAO

# 2. Garantir que está na main
git checkout main

# 3. Fazer merge da branch de staging
git merge feature/authentication-system

# 4. Atualizar banco de produção
# Execute SQL no Supabase de produção

# 5. Criar usuário admin de produção
cd backend
export $(cat .env | xargs)
python create_admin_user.py

# 6. Push para produção
git push origin main

# 7. Deploy automático (Vercel + Railway)
```

## 🗂️ Arquivos por Ambiente

### Produção (main)
- `backend/.env` - Credenciais de produção
- `frontend/.env.production` - Config frontend produção
- Banco: Supabase de produção
- Deploy: Vercel + Railway

### Staging (feature/authentication-system)
- `backend/.env.staging` - Credenciais de staging
- `frontend/.env.staging` - Config frontend staging
- Banco: Supabase de staging
- Local: localhost:8000 + localhost:5174

## 🧹 Limpeza de Arquivos

### Arquivos que podem ser deletados (não commitados)

```bash
# Python
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Node
rm -rf frontend/node_modules
rm -rf frontend/dist

# Logs
find . -name "*.log" -delete

# Sistema
find . -name ".DS_Store" -delete

# Temporários
rm -rf backend/venv
rm -rf backend/.venv
```

### Arquivos que DEVEM ser commitados

- ✅ Código fonte (`.py`, `.js`, `.jsx`)
- ✅ Configurações (`.json`, `.toml`)
- ✅ Documentação (`.md`)
- ✅ Schemas (`.sql`)
- ✅ `.gitignore`
- ✅ `requirements.txt`, `package.json`

### Arquivos que NÃO devem ser commitados

- ❌ `.env` (produção - contém credenciais reais)
- ❌ `node_modules/`
- ❌ `venv/`, `.venv/`
- ❌ `__pycache__/`
- ❌ `*.pyc`, `*.pyo`
- ❌ `.DS_Store`
- ❌ `dist/`, `build/`
- ❌ `*.log`

**NOTA**: `.env.staging` pode ser commitado como EXEMPLO, mas nunca com credenciais reais de produção!

## 📝 Comandos Úteis

### Ver qual pasta você está
```bash
pwd
```

### Ver qual branch você está
```bash
git branch
```

### Ver status do git
```bash
git status
```

### Trocar entre pastas
```bash
# Ir para produção
cd ~/Documents/FLUXOCASH-PRODUCAO

# Ir para staging
cd ~/Documents/FLUXOCASH-STAGING
```

### Trocar entre branches
```bash
# Ir para produção (main)
git checkout main

# Ir para staging
git checkout feature/authentication-system
```

## 🎯 Resumo

| Aspecto | Produção | Staging |
|---------|----------|---------|
| **Pasta** | `FLUXOCASH-PRODUCAO` | `FLUXOCASH-STAGING` |
| **Branch** | `main` | `feature/authentication-system` |
| **Backend** | `.env` | `.env.staging` |
| **Frontend** | `.env.production` | `.env.staging` |
| **Banco** | Supabase Prod | Supabase Staging |
| **URL Backend** | Railway | localhost:8000 |
| **URL Frontend** | Vercel | localhost:5174 |
| **Dados** | Reais | Teste |

## ⚠️ Importante

1. **NUNCA** misture credenciais de produção e staging
2. **SEMPRE** verifique em qual pasta e branch você está antes de fazer alterações
3. **SEMPRE** teste em staging antes de promover para produção
4. **SEMPRE** faça backup do banco de produção antes de aplicar mudanças
5. **NUNCA** commite arquivos `.env` com credenciais reais de produção

## 🆘 Troubleshooting

### "Estou perdido, em qual ambiente estou?"

```bash
# Ver pasta atual
pwd

# Ver branch atual
git branch

# Ver remote
git remote -v
```

### "Quero começar do zero"

```bash
# Deletar pastas antigas
rm -rf ~/Documents/FLUXOCASH-PRODUCAO
rm -rf ~/Documents/FLUXOCASH-STAGING

# Clonar novamente
cd ~/Documents
git clone https://github.com/Spywills/Fluxo-cash-Nader.git FLUXOCASH-PRODUCAO
git clone https://github.com/Spywills/Fluxo-cash-Nader.git FLUXOCASH-STAGING

# Configurar branches
cd FLUXOCASH-PRODUCAO && git checkout main
cd ../FLUXOCASH-STAGING && git checkout feature/authentication-system
```

## 📚 Documentação Relacionada

- `SETUP_RAPIDO_STAGING.md` - Como rodar staging
- `AUTENTICACAO.md` - Sistema de autenticação
- `README.md` - Visão geral do projeto
