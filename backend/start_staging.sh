#!/bin/bash

# Script para iniciar backend em modo staging

echo "🚀 Iniciando Backend em modo STAGING..."
echo ""

# Carregar variáveis de ambiente de staging
export SUPABASE_URL="https://jqisqohwilhtlikwgbdz.supabase.co"
export SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpxaXNxb2h3aWxodGxpa3dnYmR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0ODY4MzAsImV4cCI6MjA3OTA2MjgzMH0.WWXdugcr77is2XpWQkCcY3bWmmjcK3Gt_Woiqf1PAwg"
export JWT_SECRET_KEY="fluxo-cash-staging-secret-key-2025-change-in-production"
export ENVIRONMENT="staging"

echo "✅ Variáveis de ambiente carregadas:"
echo "   SUPABASE_URL: $SUPABASE_URL"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo ""

# Iniciar uvicorn
python3 -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
