#!/usr/bin/env bash
# Render build script

echo "📦 Instalando dependências do sistema..."

# Instalar Tesseract OCR e Poppler (para PDFs)
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-por poppler-utils

echo "✅ Tesseract e Poppler instalados!"

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r backend/requirements.txt

echo "✅ Build concluído!"
