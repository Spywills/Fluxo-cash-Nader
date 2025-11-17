"""
Database helper functions for Supabase using httpx
"""
from typing import List, Dict, Any, Optional
from .database import get_supabase_client

# ============================================
# CLIENTS
# ============================================

def get_all_clients() -> List[Dict[str, Any]]:
    """Get all clients"""
    client = get_supabase_client()
    return client.select('clients', columns='*')

def get_client_by_id(client_id: int) -> Optional[Dict[str, Any]]:
    """Get client by ID"""
    client = get_supabase_client()
    results = client.select('clients', columns='*', filters={'id': f'eq.{client_id}'})
    return results[0] if results else None

def create_client(name: str, email: str = "", phone: str = "", document: str = "", notes: str = "") -> Dict[str, Any]:
    """Create new client"""
    client = get_supabase_client()
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
    return client.insert('clients', data)

def update_client(client_id: int, **kwargs) -> Dict[str, Any]:
    """Update client"""
    client = get_supabase_client()
    return client.update('clients', kwargs, filters={'id': f'eq.{client_id}'})

def delete_client(client_id: int) -> bool:
    """Delete client"""
    client = get_supabase_client()
    return client.delete('clients', filters={'id': f'eq.{client_id}'})

def update_client_balance(client_id: int, amount: float, operation: str = 'add'):
    """Update client balance"""
    current_client = get_client_by_id(client_id)
    if not current_client:
        return None
    
    new_saldo = current_client['saldo'] + amount if operation == 'add' else current_client['saldo'] - amount
    
    update_data = {'saldo': new_saldo}
    if operation == 'add':
        update_data['total_deposits'] = current_client['total_deposits'] + amount
    else:
        update_data['total_withdrawals'] = current_client['total_withdrawals'] + amount
    
    return update_client(client_id, **update_data)

# ============================================
# PROOFS
# ============================================

def get_client_proofs(client_id: int) -> List[Dict[str, Any]]:
    """Get all proofs for a client"""
    client = get_supabase_client()
    return client.select('proofs', columns='*', filters={'client_id': f'eq.{client_id}'})

def create_proof(client_id: int, filename: str, file_hash: str, **kwargs) -> Dict[str, Any]:
    """Create new proof"""
    client = get_supabase_client()
    data = {
        "client_id": client_id,
        "filename": filename,
        "file_hash": file_hash,
        **kwargs
    }
    return client.insert('proofs', data)

def check_duplicate_proof(file_hash: str, client_id: int) -> bool:
    """Check if proof is duplicate"""
    client = get_supabase_client()
    results = client.select('proofs', columns='id', filters={
        'file_hash': f'eq.{file_hash}',
        'client_id': f'eq.{client_id}'
    })
    return len(results) > 0

def mark_proof_as_deposited(proof_id: int) -> Dict[str, Any]:
    """Mark proof as deposited"""
    client = get_supabase_client()
    return client.update('proofs', {'deposited': True}, filters={'id': f'eq.{proof_id}'})

def delete_proof(proof_id: int) -> bool:
    """Delete proof"""
    client = get_supabase_client()
    return client.delete('proofs', filters={'id': f'eq.{proof_id}'})

# ============================================
# TRANSACTIONS
# ============================================

def get_all_transactions(transaction_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all transactions, optionally filtered by type"""
    client = get_supabase_client()
    filters = {'type': f'eq.{transaction_type}'} if transaction_type else {}
    return client.select('transactions', columns='*', filters=filters)

def get_client_transactions(client_id: int) -> List[Dict[str, Any]]:
    """Get all transactions for a client"""
    client = get_supabase_client()
    return client.select('transactions', columns='*', filters={'client_id': f'eq.{client_id}'})

def create_transaction(client_id: int, amount: float, trans_type: str, **kwargs) -> Dict[str, Any]:
    """Create new transaction"""
    client = get_supabase_client()
    data = {
        "client_id": client_id,
        "amount": amount,
        "type": trans_type,
        **kwargs
    }
    return client.insert('transactions', data)

def update_transaction(transaction_id: int, **kwargs) -> Dict[str, Any]:
    """Update transaction"""
    client = get_supabase_client()
    return client.update('transactions', kwargs, filters={'id': f'eq.{transaction_id}'})

def delete_transaction(transaction_id: int) -> bool:
    """Delete transaction"""
    client = get_supabase_client()
    return client.delete('transactions', filters={'id': f'eq.{transaction_id}'})

# ============================================
# STATISTICS
# ============================================

def get_global_statistics() -> Dict[str, Any]:
    """Get global system statistics"""
    client = get_supabase_client()
    
    # Total clients
    all_clients = client.select('clients', columns='*')
    total_clients = len(all_clients)
    
    # Clients with negative balance
    clientes_negativo = len([c for c in all_clients if c['saldo'] < 0])
    
    # Total deposits
    deposits = client.select('transactions', columns='amount', filters={
        'type': 'eq.DEPOSIT',
        'status': 'eq.COMPLETED'
    })
    total_deposits = sum([t['amount'] for t in deposits]) if deposits else 0
    
    # Total withdrawals
    withdrawals = client.select('transactions', columns='amount', filters={
        'type': 'eq.WITHDRAWAL',
        'status': 'eq.COMPLETED'
    })
    total_withdrawals = sum([t['amount'] for t in withdrawals]) if withdrawals else 0
    
    # Total proofs
    all_proofs = client.select('proofs', columns='id')
    total_proofs = len(all_proofs)
    
    # Total transactions
    all_transactions = client.select('transactions', columns='id')
    total_operations = len(all_transactions)
    
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
