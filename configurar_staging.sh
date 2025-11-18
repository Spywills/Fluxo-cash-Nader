#!/bin/bash

# Script para configurar a pasta FLUXOCASH - TESTE como ambiente de staging

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🚀 CONFIGURANDO AMBIENTE DE STAGING                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

STAGING_DIR="/Users/franciscocavalcanti/Documents/FLUXOCASH - TESTE"

# Verificar se a pasta existe
if [ ! -d "$STAGING_DIR" ]; then
    echo "❌ Erro: Pasta $STAGING_DIR não encontrada!"
    exit 1
fi

echo "📁 Configurando: $STAGING_DIR"
echo ""

# Ir para a pasta
cd "$STAGING_DIR"

# Configurar git remote
echo "1️⃣  Configurando git remote..."
git remote add origin https://github.com/Spywills/Fluxo-cash-Nader.git 2>/dev/null || git remote set-url origin https://github.com/Spywills/Fluxo-cash-Nader.git
echo "✅ Remote configurado"
echo ""

# Fazer fetch
echo "2️⃣  Fazendo fetch do repositório..."
git fetch origin
echo "✅ Fetch concluído"
echo ""

# Criar branch local tracking a branch remota
echo "3️⃣  Configurando branch feature/authentication-system..."
git checkout -b feature/authentication-system origin/feature/authentication-system 2>/dev/null || git checkout feature/authentication-system
echo "✅ Branch configurada"
echo ""

# Adicionar todos os arquivos
echo "4️⃣  Adicionando arquivos..."
git add -A
echo "✅ Arquivos adicionados"
echo ""

# Verificar status
echo "5️⃣  Status do git:"
git status --short | head -10
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ✅ STAGING CONFIGURADO COM SUCESSO!                        ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Pasta de staging: $STAGING_DIR"
echo "🌿 Branch: feature/authentication-system"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "   1. Ir para a pasta de staging:"
echo "      cd \"$STAGING_DIR\""
echo ""
echo "   2. Instalar dependências do backend:"
echo "      cd backend"
echo "      pip3 install -r requirements.txt"
echo ""
echo "   3. Instalar dependências do frontend:"
echo "      cd frontend"
echo "      npm install"
echo ""
echo "   4. Iniciar backend:"
echo "      cd backend"
echo "      ./start_staging.sh"
echo ""
echo "   5. Iniciar frontend (outro terminal):"
echo "      cd frontend"
echo "      npm run dev:staging"
echo ""
