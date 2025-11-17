"""
Database configuration for Supabase PostgreSQL
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Create Supabase client
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        # Criar cliente sem opções extras que podem causar conflito
        supabase = create_client(
            supabase_url=SUPABASE_URL,
            supabase_key=SUPABASE_KEY
        )
    return supabase

def init_database():
    """Initialize database connection"""
    try:
        client = get_supabase_client()
        # Test connection
        client.table('clients').select("count", count="exact").execute()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
