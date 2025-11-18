FROM python:3.9-slim

# Instalar dependências do sistema incluindo Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalação do Tesseract
RUN tesseract --version

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY backend/requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/ .

# Expor porta
EXPOSE 8000

# Comando para iniciar (Railway usa $PORT)
CMD uvicorn app.main_supabase:app --host 0.0.0.0 --port ${PORT:-8000}
