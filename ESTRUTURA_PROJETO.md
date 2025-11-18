# 📁 Estrutura do Projeto - FLUXO CASH

## 🎯 Organização Atual

```
~/Documents/
├── FLUXOCASH-master/              # ← PRODUÇÃO (branch: main)
│   ├── backend/
│   ├── frontend/
│   ├── docs/
│   └── .git/
│
└── FLUXOCASH - TESTE/             # ← STAGING (branch: feature/authentication-system)
    ├── backend/
    ├── frontend/
    ├── docs/
    └── .git/
```

## 🚀 Como Usar

### Trabalhar em STAGING (Desenvolvimento)

```bash
# 1. Ir para pasta de staging
cd ~/Documents/FLUXOCASH\ -\ TESTE

# 2. Verificar branch
git branch
# Deve mostrar: feature/authentication-system

# 3. Fazer alterações
# ... editar código ...

# 4. Testar localmente
cd backend
./start_staging.sh

# Em outro terminal
cd frontend
npm run dev:staging

# 5. Commit e push
git add .
git commit -m "feat: descrição"
git push origin feature/authentication-system
```

### Trabalhar em PRODUÇÃO

```bash
# 1. Ir para pasta de produção
cd ~/Documents/FLUXOCASH-master

# 2. Verificar branch
git branch
# Deve mostrar: main

# 3. Fazer merge do staging (após testar)
git merge feature/authentication-system

# 4. Push para produção
git push origin main
```

## 📊 Diferenças entre Ambientes

| Aspecto | Produção | Staging |
|---------|----------|---------|
| **Pasta** | `FLUXOCASH-master` | `FLUXOCASH - TESTE` |
| **Branch** | `main` | `feature/authentication-system` |
| **Banco** | Supabase Produção | Supabase Staging |
| **Backend Config** | `.env` | `.env.staging` |
| **Frontend Config** | `.env.production` | `.env.staging` |
| **URL Backend** | Railway/Render | localhost:8000 |
| **URL Frontend** | Vercel | localhost:5174 |
| **Dados** | Reais | Teste |

## 🔧 Configuração Inicial

### Staging já está configurado!

O script `configurar_staging.sh` já foi executado e configurou:
- ✅ Git inicializado
- ✅ Remote configurado
- ✅ Branch feature/authentication-system
- ✅ Arquivos copiados

### Para instalar dependências:

```bash
# Backend
cd ~/Documents/FLUXOCASH\ -\ TESTE/backend
pip3 install -r requirements.txt

# Frontend
cd ~/Documents/FLUXOCASH\ -\ TESTE/frontend
npm install
```

## 📝 Workflow Recomendado

1. **Desenvolver em STAGING**
   - Fazer todas as alterações em `FLUXOCASH - TESTE`
   - Testar localmente
   - Commit e push para `feature/authentication-system`

2. **Validar em STAGING**
   - Rodar testes
   - Verificar funcionalidades
   - Corrigir bugs

3. **Promover para PRODUÇÃO**
   - Ir para `FLUXOCASH-master`
   - Fazer merge da branch de staging
   - Atualizar banco de produção
   - Push para `main`
   - Deploy automático

## ⚠️ Importante

- **NUNCA** misture credenciais de produção e staging
- **SEMPRE** teste em staging antes de promover para produção
- **SEMPRE** faça backup do banco de produção antes de mudanças
- **SEMPRE** verifique em qual pasta você está: `pwd`
- **SEMPRE** verifique em qual branch você está: `git branch`

## 🆘 Comandos Úteis

```bash
# Ver onde você está
pwd

# Ver qual branch
git branch

# Ver status
git status

# Ir para staging
cd ~/Documents/FLUXOCASH\ -\ TESTE

# Ir para produção
cd ~/Documents/FLUXOCASH-master
```

## 📚 Documentação

Toda a documentação está em `docs/`:
- `docs/GUIA_RAPIDO_STAGING.md` - Como rodar staging
- `docs/AUTENTICACAO.md` - Sistema de autenticação
- `docs/ORGANIZACAO_PROJETO.md` - Organização detalhada

---

**Tudo pronto!** Agora você tem ambientes completamente separados para desenvolvimento e produção.
