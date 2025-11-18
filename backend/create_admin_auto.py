"""
Script para criar usuário administrador automaticamente
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Carregar variáveis de ambiente de staging
from dotenv import load_dotenv
env_path = backend_dir / '.env.staging'
load_dotenv(dotenv_path=env_path)

from app.auth import create_user, get_user_by_username

def create_admin_auto():
    """Cria usuário admin automaticamente"""
    
    print("=" * 50)
    print("CRIAR USUÁRIO ADMIN - STAGING")
    print("=" * 50)
    
    # Verificar se já existe
    try:
        existing_admin = get_user_by_username("admin")
        if existing_admin:
            print("\n✅ Usuário 'admin' já existe!")
            print(f"   Email: {existing_admin['email']}")
            print(f"   Nome: {existing_admin.get('full_name', 'N/A')}")
            print("\n🔐 Use: admin / admin123 para fazer login")
            return
    except Exception as e:
        print(f"Verificando usuário... {e}")
    
    # Criar usuário admin padrão
    try:
        print("\n⏳ Criando usuário admin...")
        # Senha curta para evitar erro do bcrypt
        password = "admin123"
        user = create_user(
            username="admin",
            email="admin@staging.local",
            password=password,
            full_name="Admin",
            is_admin=True
        )
        
        print("\n" + "=" * 50)
        print("✅ USUÁRIO ADMIN CRIADO COM SUCESSO!")
        print("=" * 50)
        print(f"Username: admin")
        print(f"Email: admin@staging.local")
        print(f"Senha: admin123")
        print(f"Admin: Sim")
        print("=" * 50)
        print("\n🔐 Use estas credenciais para fazer login")
        
    except ValueError as e:
        print(f"\n❌ Erro: {e}")
    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        create_admin_auto()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
