# 🚀 Deploy no Render.com (RECOMENDADO)

Guia completo para fazer deploy do backend FastAPI no Render.com

---

## ✅ Por que Render.com?

- ✅ **Gratuito** (750 horas/mês)
- ✅ **Suporta FastAPI perfeitamente**
- ✅ **Upload de arquivos funciona**
- ✅ **OCR/Tesseract disponível**
- ✅ **Banco de dados PostgreSQL integrado**
- ✅ **SSL automático**
- ✅ **Logs em tempo real**

---

## 📋 Pré-requisitos

- Conta no GitHub (código já está lá)
- Conta no Render.com (gratuita)
- Credenciais do Supabase

---

## 🚀 Passo a Passo

### 1️⃣ Criar Conta no Render

1. Acesse: https://render.com
2. Clique em **"Get Started"**
3. Faça login com **GitHub**
4. Autorize o Render a acessar seus repositórios

### 2️⃣ Criar Novo Web Service

1. No dashboard, clique em **"New +"**
2. Selecione **"Web Service"**
3. Conecte seu repositório: **Spywills/Fluxo-cash-Nader**
4. Clique em **"Connect"**

### 3️⃣ Configurar o Serviço

Preencha os campos:

```
Name: fluxocash-backend
Region: Oregon (US West)
Branch: main
Root Directory: (deixe vazio)
Runtime: Python 3
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && uvicorn app.main_supabase:app --host 0.0.0.0 --port $PORT
```

### 4️⃣ Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, adicione:

```
SUPABASE_URL = https://xwshfeeobxgtvrbrfpyj.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DEBUG = False
PYTHON_VERSION = 3.9.0
```

### 5️⃣ Escolher Plano

- Selecione **"Free"** (gratuito)
- Clique em **"Create Web Service"**

### 6️⃣ Aguardar Deploy

- ⏳ O deploy leva 2-5 minutos
- 📊 Você pode ver os logs em tempo real
- ✅ Quando terminar, aparecerá "Live"

### 7️⃣ Testar a API

Sua API estará disponível em:
```
https://fluxocash-backend.onrender.com
```

Teste:
```bash
curl https://fluxocash-backend.onrender.com/health
```

Deve retornar:
```json
{
  "status": "ok",
  "service": "FLUXO CASH",
  "database": "Supabase PostgreSQL"
}
```

---

## 🔧 Configurar Frontend

Atualize o arquivo `frontend/src/services/api.js`:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'https://fluxocash-backend.onrender.com';
```

Ou crie `.env` no frontend:
```
VITE_API_URL=https://fluxocash-backend.onrender.com
```

---

## 📊 Monitoramento

No dashboard do Render você pode:
- ✅ Ver logs em tempo real
- ✅ Monitorar uso de recursos
- ✅ Ver métricas de requisições
- ✅ Configurar alertas

---

## 🔄 Atualizações Automáticas

Toda vez que você fizer push no GitHub:
1. Render detecta automaticamente
2. Faz rebuild
3. Deploy automático
4. Zero downtime

---

## ⚠️ Limitações do Plano Free

- 750 horas/mês (suficiente para 1 app)
- Servidor "dorme" após 15 min de inatividade
- Primeira requisição após dormir leva ~30s
- 512 MB RAM

**Solução para o "sleep":**
- Use um serviço de ping (UptimeRobot, cron-job.org)
- Ou upgrade para plano pago ($7/mês)

---

## 🆘 Problemas Comuns

### Erro: "Build failed"
**Solução:** Verifique se o `requirements.txt` está correto

### Erro: "Port already in use"
**Solução:** Use `$PORT` no start command (Render injeta automaticamente)

### Erro: "Module not found"
**Solução:** Verifique o `Root Directory` e `Start Command`

---

## 📚 Recursos

- 📖 Documentação: https://render.com/docs
- 💬 Suporte: https://render.com/support
- 🎓 Tutoriais: https://render.com/docs/deploy-fastapi

---

## ✅ Checklist Final

- [ ] Conta criada no Render
- [ ] Repositório conectado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído com sucesso
- [ ] API testada e funcionando
- [ ] Frontend atualizado com nova URL
- [ ] Tudo funcionando end-to-end

**Pronto! Seu backend está no ar! 🎉**
