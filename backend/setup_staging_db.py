"""
Script para configurar banco de dados de staging
Execute: python backend/setup_staging_db.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Carregar variáveis de ambiente de staging
from dotenv import load_dotenv
env_path = backend_dir / '.env.staging'
load_dotenv(dotenv_path=env_path)

from app.database import get_supabase_client

def check_tables():
    """Verifica se as tabelas existem"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO TABELAS NO BANCO DE STAGING")
    print("=" * 60)
    
    supabase = get_supabase_client()
    
    tables_to_check = ['users', 'clients', 'proofs', 'transactions']
    
    for table in tables_to_check:
        try:
            response = supabase.table(table).select('count').execute()
            print(f"✅ Tabela '{table}' existe")
        except Exception as e:
            print(f"❌ Tabela '{table}' NÃO existe ou erro: {str(e)[:50]}")
    
    print("=" * 60)

def show_instructions():
    """Mostra instruções para executar o schema"""
    print("\n" + "=" * 60)
    print("📋 INSTRUÇÕES PARA CONFIGURAR O BANCO")
    print("=" * 60)
    print("\n1. Acesse o Supabase SQL Editor:")
    print("   https://supabase.com/dashboard/project/jqisqohwilhtlikwgbdz/sql")
    print("\n2. Clique em 'New Query'")
    print("\n3. Cole o conteúdo do arquivo:")
    print("   backend/database_schema.sql")
    print("\n4. Clique em 'Run' para executar")
    print("\n5. Execute este script novamente para verificar:")
    print("   python backend/setup_staging_db.py")
    print("\n" + "=" * 60)

def main():
    print("\n" + "=" * 60)
    print("🚀 SETUP DO BANCO DE DADOS DE STAGING")
    print("=" * 60)
    
    # Verificar variáveis de ambiente
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("\n❌ ERRO: Variáveis de ambiente não configuradas!")
        print("\nCertifique-se de que backend/.env.staging está configurado:")
        print("  SUPABASE_URL=https://jqisqohwilhtlikwgbdz.supabase.co")
        print("  SUPABASE_KEY=eyJhbGci...")
        print("\nE execute:")
        print("  export $(cat backend/.env.staging | xargs)")
        return
    
    print(f"\n✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")
    
    # Verificar tabelas
    try:
        check_tables()
    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")
        print("\n⚠️  As tabelas ainda não foram criadas.")
        show_instructions()
        return
    
    print("\n✅ Banco de dados de staging configurado!")
    print("\n📝 Próximo passo: Criar usuário admin")
    print("   cd backend")
    print("   export $(cat .env.staging | xargs)")
    print("   python create_admin_user.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
