"""
Database configuration for Supabase PostgreSQL
Using httpx directly for REST API calls
"""
import os
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente do arquivo .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# REST API URL
REST_URL = f"{SUPABASE_URL}/rest/v1"

# Headers para autenticação
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

class TableQuery:
    """Helper class para compatibilidade com sintaxe antiga"""
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self._filters = {}
        self._columns = "*"
        self._order_by = None
        self._order_desc = False
    
    def select(self, columns="*"):
        self._columns = columns
        return self
    
    def eq(self, column, value):
        self._filters[column] = f"eq.{value}"
        return self
    
    def order(self, column, desc=False):
        self._order_by = column
        self._order_desc = desc
        return self
    
    def execute(self):
        """Execute query"""
        params = {"select": self._columns}
        params.update(self._filters)
        if self._order_by:
            params["order"] = f"{self._order_by}.{'desc' if self._order_desc else 'asc'}"
        
        response = self.client.client.get(f"/{self.table_name}", params=params)
        response.raise_for_status()
        
        # Retornar objeto com .data
        class Response:
            def __init__(self, data):
                self.data = data
        
        return Response(response.json())

class SupabaseClient:
    """Cliente simples para Supabase usando httpx"""
    
    def __init__(self):
        self.client = httpx.Client(base_url=REST_URL, headers=HEADERS, timeout=30.0)
    
    def table(self, table_name: str):
        """Retorna TableQuery para compatibilidade"""
        return TableQuery(self, table_name)
    
    def select(self, table: str, columns: str = "*", filters: Dict[str, Any] = None) -> List[Dict]:
        """SELECT query"""
        params = {"select": columns}
        if filters:
            params.update(filters)
        response = self.client.get(f"/{table}", params=params)
        response.raise_for_status()
        return response.json()
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict:
        """INSERT query"""
        response = self.client.post(f"/{table}", json=data)
        response.raise_for_status()
        result = response.json()
        return result[0] if isinstance(result, list) else result
    
    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict:
        """UPDATE query"""
        params = filters
        response = self.client.patch(f"/{table}", json=data, params=params)
        response.raise_for_status()
        result = response.json()
        return result[0] if isinstance(result, list) and result else {}
    
    def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """DELETE query"""
        params = filters
        response = self.client.delete(f"/{table}", params=params)
        response.raise_for_status()
        return True
    
    def close(self):
        """Close connection"""
        self.client.close()

# Global client instance
_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client"""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        _client = SupabaseClient()
    return _client

def init_database():
    """Initialize database connection"""
    try:
        client = get_supabase_client()
        # Test connection
        client.select('clients', columns='count')
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False
