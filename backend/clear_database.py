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
        transactions = supabase.select('transactions', columns='id')
        for t in transactions:
            supabase.delete('transactions', filters={'id': f'eq.{t["id"]}'})
        print(f"   ✅ {len(transactions)} transações deletadas")
        
        # 2. Deletar comprovantes
        print("🗑️  Deletando comprovantes...")
        proofs = supabase.select('proofs', columns='id')
        for p in proofs:
            supabase.delete('proofs', filters={'id': f'eq.{p["id"]}'})
        print(f"   ✅ {len(proofs)} comprovantes deletados")
        
        # 3. Deletar clientes
        print("🗑️  Deletando clientes...")
        clients = supabase.select('clients', columns='id')
        for c in clients:
            supabase.delete('clients', filters={'id': f'eq.{c["id"]}'})
        print(f"   ✅ {len(clients)} clientes deletados")
        
        print("\n" + "=" * 60)
        print("✅ Banco de dados limpo com sucesso!")
        print("📊 Todas as tabelas estão vazias agora.")
        
        # Verificar
        print("\n🔍 Verificando...")
        clients_check = supabase.select('clients', columns='id')
        proofs_check = supabase.select('proofs', columns='id')
        transactions_check = supabase.select('transactions', columns='id')
        
        print(f"   Clientes: {len(clients_check)}")
        print(f"   Comprovantes: {len(proofs_check)}")
        print(f"   Transações: {len(transactions_check)}")
        
        if len(clients_check) == 0 and len(proofs_check) == 0 and len(transactions_check) == 0:
            print("\n✅ Banco de dados completamente limpo!")
        
    except Exception as e:
        print(f"\n❌ Erro ao limpar banco de dados: {e}")

if __name__ == "__main__":
    clear_database()
