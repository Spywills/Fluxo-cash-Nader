"""
Script para limpar transações órfãs (sem cliente válido)
"""
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.database import get_supabase_client

def clean_orphan_transactions():
    """Remove transações sem cliente válido"""
    
    print("🔍 Procurando transações órfãs...")
    
    try:
        client = get_supabase_client()
        
        # Buscar todos os clientes válidos
        clients = client.select('clients', columns='id')
        valid_client_ids = [c['id'] for c in clients]
        print(f"✅ {len(valid_client_ids)} clientes válidos encontrados")
        
        # Buscar todas as transações
        transactions = client.select('transactions', columns='*')
        print(f"📊 {len(transactions)} transações encontradas")
        
        # Encontrar órfãs
        orphans = [t for t in transactions if t['client_id'] not in valid_client_ids]
        
        if not orphans:
            print("\n✅ Nenhuma transação órfã encontrada!")
            return
        
        print(f"\n⚠️  {len(orphans)} transações órfãs encontradas:")
        for t in orphans:
            print(f"   - ID: {t['id']} | Cliente: {t['client_id']} (não existe) | Tipo: {t['type']} | Valor: R$ {t['amount']:.2f}")
        
        confirm = input("\nDeseja deletar estas transações? (SIM/não): ")
        
        if confirm != "SIM":
            print("❌ Operação cancelada.")
            return
        
        # Deletar órfãs
        print("\n🗑️  Deletando transações órfãs...")
        for t in orphans:
            client.delete('transactions', filters={'id': f'eq.{t["id"]}'})
            print(f"   ✅ Transação {t['id']} deletada")
        
        print(f"\n✅ {len(orphans)} transações órfãs removidas com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    clean_orphan_transactions()
