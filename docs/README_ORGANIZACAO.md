# 🎯 Guia Rápido de Organização

## 📁 Estrutura Recomendada

```
~/Documents/
├── FLUXOCASH-PRODUCAO/          # ← Produção (branch main)
└── FLUXOCASH-STAGING/           # ← Staging/Desenvolvimento
```

## 🚀 Organizar Automaticamente

Execute o script de organização:

```bash
./organizar_projeto.sh
```

Este script irá:
1. ✅ Renomear pasta atual para `FLUXOCASH-PRODUCAO`
2. ✅ Criar clone separado `FLUXOCASH-STAGING`
3. ✅ Configurar branches corretas
4. ✅ Limpar arquivos temporários

## 📋 Ou Fazer Manualmente

### 1. Renomear Pasta Atual

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

### 3. Configurar Produção

```bash
cd ~/Documents/FLUXOCASH-PRODUCAO
git checkout main
```

## 🎯 Como Usar

### Trabalhar em Staging

```bash
cd ~/Documents/FLUXOCASH-STAGING

# Iniciar backend
cd backend
./start_staging.sh

# Iniciar frontend (outro terminal)
cd frontend
npm run dev:staging
```

### Trabalhar em Produção

```bash
cd ~/Documents/FLUXOCASH-PRODUCAO
git checkout main

# Fazer alterações apenas após testar em staging!
```

## 📚 Documentação Completa

- **ORGANIZACAO_PROJETO.md** - Guia completo de organização
- **SETUP_RAPIDO_STAGING.md** - Como rodar staging
- **AUTENTICACAO.md** - Sistema de autenticação

## ⚠️ Importante

- ✅ Sempre teste em **STAGING** primeiro
- ✅ Só promova para **PRODUÇÃO** após validar
- ❌ Nunca misture credenciais de staging e produção
- ❌ Nunca commite arquivos `.env` com credenciais reais

## 🆘 Ajuda

Se estiver perdido, execute:

```bash
# Ver onde você está
pwd

# Ver qual branch
git branch

# Ver status
git status
```

---

**Dúvidas?** Leia `ORGANIZACAO_PROJETO.md` para detalhes completos.
