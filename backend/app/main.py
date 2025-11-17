"""
FLUXO CASH - Backend com FastAPI
Sistema de gestão de clientes e comprovantes com extração automática de valores
"""

import logging
import hashlib
from datetime import datetime
from fastapi import FastAPI, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import tempfile
from pathlib import Path

# Importar o módulo de extração
from .extractors import extract_proof_data

# Importar funções do banco de dados
from .db_helpers import (
    get_all_clients, get_client_by_id, create_client, update_client, delete_client,
    update_client_balance, get_client_proofs, create_proof, check_duplicate_proof,
    mark_proof_as_deposited, delete_proof, get_all_transactions, get_client_transactions,
    create_transaction, update_transaction, delete_transaction, get_global_statistics
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(title="FLUXO CASH", version="1.0.0")

# Configurar CORS
origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://192.168.0.114:5174",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ========================================

# Inicializar conexão com Supabase
from .database import init_database

# Tentar conectar ao Supabase
if init_database():
    logger.info("✅ Conectado ao Supabase PostgreSQL")
    USE_SUPABASE = True
else:
    logger.warning("⚠️ Supabase não disponível, usando memória")
    USE_SUPABASE = False
    # Fallback para dicionários em memória
    proofs_db = {}
    clients_db = {}
    transactions_db = []
    transaction_counter = 0

# ========================================
# HEALTH CHECK
# ========================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FLUXO CASH"
    }

# ========================================
# PROOFS (COMPROVANTES)
# ========================================

@app.get("/proofs/clients/{client_id}")
def get_client_proofs(client_id: int):
    client_proofs = [p for p in proofs_db.values() if p['client_id'] == client_id]
    
    stats = {
        "total_proofs": len(client_proofs),
        "total_extracted": len([p for p in client_proofs if p['extraction_status'] == 'EXTRACTED']),
        "total_duplicates": len([p for p in client_proofs if p['is_duplicate']]),
        "total_value": sum([p['extracted_value'] or 0 for p in client_proofs if p['extraction_status'] == 'EXTRACTED'])
    }
    
    return {
        "proofs": client_proofs,
        "stats": stats
    }

@app.get("/proofs/{proof_id}")
def get_proof(proof_id: int):
    if proof_id not in proofs_db:
        return {"error": "Comprovante não encontrado"}, 404
    
    return {"proof": proofs_db[proof_id]}

@app.post("/proofs/clients/{client_id}/upload")
async def upload_proof(client_id: int, file: UploadFile = File(...)):
    """
    Endpoint para upload de comprovantes
    - Detecta duplicatas
    - Extrai valores usando OCR (PDFs/Imagens)
    - Armazena arquivo
    """
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        # Ler conteúdo do arquivo
        contents = await file.read()
        file_size = len(contents)
        
        # Gerar novo ID
        new_id = max(proofs_db.keys()) + 1 if proofs_db else 1
        
        # 🔍 Gera hash do arquivo para detectar duplicatas
        file_hash = hashlib.sha256(contents).hexdigest()
        
        # 🔍 Verifica duplicata
        is_duplicate = check_duplicate(file_hash, client_id)
        
        if is_duplicate:
            logger.warning(f"⚠️ Comprovante duplicado detectado: {file.filename}")
            return {
                "success": False,
                "proof": None,
                "is_duplicate": True,
                "message": "Arquivo duplicado detectado"
            }
        
        # 💾 Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(suffix=Path(file.filename).suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # 💰 Extrai dados do comprovante usando OCR/PDF reader
            extracted_data = extract_proof_data(tmp_path)
            
            value = extracted_data.get('value')
            confidence = extracted_data.get('confidence', 0)
            beneficiary = extracted_data.get('beneficiary')
            endtoend = extracted_data.get('endtoend')
            
            if value is None:
                value = 5000.0  # Fallback
                confidence = 0.5
            
            extraction_status = "EXTRACTED" if extracted_data.get('success') else "EXTRACTED_WITH_ERROR"
            
            # 📝 Cria novo comprovante
            new_proof = {
                "id": new_id,
                "client_id": client_id,
                "filename": file.filename,
                "file_type": file.content_type or "application/octet-stream",
                "file_size": file_size,
                "extracted_value": value,
                "extraction_confidence": confidence,
                "extraction_status": extraction_status,
                "beneficiary": beneficiary or "DESCONHECIDO",
                "endtoend": endtoend or None,
                "is_duplicate": False,
                "deposited": False,  # 🌟 NOVO: Flag para controlar se já foi creditado
                "file_hash": file_hash,
                "uploaded_at": datetime.now().isoformat()
            }
            
            proofs_db[new_id] = new_proof
            
            logger.info(f"✅ Comprovante enviado: {file.filename} | Valor: R$ {value:.2f} | Confiança: {confidence:.0%}")
            
            return {
                "success": True,
                "proof": new_proof,
                "is_duplicate": False,
                "message": f"Comprovante enviado com sucesso | Valor extraído: R$ {value:.2f}"
            }
        
        finally:
            # Limpar arquivo temporário
            try:
                Path(tmp_path).unlink()
            except:
                pass
    
    except Exception as e:
        logger.error(f"Erro ao fazer upload: {str(e)}")
        return {"error": str(e)}, 500

@app.delete("/proofs/{proof_id}")
def delete_proof(proof_id: int):
    try:
        if proof_id not in proofs_db:
            return {"error": "Comprovante não encontrado"}, 404
        
        proof = proofs_db[proof_id]
        del proofs_db[proof_id]
        
        logger.info(f"✅ Comprovante deletado: {proof['filename']} (ID: {proof_id})")
        
        return {
            "success": True,
            "message": f"Comprovante {proof['filename']} deletado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao deletar comprovante: {str(e)}")
        return {"error": str(e)}, 500

# ========================================
# DEPOSITS (DEPÓSITOS)
# ========================================

@app.post("/deposits/proofs/{proof_id}")
def create_deposit_from_proof(proof_id: int):
    global transaction_counter
    
    if proof_id not in proofs_db:
        return {"error": "Comprovante não encontrado"}, 404
    
    proof = proofs_db[proof_id]
    
    # 🌟 VALIDAÇÃO: Verificar se já foi depositado
    if proof.get('deposited', False):
        return {"error": "Este comprovante já foi creditado anteriormente"}, 400
    
    if proof['extraction_status'] != 'EXTRACTED':
        return {"error": "Comprovante não tem valor extraído"}, 400
    
    if proof['extracted_value'] is None or proof['extracted_value'] == 0:
        return {"error": "Valor inválido"}, 400
    
    # Criar transação
    transaction_counter += 1
    client_id = proof['client_id']
    value = proof['extracted_value']
    
    transaction = {
        "id": transaction_counter,
        "client_id": client_id,
        "proof_id": proof_id,
        "amount": value,
        "type": "DEPOSIT",
        "status": "COMPLETED",
        "description": f"Depósito de {proof['filename']}",
        "created_at": datetime.now().isoformat()
    }
    
    transactions_db.append(transaction)
    
    # Atualizar saldo do cliente
    if client_id in clients_db:
        clients_db[client_id]['saldo'] += value
        clients_db[client_id]['total_deposits'] += value
    
    # 🌟 MARCAR COMPROVANTE COMO DEPOSITADO
    proofs_db[proof_id]['deposited'] = True
    
    logger.info(f"✅ Depósito criado: R$ {value} para cliente {client_id} | Comprovante #{proof_id} marcado como depositado")
    
    return {
        "success": True,
        "transaction_id": transaction_counter,
        "amount": value,
        "client_saldo": clients_db[client_id]['saldo'] if client_id in clients_db else 0
    }

@app.delete("/deposits/{transaction_id}")
def remove_deposit(transaction_id: int):
    """Remove (reverte) um depósito"""
    try:
        # Buscar transação
        transaction = None
        for t in transactions_db:
            if t.get('id') == transaction_id and t.get('type') == 'DEPOSIT':
                transaction = t
                break
        
        if not transaction:
            return {"error": "Depósito não encontrado"}, 404
        
        client_id = transaction['client_id']
        value = transaction['amount']
        
        # Remover transação
        transactions_db.remove(transaction)
        
        # Reverter saldo do cliente
        if client_id in clients_db:
            clients_db[client_id]['saldo'] -= value
            clients_db[client_id]['total_deposits'] -= value
        
        logger.info(f"✅ Depósito removido: R$ {value} do cliente {client_id}")
        
        return {
            "success": True,
            "message": "Depósito removido com sucesso",
            "client_saldo": clients_db[client_id]['saldo'] if client_id in clients_db else 0
        }
    except Exception as e:
        logger.error(f"Erro ao remover depósito: {str(e)}")
        return {"error": str(e)}, 500

# ========================================
# CLIENTS (CLIENTES)
# ========================================

@app.get("/clients/{client_id}")
def get_client(client_id: int):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        client = dict(clients_db[client_id])
        client['saldo_atual'] = client.get('saldo', 0.0)
        
        return {
            "client": client
        }
    except Exception as e:
        logger.error(f"Erro em get_client: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/clients/{client_id}/balance")
def get_client_balance(client_id: int):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        client = clients_db[client_id]
        
        return {
            "balance": {
                "saldo_disponivel": client.get("saldo", 0.0),
                "total_deposits": client.get("total_deposits", 0.0),
                "total_withdrawals": client.get("total_withdrawals", 0.0),
                "status": "POSITIVO" if client.get("saldo", 0.0) >= 0 else "NEGATIVO"
            }
        }
    except Exception as e:
        logger.error(f"Erro em get_client_balance: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/clients")
def get_all_clients():
    try:
        # Adicionar saldo_atual dinamicamente
        clients_list = []
        for client in clients_db.values():
            client_data = dict(client)
            client_data['saldo_atual'] = client.get('saldo', 0.0)
            clients_list.append(client_data)
        
        return {
            "clients": clients_list,
            "total": len(clients_db)
        }
    except Exception as e:
        logger.error(f"Erro em get_all_clients: {str(e)}")
        return {"error": str(e)}, 500

@app.post("/clients")
def create_client(data: Dict[str, Any] = Body(...)):
    try:
        # Validar nome obrigatório
        name = data.get("name", "").strip()
        if not name:
            return {"error": "Nome do cliente é obrigatório"}, 400
        
        # Gerar novo ID
        new_id = max(clients_db.keys()) + 1 if clients_db else 1
        
        new_client = {
            "id": new_id,
            "name": name,
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "document": data.get("document", ""),
            "notes": data.get("notes", ""),
            "saldo": 0.0,
            "total_deposits": 0.0,
            "total_withdrawals": 0.0
        }
        
        clients_db[new_id] = new_client
        logger.info(f"✅ Cliente criado: {new_client['name']} (ID: {new_id})")
        
        return {
            "success": True,
            "client": new_client,
            "data": new_client
        }
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {str(e)}")
        return {"error": str(e)}, 500

@app.put("/clients/{client_id}")
def update_client(client_id: int, data: Dict[str, Any] = Body(...)):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        client = clients_db[client_id]
        
        # Atualizar campos
        if "name" in data:
            client["name"] = data["name"]
        if "email" in data:
            client["email"] = data["email"]
        if "phone" in data:
            client["phone"] = data["phone"]
        if "document" in data:
            client["document"] = data["document"]
        if "notes" in data:
            client["notes"] = data["notes"]
        
        logger.info(f"✅ Cliente atualizado: {client['name']} (ID: {client_id})")
        
        return {
            "success": True,
            "client": client,
            "data": client
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        return {"error": str(e)}, 500

@app.put("/clients/{client_id}/notes")
def update_client_notes(client_id: int, data: Dict[str, Any] = Body(...)):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        client = clients_db[client_id]
        client["notes"] = data.get("notes", "")
        
        logger.info(f"✅ Notas do cliente atualizadas: {client['name']} (ID: {client_id})")
        
        return {
            "success": True,
            "client": client,
            "data": client
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar notas: {str(e)}")
        return {"error": str(e)}, 500

@app.delete("/clients/{client_id}")
def delete_client(client_id: int):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        client_name = clients_db[client_id]["name"]
        
        # Cascade delete: remover saques e transações do cliente
        # (Comprovantes são mantidos para evitar duplicação)
        
        # Remover saques (withdrawals)
        withdrawals_deleted = 0
        withdrawals_to_delete = [w_id for w_id, w in clients_db[client_id].get('withdrawals', {}).items()]
        for withdrawal_id in withdrawals_to_delete:
            if client_id in clients_db and 'withdrawals' in clients_db[client_id]:
                if withdrawal_id in clients_db[client_id]['withdrawals']:
                    del clients_db[client_id]['withdrawals'][withdrawal_id]
                    withdrawals_deleted += 1
        
        # Remover transações do cliente
        transactions_deleted = 0
        initial_count = len(transactions_db)
        transactions_db.clear()  # Limpar transações
        transactions_deleted = initial_count
        
        # Deletar cliente
        del clients_db[client_id]
        
        logger.info(f"✅ Cliente deletado com cascade: {client_name} (ID: {client_id})")
        logger.info(f"   - Saques removidos: {withdrawals_deleted}")
        logger.info(f"   - Transações removidas: {transactions_deleted}")
        logger.info(f"   - Comprovantes mantidos: (para evitar duplicação)")
        
        return {
            "success": True,
            "message": f"Cliente {client_name} deletado com sucesso",
            "deleted": {
                "withdrawals": withdrawals_deleted,
                "transactions": transactions_deleted,
                "proofs_kept": True
            }
        }
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {str(e)}")
        return {"error": str(e)}, 500

# ========================================
# GLOBAL BALANCE
# ========================================

@app.get("/global-balance")
def get_global_balance():
    try:
        # Calcular total de depósitos reais
        total_deposits = sum([
            t['amount'] for t in transactions_db 
            if t['type'] == "DEPOSIT" and t['status'] == "COMPLETED"
        ])
        
        # Calcular total de saques reais
        total_withdrawals = sum([
            t['amount'] for t in transactions_db 
            if t['type'] == "WITHDRAWAL" and t['status'] == "COMPLETED"
        ])
        
        # Saldo geral
        saldo_geral = total_deposits - total_withdrawals
        
        # Clientes em negativo
        clientes_negativo = len([c for c in clients_db.values() if c['saldo'] < 0])
        
        return {
            "saldo_total": saldo_geral,
            "saldo_geral": saldo_geral,
            "total_depositos": total_deposits,
            "total_saques": total_withdrawals,
            "total_clientes": len(clients_db),
            "clientes_em_negativo": clientes_negativo
        }
    except Exception as e:
        logger.error(f"Erro em get_global_balance: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/global-withdrawals")
def get_global_withdrawals():
    try:
        # Retornar apenas transações de saque reais, normalizadas
        withdrawals = [w for w in transactions_db if w.get('type') == 'WITHDRAWAL']
        
        # Ordenar por data (mais recente primeiro)
        withdrawals.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        result = []
        for t in withdrawals:
            client_id = t['client_id']
            client_name = clients_db.get(client_id, {}).get('name', 'Cliente Desconhecido')
            # Converter status para exibição: COMPLETED → APROVADO, PENDING → PENDENTE
            display_status = "APROVADO" if t['status'] == "COMPLETED" else "PENDENTE"
            result.append({
                "id": t['id'],
                "client_id": client_id,
                "client": client_name,
                "amount_brl": t['amount'],
                "amount_crypto": 0,
                "status": display_status,
                "date": t.get('created_at', ''),
                "notes": t.get('description', '')
            })
        
        return result
    except Exception as e:
        logger.error(f"Erro em get_global_withdrawals: {str(e)}")
        return {"error": str(e)}, 500

# ========================================
# WITHDRAWALS (SAQUES)
# ========================================

@app.post("/clients/{client_id}/withdrawals")
def create_withdrawal(client_id: int, data: Dict[str, Any] = Body(...)):
    global transaction_counter
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        # Usar contador global para ID único
        transaction_counter += 1
        new_id = transaction_counter
        
        withdrawal = {
            "id": new_id,
            "client_id": client_id,
            "amount": float(data.get("valor", 0)),
            "description": data.get("descricao", ""),
            "admin_notes": data.get("admin_notes", ""),
            "status": "PENDING",
            "type": "WITHDRAWAL",
            "created_at": datetime.now().isoformat()
        }
        
        transactions_db.append(withdrawal)
        logger.info(f"✅ Saque criado: R$ {withdrawal['amount']} para cliente {client_id}")
        
        return {
            "success": True,
            "withdrawal": withdrawal,
            "client_id": client_id
        }
    except Exception as e:
        logger.error(f"Erro ao criar saque: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/clients/{client_id}/withdrawals")
def get_client_withdrawals(client_id: int):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        client_withdrawals = [w for w in transactions_db if w.get('client_id') == client_id and w.get('type') == 'WITHDRAWAL']
        
        return {
            "withdrawals": client_withdrawals
        }
    except Exception as e:
        logger.error(f"Erro ao buscar saques: {str(e)}")
        return {"error": str(e)}, 500

@app.put("/clients/{client_id}/withdrawals/{withdrawal_id}")
def update_withdrawal(client_id: int, withdrawal_id: int, data: Dict[str, Any] = Body(...)):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        # Buscar saque
        withdrawal = None
        withdrawal_index = None
        for i, w in enumerate(transactions_db):
            if w.get('id') == withdrawal_id and w.get('client_id') == client_id and w.get('type') == 'WITHDRAWAL':
                withdrawal = w
                withdrawal_index = i
                break
        
        if not withdrawal:
            return {"error": "Saque não encontrado"}, 404
        
        # Normalizar status (aceitar PT/EN e manter estado interno como PENDING/COMPLETED)
        def _normalize_status(s):
            if s is None:
                return s
            s_up = str(s).upper()
            if s_up in ("APPROVED", "APROVADO", "COMPLETED"):
                return "COMPLETED"
            if s_up in ("PENDING", "PENDENTE"):
                return "PENDING"
            return s_up

        old_status_raw = withdrawal.get('status')
        old_status = _normalize_status(old_status_raw)

        new_status_raw = data.get('status', old_status_raw)
        new_status = _normalize_status(new_status_raw)

        # Atualizar status interno e notas
        if "status" in data:
            withdrawal["status"] = new_status

        if "admin_notes" in data:
            withdrawal["admin_notes"] = data["admin_notes"]

        # Se houve transição PENDING -> COMPLETED, aplicar redução de saldo do cliente
        if old_status == "PENDING" and new_status == "COMPLETED":
            client_id_w = withdrawal['client_id']
            try:
                valor_saque = float(withdrawal.get('amount', withdrawal.get('valor', 0) or 0))
            except Exception:
                valor_saque = 0.0

            if client_id_w in clients_db:
                clients_db[client_id_w]['saldo'] = clients_db[client_id_w].get('saldo', 0.0) - valor_saque
                clients_db[client_id_w]['total_withdrawals'] = clients_db[client_id_w].get('total_withdrawals', 0.0) + valor_saque
        
        # Atualizar na lista (garante que a mudança persiste)
        transactions_db[withdrawal_index] = withdrawal
        
        # Para exibição no frontend, manter label em PT (APROVADO/PENDENTE)
        display_status = "APROVADO" if withdrawal.get('status') == "COMPLETED" else ("PENDENTE" if withdrawal.get('status') == "PENDING" else withdrawal.get('status'))
        logger.info(f"✅ Saque atualizado: ID={withdrawal_id}, Status={withdrawal.get('status')}, Valor={withdrawal.get('amount', withdrawal.get('valor'))}")

        return {
            "success": True,
            "withdrawal": {**withdrawal, "display_status": display_status},
            "message": f"Saque atualizado para {display_status}"
        }, 200
    except Exception as e:
        logger.error(f"Erro ao atualizar saque: {str(e)}")
        return {"error": str(e)}, 500

@app.delete("/clients/{client_id}/withdrawals/{withdrawal_id}")
def delete_withdrawal(client_id: int, withdrawal_id: int):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        # Buscar e deletar saque
        for i, w in enumerate(transactions_db):
            if w.get('id') == withdrawal_id and w.get('client_id') == client_id:
                del transactions_db[i]
                logger.info(f"✅ Saque deletado: {withdrawal_id}")
                return {
                    "success": True,
                    "message": "Saque deletado com sucesso"
                }
        
        return {"error": "Saque não encontrado"}, 404
    except Exception as e:
        logger.error(f"Erro ao deletar saque: {str(e)}")
        return {"error": str(e)}, 500

# ========================================
# HISTORY (HISTÓRICO)
# ========================================

@app.get("/clients/{client_id}/history")
def get_client_history(client_id: int, period: str = "all"):
    try:
        if client_id not in clients_db:
            return {"error": "Cliente não encontrado"}, 404
        
        # Filtrar transações completadas do cliente
        client_transactions = [
            t for t in transactions_db 
            if t.get('client_id') == client_id and t.get('status') == 'COMPLETED'
        ]
        
        # Calcular totais
        total_deposits = sum([
            t['amount'] for t in client_transactions 
            if t.get('type') == 'DEPOSIT'
        ])
        
        total_withdrawals = sum([
            t['amount'] for t in client_transactions 
            if t.get('type') == 'WITHDRAWAL'
        ])
        
        saldo_periodo = total_deposits - total_withdrawals
        
        # Formatar transações para UI
        formatted_transactions = []
        for t in client_transactions:
            client_name = clients_db.get(t['client_id'], {}).get('name', 'N/A')
            formatted_transactions.append({
                "id": t['id'],
                "cliente": client_name,
                "tipo": "📥 Depósito" if t['type'] == 'DEPOSIT' else "📤 Saque",
                "tipo_raw": t['type'],
                "valor": t['amount'],
                "valor_formatado": f"{t['amount']:.2f}",
                "data": t.get('created_at', ''),
                "descricao": t.get('description', ''),
                "status": t.get('status', 'PENDING')
            })
        
        # Ordenar por data (mais recente primeiro)
        formatted_transactions.sort(key=lambda x: x['data'], reverse=True)
        
        return {
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "saldo_periodo": saldo_periodo,
            "transactions": formatted_transactions,
            "total": len(formatted_transactions)
        }
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/bank/global/history")
def get_global_history(period: str = "all"):
    try:
        # Filtrar transações completadas
        completed_transactions = [
            t for t in transactions_db 
            if t.get('status') == 'COMPLETED'
        ]
        
        # Calcular totais
        total_deposits = sum([
            t['amount'] for t in completed_transactions 
            if t.get('type') == 'DEPOSIT'
        ])
        
        total_withdrawals = sum([
            t['amount'] for t in completed_transactions 
            if t.get('type') == 'WITHDRAWAL'
        ])
        
        saldo_periodo = total_deposits - total_withdrawals
        
        # Formatar transações para UI
        formatted_transactions = []
        for t in completed_transactions:
            client_name = clients_db.get(t['client_id'], {}).get('name', 'N/A')
            formatted_transactions.append({
                "id": t['id'],
                "cliente": client_name,
                "tipo": "📥 Depósito" if t['type'] == 'DEPOSIT' else "📤 Saque",
                "tipo_raw": t['type'],
                "valor": t['amount'],
                "valor_formatado": f"{t['amount']:.2f}",
                "data": t.get('created_at', ''),
                "descricao": t.get('description', ''),
                "status": t.get('status', 'PENDING')
            })
        
        # Ordenar por data (mais recente primeiro)
        formatted_transactions.sort(key=lambda x: x['data'], reverse=True)
        
        return {
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "saldo_periodo": saldo_periodo,
            "transactions": formatted_transactions,
            "total": len(formatted_transactions)
        }
    except Exception as e:
        logger.error(f"Erro ao buscar histórico global: {str(e)}")
        return {"error": str(e)}, 500

# ========================================
# BANK SIMULATION (SIMULAÇÃO BANCÁRIA)
# ========================================

@app.get("/bank-simulation/global")
def get_bank_simulation_global():
    try:
        total_clients = len(clients_db)
        total_operations = len(transactions_db)
        
        # Calcular total de depósitos (DEPOSITS)
        total_deposits = sum([
            t['amount'] for t in transactions_db 
            if t['type'] == "DEPOSIT" and t['status'] == "COMPLETED"
        ])
        
        # Calcular total de saques (WITHDRAWALS)
        total_withdrawals = sum([
            t['amount'] for t in transactions_db 
            if t['type'] == "WITHDRAWAL" and t['status'] == "COMPLETED"
        ])
        
        # Saldo geral = depósitos - saques
        saldo_geral = total_deposits - total_withdrawals
        
        # Contar clientes com saldo negativo
        clientes_negativo = len([c for c in clients_db.values() if c['saldo'] < 0])
        
        # Contar clientes com saldo positivo
        clientes_positivos = len([c for c in clients_db.values() if c['saldo'] > 0])
        
        return {
            "total_clients": total_clients,
            "total_operations": total_operations,
            "total_buy_brl": total_deposits,  # Mantém compatibilidade com frontend
            "total_sell_brl": total_withdrawals,  # Mantém compatibilidade com frontend
            "total_comprovantes": len(proofs_db),
            "saldo_geral": saldo_geral,
            "total_depositos": total_deposits,
            "total_saques": total_withdrawals,
            "clientes_em_negativo": clientes_negativo,
            "clientes_positivos": clientes_positivos
        }
    except Exception as e:
        logger.error(f"Erro em get_bank_simulation_global: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/bank-simulation/withdrawals")
def get_bank_simulation_withdrawals():
    try:
        # Pegar operações de saque reais (WITHDRAWAL)
        withdrawals = [
            t for t in transactions_db 
            if t['type'] == "WITHDRAWAL"
        ]
        
        # Ordenar por data (mais recente primeiro)
        withdrawals.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        result = []
        for t in withdrawals:
            client_id = t['client_id']
            client_name = clients_db.get(client_id, {}).get('name', 'Cliente Desconhecido')
            # Converter status para exibição: COMPLETED → APROVADO, PENDING → PENDENTE
            display_status = "APROVADO" if t['status'] == "COMPLETED" else "PENDENTE"
            result.append({
                "id": t['id'],
                "client_id": client_id,
                "client": client_name,
                "amount_brl": t['amount'],
                "amount_crypto": 0,  # Compatibilidade com frontend
                "status": display_status,
                "date": t.get('created_at', ''),
                "notes": t.get('description', '')
            })
        
        return result
    except Exception as e:
        logger.error(f"Erro em get_bank_simulation_withdrawals: {str(e)}")
        return {"error": str(e)}, 500

logger.info("✅ FLUXO CASH Backend iniciado com sucesso")
