# 🚀 Como Rodar o FLUXO CASH

## Pré-requisitos

- Python 3.9+
- Node.js 18+
- Tesseract OCR instalado (para extração de texto de imagens)

### Instalar Tesseract (macOS)
```bash
brew install tesseract
```

## 1️⃣ Backend (FastAPI)

### Criar ambiente virtual e instalar dependências
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r backend/requirements.txt
```

### Iniciar servidor backend
```bash
# A partir da raiz do projeto
source venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

O backend estará disponível em: **http://127.0.0.1:8000**

### Testar backend
```bash
curl http://127.0.0.1:8000/health
# Resposta esperada: {"status":"ok","service":"FLUXO CASH"}
```

## 2️⃣ Frontend (React + Vite)

### Instalar dependências
```bash
cd frontend
npm install
```

### Iniciar servidor frontend
```bash
npm run dev
```

O frontend estará disponível em: **http://localhost:5174**

## 🎯 Acessar a aplicação

Abra seu navegador e acesse: **http://localhost:5174**

## 📊 Estrutura de URLs

- **Frontend**: http://localhost:5174
- **Backend API**: http://127.0.0.1:8000
- **Documentação API**: http://127.0.0.1:8000/docs (Swagger UI)

## 🛑 Parar os servidores

### Backend
Pressione `CTRL+C` no terminal do backend

### Frontend
Pressione `CTRL+C` no terminal do frontend

## 🔧 Troubleshooting

### Erro: "Tesseract is not installed"
```bash
# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr

# Windows
# Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
```

### Erro: "Port 8000 already in use"
```bash
# Encontrar processo usando a porta
lsof -ti:8000

# Matar processo
kill -9 $(lsof -ti:8000)
```

### Erro: "Port 5174 already in use"
```bash
# Encontrar processo usando a porta
lsof -ti:5174

# Matar processo
kill -9 $(lsof -ti:5174)
```

## 📝 Comandos Úteis

### Backend
```bash
# Ver logs do backend
tail -f backend/logs/app.log

# Listar todas as rotas
curl http://127.0.0.1:8000/openapi.json | jq '.paths | keys'
```

### Frontend
```bash
# Build para produção
npm run build

# Preview do build
npm run preview
```

## ✅ Status Atual

- ✅ Backend rodando em http://127.0.0.1:8000
- ✅ Frontend rodando em http://localhost:5174
- ✅ Comunicação entre frontend e backend funcionando
- ✅ Tesseract OCR instalado e configurado

## 🎉 Pronto!

O projeto está rodando e pronto para uso!
