"""
FLUXO CASH - Backend com FastAPI + Supabase
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
    get_all_clients, get_client_by_id, create_client as db_create_client,
    update_client as db_update_client, delete_client as db_delete_client,
    update_client_balance, get_client_proofs, create_proof as db_create_proof,
    check_duplicate_proof, mark_proof_as_deposited, delete_proof as db_delete_proof,
    get_all_transactions, get_client_transactions, create_transaction as db_create_transaction,
    update_transaction as db_update_transaction, delete_transaction as db_delete_transaction,
    get_global_statistics
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(title="FLUXO CASH", version="2.0.0 - Supabase")

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
# HEALTH CHECK
# ========================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FLUXO CASH",
        "database": "Supabase PostgreSQL"
    }

# ========================================
# CLIENTS (CLIENTES)
# ========================================

@app.get("/clients")
def get_clients():
    try:
        clients = get_all_clients()
        # Adicionar saldo_atual para compatibilidade
        for client in clients:
            client['saldo_atual'] = client.get('saldo', 0.0)
        
        return {
            "clients": clients,
            "total": len(clients)
        }
    except Exception as e:
        logger.error(f"Erro em get_clients: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/clients/{client_id}")
def get_client(client_id: int):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        client['saldo_atual'] = client.get('saldo', 0.0)
        return {"client": client}
    except Exception as e:
        logger.error(f"Erro em get_client: {str(e)}")
        return {"error": str(e)}, 500

@app.post("/clients")
def create_client(data: Dict[str, Any] = Body(...)):
    try:
        name = data.get("name", "").strip()
        if not name:
            return {"error": "Nome do cliente é obrigatório"}, 400
        
        new_client = db_create_client(
            name=name,
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            document=data.get("document", ""),
            notes=data.get("notes", "")
        )
        
        logger.info(f"✅ Cliente criado: {new_client['name']} (ID: {new_client['id']})")
        
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
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        # Preparar dados para atualização
        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "email" in data:
            update_data["email"] = data["email"]
        if "phone" in data:
            update_data["phone"] = data["phone"]
        if "document" in data:
            update_data["document"] = data["document"]
        if "notes" in data:
            update_data["notes"] = data["notes"]
        
        updated_client = db_update_client(client_id, **update_data)
        logger.info(f"✅ Cliente atualizado: {updated_client['name']} (ID: {client_id})")
        
        return {
            "success": True,
            "client": updated_client,
            "data": updated_client
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {str(e)}")
        return {"error": str(e)}, 500

@app.put("/clients/{client_id}/notes")
def update_client_notes(client_id: int, data: Dict[str, Any] = Body(...)):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        updated_client = db_update_client(client_id, notes=data.get("notes", ""))
        logger.info(f"✅ Notas do cliente atualizadas: {updated_client['name']} (ID: {client_id})")
        
        return {
            "success": True,
            "client": updated_client,
            "data": updated_client
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar notas: {str(e)}")
        return {"error": str(e)}, 500

@app.delete("/clients/{client_id}")
def delete_client(client_id: int):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        client_name = client["name"]
        db_delete_client(client_id)
        
        logger.info(f"✅ Cliente deletado: {client_name} (ID: {client_id})")
        
        return {
            "success": True,
            "message": f"Cliente {client_name} deletado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao deletar cliente: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/clients/{client_id}/balance")
def get_client_balance(client_id: int):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
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

logger.info("✅ FLUXO CASH Backend (Supabase) iniciado com sucesso")
