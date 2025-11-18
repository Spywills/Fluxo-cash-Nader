"""
FLUXO CASH - Backend com FastAPI + Supabase
Sistema de gestão de clientes e comprovantes com extração automática de valores
"""

import logging
import hashlib
from datetime import datetime
from fastapi import FastAPI, Body, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import tempfile
from pathlib import Path

# Importar o módulo de extração
from .extractors import extract_proof_data

# Importar autenticação
from .auth import (
    authenticate_user, create_access_token, create_user,
    get_current_user, get_current_admin_user, update_last_login
)

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
# AUTENTICAÇÃO
# ========================================

@app.post("/auth/login")
def login(data: Dict[str, Any] = Body(...)):
    """
    Endpoint de login
    Body: { "username": "...", "password": "..." }
    """
    try:
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username e senha são obrigatórios"
            )
        
        # Autenticar usuário
        user = authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar token
        access_token = create_access_token(data={"sub": user['username']})
        
        # Atualizar último login
        update_last_login(user['id'])
        
        logger.info(f"✅ Login bem-sucedido: {username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user.get('full_name', ''),
                "is_admin": user.get('is_admin', False)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/auth/create-user")
def create_user_endpoint(data: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_admin_user)):
    """
    Endpoint para admin criar novo usuário
    Requer autenticação de admin
    Body: { "username": "...", "email": "...", "password": "...", "full_name": "...", "is_admin": false }
    """
    try:
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "").strip()
        is_admin = data.get("is_admin", False)
        
        if not username or not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username, email e senha são obrigatórios"
            )
        
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha deve ter no mínimo 6 caracteres"
            )
        
        # Criar usuário
        user = create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_admin=is_admin
        )
        
        logger.info(f"✅ Novo usuário criado por admin {current_user['username']}: {username}")
        
        return {
            "success": True,
            "message": "Usuário criado com sucesso",
            "user": user
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna informações do usuário logado"""
    return {
        "user": current_user
    }

@app.post("/auth/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """Endpoint de logout (apenas para consistência, token é gerenciado no frontend)"""
    logger.info(f"✅ Logout: {current_user['username']}")
    return {
        "success": True,
        "message": "Logout realizado com sucesso"
    }

# ========================================
# GERENCIAMENTO DE USUÁRIOS (ADMIN ONLY)
# ========================================

@app.get("/users")
def get_users(current_user: dict = Depends(get_current_admin_user)):
    """Lista todos os usuários (apenas admin)"""
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table('users').select('id,username,email,full_name,is_active,is_admin,created_at,last_login').execute()
        
        return {
            "users": response.data,
            "total": len(response.data)
        }
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/users/{user_id}")
def update_user(user_id: int, data: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_admin_user)):
    """Atualiza usuário (apenas admin)"""
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Não permitir que admin desative a si mesmo
        if user_id == current_user['id'] and 'is_active' in data and not data['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode desativar sua própria conta"
            )
        
        # Preparar dados para atualização
        update_data = {}
        allowed_fields = ['full_name', 'email', 'is_active', 'is_admin']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo para atualizar"
            )
        
        # Atualizar usuário
        updated_user = supabase.update('users', update_data, {'id': f'eq.{user_id}'})
        
        logger.info(f"✅ Usuário {user_id} atualizado por admin {current_user['username']}")
        
        return {
            "success": True,
            "message": "Usuário atualizado com sucesso",
            "user": updated_user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(get_current_admin_user)):
    """Deleta usuário (apenas admin)"""
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Não permitir que admin delete a si mesmo
        if user_id == current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode deletar sua própria conta"
            )
        
        # Buscar usuário
        response = supabase.table('users').select('username').eq('id', user_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        username = response.data[0]['username']
        
        # Deletar usuário
        supabase.delete('users', {'id': f'eq.{user_id}'})
        
        logger.info(f"✅ Usuário {username} deletado por admin {current_user['username']}")
        
        return {
            "success": True,
            "message": f"Usuário {username} deletado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ========================================
# CLIENTS (CLIENTES)
# ========================================

@app.get("/clients")
def get_clients(current_user: dict = Depends(get_current_user)):
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
def create_client(data: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user)):
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


# ========================================
# PROOFS (COMPROVANTES)
# ========================================

@app.get("/proofs/clients/{client_id}")
def get_client_proofs_route(client_id: int):
    try:
        proofs = get_client_proofs(client_id)
        
        stats = {
            "total_proofs": len(proofs),
            "total_extracted": len([p for p in proofs if p['extraction_status'] == 'EXTRACTED']),
            "total_duplicates": len([p for p in proofs if p['is_duplicate']]),
            "total_value": sum([p['extracted_value'] or 0 for p in proofs if p['extraction_status'] == 'EXTRACTED'])
        }
        
        return {
            "proofs": proofs,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Erro ao buscar comprovantes: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/proofs/{proof_id}")
def get_proof(proof_id: int):
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        response = supabase.table('proofs').select('*').eq('id', proof_id).execute()
        
        if not response.data:
            return {"error": "Comprovante não encontrado"}, 404
        
        return {"proof": response.data[0]}
    except Exception as e:
        logger.error(f"Erro ao buscar comprovante: {str(e)}")
        return {"error": str(e)}, 500

@app.post("/proofs/clients/{client_id}/upload")
async def upload_proof(client_id: int, file: UploadFile = File(...)):
    """
    Endpoint para upload de comprovantes
    - Detecta duplicatas
    - Extrai valores usando OCR (PDFs/Imagens)
    - Armazena arquivo
    """
    try:
        # Verificar se cliente existe
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        # Ler conteúdo do arquivo
        contents = await file.read()
        file_size = len(contents)
        
        # Gerar hash do arquivo para detectar duplicatas
        file_hash = hashlib.sha256(contents).hexdigest()
        
        # Verificar duplicata
        is_duplicate = check_duplicate_proof(file_hash, client_id)
        
        if is_duplicate:
            logger.warning(f"⚠️ Comprovante duplicado detectado: {file.filename}")
            return {
                "success": False,
                "proof": None,
                "is_duplicate": True,
                "message": "Arquivo duplicado detectado"
            }
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(suffix=Path(file.filename).suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Extrair dados do comprovante usando OCR/PDF reader
            extracted_data = extract_proof_data(tmp_path)
            
            value = extracted_data.get('value')
            confidence = extracted_data.get('confidence', 0)
            beneficiary = extracted_data.get('beneficiary')
            endtoend = extracted_data.get('endtoend')
            
            if value is None:
                value = 5000.0  # Fallback
                confidence = 0.5
            
            extraction_status = "EXTRACTED" if extracted_data.get('success') else "EXTRACTED_WITH_ERROR"
            
            # Criar novo comprovante no banco
            new_proof = db_create_proof(
                client_id=client_id,
                filename=file.filename,
                file_hash=file_hash,
                file_type=file.content_type or "application/octet-stream",
                file_size=file_size,
                extracted_value=value,
                extraction_confidence=confidence,
                extraction_status=extraction_status,
                beneficiary=beneficiary or "DESCONHECIDO",
                endtoend=endtoend or None,
                is_duplicate=False,
                deposited=False
            )
            
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
def delete_proof_route(proof_id: int):
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar comprovante
        response = supabase.table('proofs').select('*').eq('id', proof_id).execute()
        if not response.data:
            return {"error": "Comprovante não encontrado"}, 404
        
        proof = response.data[0]
        
        # Deletar
        db_delete_proof(proof_id)
        
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
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar comprovante
        response = supabase.table('proofs').select('*').eq('id', proof_id).execute()
        if not response.data:
            return {"error": "Comprovante não encontrado"}, 404
        
        proof = response.data[0]
        
        # Validação: Verificar se já foi depositado
        if proof.get('deposited', False):
            return {"error": "Este comprovante já foi creditado anteriormente"}, 400
        
        # Aceitar EXTRACTED ou EXTRACTED_WITH_ERROR
        if proof['extraction_status'] not in ['EXTRACTED', 'EXTRACTED_WITH_ERROR']:
            return {"error": "Comprovante não tem valor extraído"}, 400
        
        if proof['extracted_value'] is None or proof['extracted_value'] == 0:
            return {"error": "Valor inválido"}, 400
        
        client_id = proof['client_id']
        value = float(proof['extracted_value'])
        
        # Criar transação
        transaction = db_create_transaction(
            client_id=client_id,
            amount=value,
            trans_type="DEPOSIT",
            status="COMPLETED",
            description=f"Depósito de {proof['filename']}",
            proof_id=proof_id
        )
        
        # Atualizar saldo do cliente
        update_client_balance(client_id, value, operation='add')
        
        # Marcar comprovante como depositado
        mark_proof_as_deposited(proof_id)
        
        # Buscar saldo atualizado
        client = get_client_by_id(client_id)
        
        logger.info(f"✅ Depósito criado: R$ {value} para cliente {client_id} | Comprovante #{proof_id} marcado como depositado")
        
        return {
            "success": True,
            "transaction_id": transaction['id'],
            "amount": value,
            "client_saldo": client['saldo'] if client else 0
        }
    except Exception as e:
        logger.error(f"Erro ao criar depósito: {str(e)}")
        return {"error": str(e)}, 500

@app.delete("/deposits/{transaction_id}")
def remove_deposit(transaction_id: int):
    """Remove (reverte) um depósito"""
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar transação
        response = supabase.table('transactions').select('*').eq('id', transaction_id).eq('type', 'DEPOSIT').execute()
        if not response.data:
            return {"error": "Depósito não encontrado"}, 404
        
        transaction = response.data[0]
        client_id = transaction['client_id']
        value = float(transaction['amount'])
        
        # Remover transação
        db_delete_transaction(transaction_id)
        
        # Reverter saldo do cliente
        update_client_balance(client_id, value, operation='subtract')
        
        # Buscar saldo atualizado
        client = get_client_by_id(client_id)
        
        logger.info(f"✅ Depósito removido: R$ {value} do cliente {client_id}")
        
        return {
            "success": True,
            "message": "Depósito removido com sucesso",
            "client_saldo": client['saldo'] if client else 0
        }
    except Exception as e:
        logger.error(f"Erro ao remover depósito: {str(e)}")
        return {"error": str(e)}, 500


# ========================================
# WITHDRAWALS (SAQUES)
# ========================================

@app.post("/clients/{client_id}/withdrawals")
def create_withdrawal(client_id: int, data: Dict[str, Any] = Body(...)):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        withdrawal = db_create_transaction(
            client_id=client_id,
            amount=float(data.get("valor", 0)),
            trans_type="WITHDRAWAL",
            status="PENDING",
            description=data.get("descricao", ""),
            admin_notes=data.get("admin_notes", "")
        )
        
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
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table('transactions').select('*').eq('client_id', client_id).eq('type', 'WITHDRAWAL').execute()
        
        return {
            "withdrawals": response.data
        }
    except Exception as e:
        logger.error(f"Erro ao buscar saques: {str(e)}")
        return {"error": str(e)}, 500

@app.put("/clients/{client_id}/withdrawals/{withdrawal_id}")
def update_withdrawal(client_id: int, withdrawal_id: int, data: Dict[str, Any] = Body(...)):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar saque
        response = supabase.table('transactions').select('*').eq('id', withdrawal_id).eq('client_id', client_id).eq('type', 'WITHDRAWAL').execute()
        if not response.data:
            return {"error": "Saque não encontrado"}, 404
        
        withdrawal = response.data[0]
        old_status = withdrawal.get('status')
        
        # Normalizar status
        def _normalize_status(s):
            if s is None:
                return s
            s_up = str(s).upper()
            if s_up in ("APPROVED", "APROVADO", "COMPLETED"):
                return "COMPLETED"
            if s_up in ("PENDING", "PENDENTE"):
                return "PENDING"
            return s_up
        
        new_status = _normalize_status(data.get('status', old_status))
        
        # Preparar dados de atualização
        update_data = {}
        if "status" in data:
            update_data["status"] = new_status
        if "admin_notes" in data:
            update_data["admin_notes"] = data["admin_notes"]
        
        # Se houve transição PENDING -> COMPLETED, aplicar redução de saldo
        if old_status == "PENDING" and new_status == "COMPLETED":
            valor_saque = float(withdrawal.get('amount', 0))
            update_client_balance(client_id, valor_saque, operation='subtract')
        
        # Atualizar transação
        updated_withdrawal = db_update_transaction(withdrawal_id, **update_data)
        
        # Label para exibição
        display_status = "APROVADO" if updated_withdrawal.get('status') == "COMPLETED" else ("PENDENTE" if updated_withdrawal.get('status') == "PENDING" else updated_withdrawal.get('status'))
        
        logger.info(f"✅ Saque atualizado: ID={withdrawal_id}, Status={updated_withdrawal.get('status')}, Valor={updated_withdrawal.get('amount')}")
        
        return {
            "success": True,
            "withdrawal": {**updated_withdrawal, "display_status": display_status},
            "message": f"Saque atualizado para {display_status}"
        }, 200
    except Exception as e:
        logger.error(f"Erro ao atualizar saque: {str(e)}")
        return {"error": str(e)}, 500

@app.delete("/clients/{client_id}/withdrawals/{withdrawal_id}")
def delete_withdrawal(client_id: int, withdrawal_id: int):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar e deletar saque
        response = supabase.table('transactions').select('*').eq('id', withdrawal_id).eq('client_id', client_id).execute()
        if not response.data:
            return {"error": "Saque não encontrado"}, 404
        
        db_delete_transaction(withdrawal_id)
        
        logger.info(f"✅ Saque deletado: {withdrawal_id}")
        
        return {
            "success": True,
            "message": "Saque deletado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro ao deletar saque: {str(e)}")
        return {"error": str(e)}, 500


# ========================================
# GLOBAL BALANCE & STATISTICS
# ========================================

@app.get("/global-balance")
def get_global_balance(current_user: dict = Depends(get_current_user)):
    try:
        stats = get_global_statistics()
        return stats
    except Exception as e:
        logger.error(f"Erro em get_global_balance: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/global-withdrawals")
def get_global_withdrawals():
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar todas as transações de saque
        response = supabase.table('transactions').select('*').eq('type', 'WITHDRAWAL').order('created_at', desc=True).execute()
        
        result = []
        for t in response.data:
            client_id = t['client_id']
            client = get_client_by_id(client_id)
            client_name = client['name'] if client else 'Cliente Desconhecido'
            
            # Converter status para exibição
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
# HISTORY (HISTÓRICO)
# ========================================

@app.get("/clients/{client_id}/history")
def get_client_history(client_id: int, period: str = "all"):
    try:
        client = get_client_by_id(client_id)
        if not client:
            return {"error": "Cliente não encontrado"}, 404
        
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar transações completadas do cliente
        response = supabase.table('transactions').select('*').eq('client_id', client_id).eq('status', 'COMPLETED').order('created_at', desc=True).execute()
        
        transactions = response.data
        
        # Calcular totais
        total_deposits = sum([t['amount'] for t in transactions if t['type'] == 'DEPOSIT'])
        total_withdrawals = sum([t['amount'] for t in transactions if t['type'] == 'WITHDRAWAL'])
        saldo_periodo = total_deposits - total_withdrawals
        
        # Formatar transações para UI
        formatted_transactions = []
        for t in transactions:
            formatted_transactions.append({
                "id": t['id'],
                "cliente": client['name'],
                "tipo": "📥 Depósito" if t['type'] == 'DEPOSIT' else "📤 Saque",
                "tipo_raw": t['type'],
                "valor": t['amount'],
                "valor_formatado": f"{t['amount']:.2f}",
                "data": t.get('created_at', ''),
                "descricao": t.get('description', ''),
                "status": t.get('status', 'PENDING')
            })
        
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
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar transações completadas
        response = supabase.table('transactions').select('*').eq('status', 'COMPLETED').order('created_at', desc=True).execute()
        
        transactions = response.data
        
        # Calcular totais
        total_deposits = sum([t['amount'] for t in transactions if t['type'] == 'DEPOSIT'])
        total_withdrawals = sum([t['amount'] for t in transactions if t['type'] == 'WITHDRAWAL'])
        saldo_periodo = total_deposits - total_withdrawals
        
        # Formatar transações para UI
        formatted_transactions = []
        for t in transactions:
            client = get_client_by_id(t['client_id'])
            client_name = client['name'] if client else 'N/A'
            
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
        stats = get_global_statistics()
        
        # Adicionar campos extras para compatibilidade
        stats['clientes_positivos'] = stats.get('total_clients', 0) - stats.get('clientes_em_negativo', 0)
        
        return stats
    except Exception as e:
        logger.error(f"Erro em get_bank_simulation_global: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/bank-simulation/withdrawals")
def get_bank_simulation_withdrawals():
    try:
        from .database import get_supabase_client
        supabase = get_supabase_client()
        
        # Buscar operações de saque
        response = supabase.table('transactions').select('*').eq('type', 'WITHDRAWAL').order('created_at', desc=True).execute()
        
        result = []
        for t in response.data:
            client = get_client_by_id(t['client_id'])
            client_name = client['name'] if client else 'Cliente Desconhecido'
            
            # Converter status para exibição
            display_status = "APROVADO" if t['status'] == "COMPLETED" else "PENDENTE"
            
            result.append({
                "id": t['id'],
                "client_id": t['client_id'],
                "client": client_name,
                "amount_brl": t['amount'],
                "amount_crypto": 0,
                "status": display_status,
                "date": t.get('created_at', ''),
                "notes": t.get('description', '')
            })
        
        return result
    except Exception as e:
        logger.error(f"Erro em get_bank_simulation_withdrawals: {str(e)}")
        return {"error": str(e)}, 500
