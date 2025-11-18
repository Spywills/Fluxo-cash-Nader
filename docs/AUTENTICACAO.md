# 🔐 Sistema de Autenticação - FLUXO CASH

## Visão Geral

O FLUXO CASH agora possui um sistema completo de autenticação com login e senha, protegendo todas as funcionalidades do sistema.

## Características

- ✅ **Login com JWT**: Tokens seguros com expiração de 24 horas
- ✅ **Senhas criptografadas**: Usando bcrypt para hash seguro
- ✅ **Registro de usuários**: Criação de novas contas
- ✅ **Proteção de rotas**: Todas as APIs protegidas por autenticação
- ✅ **Níveis de acesso**: Suporte para usuários admin e regulares
- ✅ **Sessão persistente**: Token salvo no localStorage

## Estrutura do Banco de Dados

### Tabela `users`

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuração Inicial

### 1. Atualizar o Banco de Dados

Execute o schema atualizado no Supabase:

```bash
# O arquivo database_schema.sql já foi atualizado com a tabela users
```

No Supabase SQL Editor, execute o conteúdo de `backend/database_schema.sql`

### 2. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

Novas dependências adicionadas:
- `python-jose[cryptography]` - Para JWT tokens
- `passlib[bcrypt]` - Para hash de senhas
- `supabase` - Cliente Supabase

### 3. Configurar Variável de Ambiente (Opcional)

Adicione ao `.env` do backend:

```env
JWT_SECRET_KEY=sua-chave-secreta-aqui-mude-em-producao
```

Se não configurar, será usado um valor padrão (não recomendado para produção).

### 4. Criar Primeiro Usuário Admin

Execute o script para criar o usuário administrador:

```bash
python backend/create_admin_user.py
```

Exemplo de criação:
```
Username: admin
Email: admin@fluxocash.com
Senha: admin123
Nome completo: Administrador
Usuário administrador? (s/n): s
```

## Endpoints da API

### POST `/auth/login`

Faz login no sistema.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@fluxocash.com",
    "full_name": "Administrador",
    "is_admin": true
  }
}
```

### POST `/auth/register`

Registra novo usuário.

**Request:**
```json
{
  "username": "joao",
  "email": "joao@email.com",
  "password": "senha123",
  "full_name": "João Silva"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Usuário criado com sucesso",
  "user": {
    "id": 2,
    "username": "joao",
    "email": "joao@email.com",
    "full_name": "João Silva",
    "is_admin": false
  }
}
```

### GET `/auth/me`

Retorna informações do usuário logado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@fluxocash.com",
    "full_name": "Administrador",
    "is_admin": true
  }
}
```

### POST `/auth/logout`

Faz logout (token é removido no frontend).

## Frontend

### Fluxo de Autenticação

1. **Tela de Login**: Usuário não autenticado vê a tela de login
2. **Login**: Credenciais são enviadas para `/auth/login`
3. **Token**: JWT token é salvo no `localStorage`
4. **Acesso**: Token é enviado em todas as requisições via header `Authorization`
5. **Logout**: Token é removido do `localStorage`

### Interceptors Axios

O frontend possui interceptors configurados para:

- **Request**: Adicionar token JWT automaticamente em todas as requisições
- **Response**: Redirecionar para login se token expirar (401)

```javascript
// Adicionar token em todas as requisições
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Tratar token expirado
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Proteção de Rotas

### Backend

Todos os endpoints principais agora requerem autenticação:

```python
@app.get("/clients")
def get_clients(current_user: dict = Depends(get_current_user)):
    # Apenas usuários autenticados podem acessar
    ...

@app.post("/clients")
def create_client(
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    # Apenas usuários autenticados podem criar clientes
    ...
```

Para rotas que requerem admin:

```python
@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_admin_user)
):
    # Apenas admins podem deletar usuários
    ...
```

### Frontend

O App.jsx verifica autenticação antes de renderizar:

```javascript
// Verificar se está autenticado
if (!isAuthenticated) {
  return <Login onLoginSuccess={handleLoginSuccess} />;
}

// Renderizar app normalmente
return <App />;
```

## Segurança

### Boas Práticas Implementadas

1. ✅ **Senhas nunca são armazenadas em texto plano** - Apenas hash bcrypt
2. ✅ **Tokens JWT com expiração** - 24 horas de validade
3. ✅ **HTTPS recomendado em produção** - Para proteger tokens em trânsito
4. ✅ **Validação de entrada** - Username, email e senha validados
5. ✅ **Proteção contra força bruta** - Considere adicionar rate limiting

### Recomendações para Produção

1. **Altere o JWT_SECRET_KEY**: Use uma chave forte e única
2. **Use HTTPS**: Sempre em produção
3. **Configure CORS**: Restrinja origens permitidas
4. **Rate Limiting**: Adicione limite de tentativas de login
5. **Logs de Auditoria**: Registre tentativas de login
6. **2FA (Opcional)**: Considere autenticação de dois fatores

## Testando o Sistema

### 1. Criar usuário admin

```bash
python backend/create_admin_user.py
```

### 2. Iniciar o backend

```bash
cd backend
uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
```

### 3. Iniciar o frontend

```bash
cd frontend
npm run dev
```

### 4. Acessar o sistema

Abra `http://localhost:5174` e faça login com as credenciais criadas.

## Troubleshooting

### Erro: "Token inválido ou expirado"

- Token expirou (24h)
- Faça login novamente

### Erro: "Username ou senha incorretos"

- Verifique as credenciais
- Certifique-se que o usuário existe no banco

### Erro: "Usuário inativo"

- Usuário foi desativado
- Admin precisa reativar: `UPDATE users SET is_active = true WHERE username = 'usuario'`

### Frontend não redireciona para login

- Limpe o localStorage: `localStorage.clear()`
- Recarregue a página

## Próximos Passos

Funcionalidades que podem ser adicionadas:

- [ ] Recuperação de senha por email
- [ ] Autenticação de dois fatores (2FA)
- [ ] Gerenciamento de usuários (CRUD completo)
- [ ] Logs de auditoria de login
- [ ] Sessões múltiplas
- [ ] Refresh tokens
- [ ] OAuth2 (Google, Facebook, etc)

## Suporte

Para dúvidas ou problemas, consulte:
- Documentação do FastAPI: https://fastapi.tiangolo.com
- Documentação do Supabase: https://supabase.com/docs
- python-jose: https://python-jose.readthedocs.io
