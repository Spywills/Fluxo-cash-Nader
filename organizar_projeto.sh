#!/bin/bash

# Script para organizar o projeto FLUXO CASH
# Cria estrutura separada para produção e staging

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   📁 ORGANIZAÇÃO DO PROJETO FLUXO CASH                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se estamos no diretório correto
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Erro: Execute este script na raiz do projeto (onde está o .git)${NC}"
    exit 1
fi

CURRENT_DIR=$(pwd)
PARENT_DIR=$(dirname "$CURRENT_DIR")
PROJECT_NAME=$(basename "$CURRENT_DIR")

echo "📍 Diretório atual: $CURRENT_DIR"
echo "📂 Nome do projeto: $PROJECT_NAME"
echo ""

# Perguntar ao usuário
echo "Este script irá:"
echo "  1. Renomear esta pasta para: FLUXOCASH-PRODUCAO"
echo "  2. Criar clone separado em: FLUXOCASH-STAGING"
echo "  3. Configurar branches corretas"
echo ""
read -p "Deseja continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "🚀 Iniciando organização..."
echo ""

# 1. Renomear pasta atual
echo "1️⃣  Renomeando pasta atual..."
cd "$PARENT_DIR"
if [ -d "FLUXOCASH-PRODUCAO" ]; then
    echo -e "${YELLOW}⚠️  Pasta FLUXOCASH-PRODUCAO já existe!${NC}"
    read -p "Deseja sobrescrever? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf FLUXOCASH-PRODUCAO
    else
        echo "Operação cancelada."
        exit 0
    fi
fi

mv "$PROJECT_NAME" FLUXOCASH-PRODUCAO
echo -e "${GREEN}✅ Pasta renomeada para FLUXOCASH-PRODUCAO${NC}"
echo ""

# 2. Criar clone para staging
echo "2️⃣  Criando clone para staging..."
if [ -d "FLUXOCASH-STAGING" ]; then
    echo -e "${YELLOW}⚠️  Pasta FLUXOCASH-STAGING já existe!${NC}"
    read -p "Deseja sobrescrever? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        rm -rf FLUXOCASH-STAGING
    else
        echo "Pulando criação de staging..."
        cd FLUXOCASH-PRODUCAO
        git checkout main
        echo ""
        echo -e "${GREEN}✅ Organização concluída!${NC}"
        exit 0
    fi
fi

# Obter URL do remote
cd FLUXOCASH-PRODUCAO
REMOTE_URL=$(git remote get-url origin)
cd ..

echo "📥 Clonando de: $REMOTE_URL"
git clone "$REMOTE_URL" FLUXOCASH-STAGING
echo -e "${GREEN}✅ Clone criado em FLUXOCASH-STAGING${NC}"
echo ""

# 3. Configurar branches
echo "3️⃣  Configurando branches..."

# Produção - main
cd FLUXOCASH-PRODUCAO
git checkout main
echo -e "${GREEN}✅ FLUXOCASH-PRODUCAO configurado na branch 'main'${NC}"

# Staging - feature/authentication-system
cd ../FLUXOCASH-STAGING
git checkout feature/authentication-system
echo -e "${GREEN}✅ FLUXOCASH-STAGING configurado na branch 'feature/authentication-system'${NC}"
echo ""

# 4. Limpar arquivos temporários
echo "4️⃣  Limpando arquivos temporários..."

# Limpar produção
cd ../FLUXOCASH-PRODUCAO
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
echo -e "${GREEN}✅ FLUXOCASH-PRODUCAO limpo${NC}"

# Limpar staging
cd ../FLUXOCASH-STAGING
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
echo -e "${GREEN}✅ FLUXOCASH-STAGING limpo${NC}"
echo ""

# Resumo final
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ✅ ORGANIZAÇÃO CONCLUÍDA COM SUCESSO!                      ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Estrutura criada:"
echo ""
echo "   $PARENT_DIR/"
echo "   ├── FLUXOCASH-PRODUCAO/     (branch: main)"
echo "   └── FLUXOCASH-STAGING/      (branch: feature/authentication-system)"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "   Para trabalhar em PRODUÇÃO:"
echo "   cd $PARENT_DIR/FLUXOCASH-PRODUCAO"
echo ""
echo "   Para trabalhar em STAGING:"
echo "   cd $PARENT_DIR/FLUXOCASH-STAGING"
echo ""
echo "📚 Leia: ORGANIZACAO_PROJETO.md para mais detalhes"
echo ""
