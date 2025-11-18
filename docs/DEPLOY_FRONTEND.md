# 🚀 Deploy do Frontend no Vercel

Guia completo para fazer deploy do frontend React no Vercel

---

## 📋 Pré-requisitos

- Backend já deployado no Render.com
- URL do backend (ex: `https://fluxocash-backend.onrender.com`)
- Conta no Vercel (gratuita)

---

## 🚀 Passo a Passo

### 1️⃣ Preparar o Projeto

O projeto já está configurado! Apenas certifique-se de que o backend está rodando.

### 2️⃣ Deploy no Vercel

#### Opção A: Via Dashboard (Recomendado)

1. Acesse: https://vercel.com
2. Faça login com **GitHub**
3. Clique em **"Add New..."** → **"Project"**
4. Selecione o repositório: **Spywills/Fluxo-cash-Nader**
5. Configure:

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

6. **Adicione Variável de Ambiente:**

```
Name: VITE_API_URL
Value: https://fluxocash-backend.onrender.com
```

⚠️ **IMPORTANTE:** Substitua pela URL real do seu backend no Render!

7. Clique em **"Deploy"**

#### Opção B: Via CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

Quando perguntar sobre variáveis de ambiente:
```
VITE_API_URL = https://fluxocash-backend.onrender.com
```

---

## 🔧 Configuração da Variável de Ambiente

### No Vercel Dashboard:

1. Vá em **Settings** → **Environment Variables**
2. Adicione:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://fluxocash-backend.onrender.com`
   - **Environment:** Production, Preview, Development

3. Clique em **"Save"**

4. **Redeploy** o projeto para aplicar as mudanças

---

## ✅ Verificar se Funcionou

Após o deploy:

1. Acesse a URL do Vercel (ex: `https://fluxocash.vercel.app`)
2. Abra o **Console do navegador** (F12)
3. Você deve ver: `🔗 API URL: https://fluxocash-backend.onrender.com`
4. Teste criar um cliente
5. Verifique se os dados aparecem

---

## 🔄 Atualizações Automáticas

Toda vez que você fizer push no GitHub:
- Vercel detecta automaticamente
- Faz rebuild
- Deploy automático
- Zero downtime

---

## 🌐 URLs Finais

Após o deploy, você terá:

```
Frontend: https://fluxocash.vercel.app
Backend:  https://fluxocash-backend.onrender.com
Database: https://xwshfeeobxgtvrbrfpyj.supabase.co
```

---

## 🔧 Configuração de CORS no Backend

O backend já está configurado para aceitar requisições de qualquer origem:

```python
origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "*",  # Aceita todas as origens
]
```

Se quiser restringir apenas para o Vercel, atualize no `backend/app/main_supabase.py`:

```python
origins = [
    "https://fluxocash.vercel.app",  # Sua URL do Vercel
    "http://localhost:5174",         # Desenvolvimento local
]
```

---

## 🆘 Problemas Comuns

### Erro: "Network Error" ou "Failed to fetch"

**Causa:** Backend não está acessível ou CORS bloqueado

**Solução:**
1. Verifique se o backend está rodando: `https://seu-backend.onrender.com/health`
2. Verifique a variável `VITE_API_URL` no Vercel
3. Verifique CORS no backend

### Erro: "404 Not Found"

**Causa:** Rota não existe no backend

**Solução:**
1. Verifique se a URL da API está correta
2. Teste a rota diretamente: `https://seu-backend.onrender.com/clients`

### Frontend carrega mas não mostra dados

**Causa:** Variável de ambiente não configurada

**Solução:**
1. Vá em Vercel → Settings → Environment Variables
2. Adicione `VITE_API_URL`
3. Redeploy o projeto

---

## 📊 Monitoramento

### No Vercel:
- Ver logs de build
- Ver analytics
- Ver performance

### No Render (Backend):
- Ver logs em tempo real
- Ver métricas de CPU/RAM
- Ver requisições

---

## 💰 Custos

**Vercel (Frontend):**
- ✅ Gratuito para projetos pessoais
- ✅ 100 GB bandwidth/mês
- ✅ Builds ilimitados

**Render (Backend):**
- ✅ Gratuito (750 horas/mês)
- ⚠️ Servidor dorme após 15 min

**Supabase (Database):**
- ✅ Gratuito (500 MB storage)
- ✅ 2 GB bandwidth/mês

**Total: R$ 0,00/mês** 🎉

---

## ✅ Checklist Final

- [ ] Backend deployado no Render
- [ ] URL do backend anotada
- [ ] Frontend deployado no Vercel
- [ ] Variável `VITE_API_URL` configurada
- [ ] Site acessível e funcionando
- [ ] Teste de criar cliente OK
- [ ] Teste de upload de comprovante OK
- [ ] Teste de depósito OK

**Pronto! Seu sistema está no ar! 🎉**

---

## 🔗 Links Úteis

- Vercel Dashboard: https://vercel.com/dashboard
- Render Dashboard: https://dashboard.render.com
- Supabase Dashboard: https://supabase.com/dashboard
- Documentação Vite: https://vitejs.dev/guide/env-and-mode.html
