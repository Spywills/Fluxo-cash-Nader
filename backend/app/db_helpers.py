"""
Database helper functions for Supabase
"""
from typing import List, Dict, Any, Optional
from .database import get_supabase_client

# ============================================
# CLIENTS
# ============================================

def get_all_clients() -> List[Dict[str, Any]]:
    """Get all clients"""
    supabase = get_supabase_client()
    response = supabase.table('clients').select('*').order('created_at', desc=True).execute()
    return response.data

def get_client_by_id(client_id: int) -> Optional[Dict[str, Any]]:
    """Get client by ID"""
    supabase = get_supabase_client()
    response = supabase.table('clients').select('*').eq('id', client_id).execute()
    return response.data[0] if response.data else None

def create_client(name: str, email: str = "", phone: str = "", document: str = "", notes: str = "") -> Dict[str, Any]:
    """Create new client"""
    supabase = get_supabase_client()
    data = {
        "name": name,
        "email": email,
        "phone": phone,
        "document": document,
        "notes": notes,
        "saldo": 0.0,
        "total_deposits": 0.0,
        "total_withdrawals": 0.0
    }
    response = supabase.table('clients').insert(data).execute()
    return response.data[0]

def update_client(client_id: int, **kwargs) -> Dict[str, Any]:
    """Update client"""
    supabase = get_supabase_client()
    response = supabase.table('clients').update(kwargs).eq('id', client_id).execute()
    return response.data[0] if response.data else None

def delete_client(client_id: int) -> bool:
    """Delete client"""
    supabase = get_supabase_client()
    supabase.table('clients').delete().eq('id', client_id).execute()
    return True

def update_client_balance(client_id: int, amount: float, operation: str = 'add'):
    """Update client balance"""
    client = get_client_by_id(client_id)
    if not client:
        return None
    
    new_saldo = client['saldo'] + amount if operation == 'add' else client['saldo'] - amount
    
    update_data = {'saldo': new_saldo}
    if operation == 'add':
        update_data['total_deposits'] = client['total_deposits'] + amount
    else:
        update_data['total_withdrawals'] = client['total_withdrawals'] + amount
    
    return update_client(client_id, **update_data)

# ============================================
# PROOFS
# ============================================

def get_client_proofs(client_id: int) -> List[Dict[str, Any]]:
    """Get all proofs for a client"""
    supabase = get_supabase_client()
    response = supabase.table('proofs').select('*').eq('client_id', client_id).order('created_at', desc=True).execute()
    return response.data

def create_proof(client_id: int, filename: str, file_hash: str, **kwargs) -> Dict[str, Any]:
    """Create new proof"""
    supabase = get_supabase_client()
    data = {
        "client_id": client_id,
        "filename": filename,
        "file_hash": file_hash,
        **kwargs
    }
    response = supabase.table('proofs').insert(data).execute()
    return response.data[0]

def check_duplicate_proof(file_hash: str, client_id: int) -> bool:
    """Check if proof is duplicate"""
    supabase = get_supabase_client()
    response = supabase.table('proofs').select('id').eq('file_hash', file_hash).eq('client_id', client_id).execute()
    return len(response.data) > 0

def mark_proof_as_deposited(proof_id: int) -> Dict[str, Any]:
    """Mark proof as deposited"""
    supabase = get_supabase_client()
    response = supabase.table('proofs').update({'deposited': True}).eq('id', proof_id).execute()
    return response.data[0] if response.data else None

def delete_proof(proof_id: int) -> bool:
    """Delete proof"""
    supabase = get_supabase_client()
    supabase.table('proofs').delete().eq('id', proof_id).execute()
    return True

# ============================================
# TRANSACTIONS
# ============================================

def get_all_transactions(transaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all transactions, optionally filtered by type"""
    supabase = get_supabase_client()
    query = supabase.table('transactions').select('*')
    if transaction_type:
        query = query.eq('type', transaction_type)
    response = query.order('created_at', desc=True).execute()
    return response.data

def get_client_transactions(client_id: int) -> List[Dict[str, Any]]:
    """Get all transactions for a client"""
    supabase = get_supabase_client()
    response = supabase.table('transactions').select('*').eq('client_id', client_id).order('created_at', desc=True).execute()
    return response.data

def create_transaction(client_id: int, amount: float, trans_type: str, **kwargs) -> Dict[str, Any]:
    """Create new transaction"""
    supabase = get_supabase_client()
    data = {
        "client_id": client_id,
        "amount": amount,
        "type": trans_type,
        **kwargs
    }
    response = supabase.table('transactions').insert(data).execute()
    return response.data[0]

def update_transaction(transaction_id: int, **kwargs) -> Dict[str, Any]:
    """Update transaction"""
    supabase = get_supabase_client()
    response = supabase.table('transactions').update(kwargs).eq('id', transaction_id).execute()
    return response.data[0] if response.data else None

def delete_transaction(transaction_id: int) -> bool:
    """Delete transaction"""
    supabase = get_supabase_client()
    supabase.table('transactions').delete().eq('id', transaction_id).execute()
    return True

# ============================================
# STATISTICS
# ============================================

def get_global_statistics() -> Dict[str, Any]:
    """Get global system statistics"""
    supabase = get_supabase_client()
    
    # Total clients
    clients_response = supabase.table('clients').select('*', count='exact').execute()
    total_clients = clients_response.count
    
    # Clients with negative balance
    negative_clients = supabase.table('clients').select('*', count='exact').lt('saldo', 0).execute()
    clientes_negativo = negative_clients.count
    
    # Total deposits
    deposits = supabase.table('transactions').select('amount').eq('type', 'DEPOSIT').eq('status', 'COMPLETED').execute()
    total_deposits = sum([t['amount'] for t in deposits.data]) if deposits.data else 0
    
    # Total withdrawals
    withdrawals = supabase.table('transactions').select('amount').eq('type', 'WITHDRAWAL').eq('status', 'COMPLETED').execute()
    total_withdrawals = sum([t['amount'] for t in withdrawals.data]) if withdrawals.data else 0
    
    # Total proofs
    proofs_response = supabase.table('proofs').select('*', count='exact').execute()
    total_proofs = proofs_response.count
    
    # Total transactions
    transactions_response = supabase.table('transactions').select('*', count='exact').execute()
    total_operations = transactions_response.count
    
    return {
        "total_clients": total_clients,
        "clientes_em_negativo": clientes_negativo,
        "total_depositos": total_deposits,
        "total_saques": total_withdrawals,
        "saldo_geral": total_deposits - total_withdrawals,
        "total_comprovantes": total_proofs,
        "total_operations": total_operations,
        "total_buy_brl": total_deposits,
        "total_sell_brl": total_withdrawals
    }
