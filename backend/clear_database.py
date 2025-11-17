"""
Script para limpar (zerar) todo o banco de dados Supabase
ATENÇÃO: Isso vai deletar TODOS os dados!
"""
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.database import get_supabase_client

def clear_database():
    """Limpa todos os dados do banco de dados"""
    
    print("⚠️  ATENÇÃO: Isso vai deletar TODOS os dados do banco!")
    print("=" * 60)
    
    confirm = input("Digite 'SIM' para confirmar: ")
    
    if confirm != "SIM":
        print("❌ Operação cancelada.")
        return
    
    print("\n🔄 Limpando banco de dados...")
    
    try:
        supabase = get_supabase_client()
        
        # Deletar na ordem correta (por causa das foreign keys)
        
        # 1. Deletar transações
        print("🗑️  Deletando transações...")
        result = supabase.table('transactions').delete().neq('id', 0).execute()
        print(f"   ✅ {len(result.data)} transações deletadas")
        
        # 2. Deletar comprovantes
        print("🗑️  Deletando comprovantes...")
        result = supabase.table('proofs').delete().neq('id', 0).execute()
        print(f"   ✅ {len(result.data)} comprovantes deletados")
        
        # 3. Deletar clientes
        print("🗑️  Deletando clientes...")
        result = supabase.table('clients').delete().neq('id', 0).execute()
        print(f"   ✅ {len(result.data)} clientes deletados")
        
        print("\n" + "=" * 60)
        print("✅ Banco de dados limpo com sucesso!")
        print("📊 Todas as tabelas estão vazias agora.")
        
        # Verificar
        print("\n🔍 Verificando...")
        clients = supabase.table('clients').select('*', count='exact').execute()
        proofs = supabase.table('proofs').select('*', count='exact').execute()
        transactions = supabase.table('transactions').select('*', count='exact').execute()
        
        print(f"   Clientes: {clients.count}")
        print(f"   Comprovantes: {proofs.count}")
        print(f"   Transações: {transactions.count}")
        
        if clients.count == 0 and proofs.count == 0 and transactions.count == 0:
            print("\n✅ Banco de dados completamente limpo!")
        
    except Exception as e:
        print(f"\n❌ Erro ao limpar banco de dados: {e}")

if __name__ == "__main__":
    clear_database()
