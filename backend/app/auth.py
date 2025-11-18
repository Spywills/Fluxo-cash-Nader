"""
Sistema de Autenticação - FLUXO CASH
JWT tokens + bcrypt password hashing
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import get_supabase_client

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fluxo-cash-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Configurar bcrypt para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica e valida um JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_by_username(username: str):
    """Busca usuário por username"""
    supabase = get_supabase_client()
    response = supabase.table('users').select('*').eq('username', username).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


def get_user_by_email(email: str):
    """Busca usuário por email"""
    supabase = get_supabase_client()
    response = supabase.table('users').select('*').eq('email', email).execute()
    
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


def authenticate_user(username: str, password: str):
    """Autentica usuário com username e senha"""
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user['password_hash']):
        return False
    if not user.get('is_active', True):
        return False
    return user


def create_user(username: str, email: str, password: str, full_name: str = "", is_admin: bool = False):
    """Cria novo usuário"""
    supabase = get_supabase_client()
    
    # Verificar se username já existe
    if get_user_by_username(username):
        raise ValueError("Username já existe")
    
    # Verificar se email já existe
    if get_user_by_email(email):
        raise ValueError("Email já existe")
    
    # Criar usuário
    password_hash = get_password_hash(password)
    
    response = supabase.table('users').insert({
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'full_name': full_name,
        'is_active': True,
        'is_admin': is_admin
    }).execute()
    
    if response.data and len(response.data) > 0:
        user = response.data[0]
        # Remover password_hash da resposta
        user.pop('password_hash', None)
        return user
    
    raise Exception("Erro ao criar usuário")


def update_last_login(user_id: int):
    """Atualiza timestamp do último login"""
    supabase = get_supabase_client()
    supabase.table('users').update({
        'last_login': datetime.utcnow().isoformat()
    }).eq('id', user_id).execute()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency para obter usuário atual do token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Remover password_hash
    user.pop('password_hash', None)
    return user


async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency para verificar se usuário é admin"""
    if not current_user.get('is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: privilégios de administrador necessários"
        )
    return current_user
