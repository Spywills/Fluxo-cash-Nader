#!/bin/bash

# Script para configurar ambiente de staging do FLUXO CASH

echo "================================================"
echo "🚀 SETUP DE STAGING - FLUXO CASH"
echo "================================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está na branch correta
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "feature/authentication-system" ]; then
    echo -e "${YELLOW}⚠️  Você está na branch: $CURRENT_BRANCH${NC}"
    echo -e "${YELLOW}   Recomendado estar em: feature/authentication-system${NC}"
    read -p "Deseja continuar mesmo assim? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Operação cancelada."
        exit 1
    fi
fi

echo ""
echo "📋 Checklist de Configuração:"
echo ""

# 1. Verificar arquivos .env
echo "1️⃣  Verificando arquivos de configuração..."
if [ ! -f "backend/.env.staging" ]; then
    echo -e "${RED}   ❌ backend/.env.staging não encontrado${NC}"
    echo "   Criando arquivo de exemplo..."
    cat > backend/.env.staging << EOF
# Supabase - Staging
SUPABASE_URL=https://seu-projeto-staging.supabase.co
SUPABASE_KEY=sua-chave-staging-aqui

# JWT Secret
JWT_SECRET_KEY=staging-secret-key-change-this

# Ambiente
ENVIRONMENT=staging
EOF
    echo -e "${YELLOW}   ⚠️  Configure backend/.env.staging com suas credenciais${NC}"
else
    echo -e "${GREEN}   ✅ backend/.env.staging encontrado${NC}"
fi

if [ ! -f "frontend/.env.staging" ]; then
    echo -e "${RED}   ❌ frontend/.env.staging não encontrado${NC}"
    echo "   Criando arquivo..."
    cat > frontend/.env.staging << EOF
VITE_API_URL=http://localhost:8000
VITE_ENV=staging
EOF
    echo -e "${GREEN}   ✅ frontend/.env.staging criado${NC}"
else
    echo -e "${GREEN}   ✅ frontend/.env.staging encontrado${NC}"
fi

echo ""

# 2. Verificar dependências do backend
echo "2️⃣  Verificando dependências do backend..."
if [ ! -d "backend/venv" ] && [ ! -d "backend/.venv" ]; then
    echo -e "${YELLOW}   ⚠️  Virtual environment não encontrado${NC}"
    read -p "   Deseja criar um virtual environment? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
        echo -e "${GREEN}   ✅ Virtual environment criado e dependências instaladas${NC}"
    fi
else
    echo -e "${GREEN}   ✅ Virtual environment encontrado${NC}"
fi

echo ""

# 3. Verificar dependências do frontend
echo "3️⃣  Verificando dependências do frontend..."
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}   ⚠️  node_modules não encontrado${NC}"
    read -p "   Deseja instalar dependências? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        cd frontend
        npm install
        cd ..
        echo -e "${GREEN}   ✅ Dependências instaladas${NC}"
    fi
else
    echo -e "${GREEN}   ✅ node_modules encontrado${NC}"
fi

echo ""
echo "================================================"
echo "📝 PRÓXIMOS PASSOS:"
echo "================================================"
echo ""
echo "1. Configure o Supabase de Staging:"
echo "   - Crie um novo projeto em https://supabase.com"
echo "   - Execute o SQL em: backend/database_schema.sql"
echo "   - Copie as credenciais para backend/.env.staging"
echo ""
echo "2. Crie o usuário admin:"
echo "   cd backend"
echo "   export \$(cat .env.staging | xargs)"
echo "   python create_admin_user.py"
echo ""
echo "3. Inicie o backend:"
echo "   cd backend"
echo "   export \$(cat .env.staging | xargs)"
echo "   uvicorn app.main_supabase:app --reload"
echo ""
echo "4. Inicie o frontend (em outro terminal):"
echo "   cd frontend"
echo "   npm run dev:staging"
echo ""
echo "5. Acesse: http://localhost:5174"
echo ""
echo "================================================"
echo -e "${GREEN}✅ Setup concluído!${NC}"
echo "================================================"
echo ""
echo "📚 Documentação completa: SETUP_STAGING.md"
echo ""
