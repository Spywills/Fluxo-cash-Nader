"""
Script para criar usuário administrador inicial
Execute: python backend/create_admin_user.py
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.auth import create_user, get_user_by_username
from app.database import get_supabase_client

def create_admin():
    """Cria usuário admin padrão"""
    
    print("=" * 50)
    print("CRIAR USUÁRIO ADMINISTRADOR - FLUXO CASH")
    print("=" * 50)
    
    # Verificar se já existe um admin
    try:
        existing_admin = get_user_by_username("admin")
        if existing_admin:
            print("\n⚠️  Usuário 'admin' já existe!")
            print(f"   Email: {existing_admin['email']}")
            print(f"   Nome: {existing_admin.get('full_name', 'N/A')}")
            
            response = input("\nDeseja criar outro usuário? (s/n): ").lower()
            if response != 's':
                print("\n✅ Operação cancelada.")
                return
    except Exception as e:
        print(f"Erro ao verificar usuário existente: {e}")
    
    # Coletar dados do novo usuário
    print("\n📝 Preencha os dados do novo usuário:\n")
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Username é obrigatório!")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        return
    
    password = input("Senha (mínimo 6 caracteres): ").strip()
    if len(password) < 6:
        print("❌ Senha deve ter no mínimo 6 caracteres!")
        return
    
    full_name = input("Nome completo (opcional): ").strip()
    
    is_admin_input = input("Usuário administrador? (s/n): ").lower()
    is_admin = is_admin_input == 's'
    
    # Criar usuário
    try:
        print("\n⏳ Criando usuário...")
        user = create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            is_admin=is_admin
        )
        
        print("\n" + "=" * 50)
        print("✅ USUÁRIO CRIADO COM SUCESSO!")
        print("=" * 50)
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Nome: {user.get('full_name', 'N/A')}")
        print(f"Admin: {'Sim' if user.get('is_admin') else 'Não'}")
        print("=" * 50)
        print("\n🔐 Use estas credenciais para fazer login no sistema.")
        
    except ValueError as e:
        print(f"\n❌ Erro: {e}")
    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}")


if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
