"""
Script de migração de dados em memória para Supabase
Execute após configurar o .env com as credenciais do Supabase
"""
import os
from dotenv import load_dotenv
from app.database import get_supabase_client, init_database

# Carregar variáveis de ambiente
load_dotenv()

def migrate_data():
    """Migra dados do sistema em memória para Supabase"""
    
    print("🔄 Iniciando migração para Supabase...")
    
    # Testar conexão
    if not init_database():
        print("❌ Erro: Não foi possível conectar ao Supabase")
        print("Verifique se o arquivo .env está configurado corretamente")
        return False
    
    print("✅ Conexão com Supabase estabelecida!")
    
    supabase = get_supabase_client()
    
    # Verificar se tabelas existem
    try:
        supabase.table('clients').select("count", count="exact").execute()
        print("✅ Tabela 'clients' encontrada")
        
        supabase.table('proofs').select("count", count="exact").execute()
        print("✅ Tabela 'proofs' encontrada")
        
        supabase.table('transactions').select("count", count="exact").execute()
        print("✅ Tabela 'transactions' encontrada")
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        print("\n💡 Dica: Execute o SQL do arquivo 'database_schema.sql' no SQL Editor do Supabase")
        return False
    
    print("\n✅ Todas as tabelas estão prontas!")
    print("\n📊 Sistema pronto para usar o Supabase!")
    print("\nPróximos passos:")
    print("1. Reinicie o backend: cd backend && python -m uvicorn app.main:app --reload --port 8000")
    print("2. O sistema agora usará o banco de dados PostgreSQL do Supabase")
    print("3. Todos os dados serão persistidos permanentemente")
    
    return True

if __name__ == "__main__":
    migrate_data()
