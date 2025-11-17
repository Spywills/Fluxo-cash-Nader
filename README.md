# 💰 FLUXO CASH

Sistema de gestão financeira para controle de clientes, depósitos e saques com upload e extração automática de valores de comprovantes.

## 🚀 Funcionalidades

- ✅ **Gestão de Clientes** - Cadastro e gerenciamento de clientes
- ✅ **Upload de Comprovantes** - Envio de PDFs e imagens
- ✅ **Extração Automática** - OCR para extrair valores dos comprovantes
- ✅ **Detecção de Duplicatas** - Evita upload de comprovantes duplicados
- ✅ **Controle de Depósitos** - Aprovação e crédito de valores
- ✅ **Gestão de Saques** - Solicitação e aprovação de saques
- ✅ **Histórico Completo** - Visualização de todas as transações
- ✅ **Dashboard em Tempo Real** - Visão geral do sistema
- ✅ **Resumo Bancário** - Totais de depósitos, saques e clientes negativos

## 🛠️ Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **Python 3.9+** - Linguagem de programação
- **Uvicorn** - Servidor ASGI
- **PyPDF2** - Extração de texto de PDFs
- **Pillow** - Processamento de imagens

### Frontend
- **React** - Biblioteca JavaScript para UI
- **Vite** - Build tool e dev server
- **Tailwind CSS** - Framework CSS utility-first
- **Lucide React** - Ícones modernos
- **Axios** - Cliente HTTP

## 📦 Instalação

### Pré-requisitos
- Python 3.9 ou superior
- Node.js 16 ou superior
- npm ou yarn

### Backend

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r backend/requirements.txt
```

### Frontend

```bash
# Entrar na pasta do frontend
cd frontend

# Instalar dependências
npm install
```

## 🚀 Executar o Sistema

### Backend

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar servidor
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

O backend estará disponível em: `http://127.0.0.1:8000`

### Frontend

```bash
# Em outro terminal
cd frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:5174`

## 📁 Estrutura do Projeto

```
FLUXOCASH/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # API principal
│   │   ├── models.py        # Modelos de dados
│   │   └── extractors.py    # Extração de valores
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── pages/           # Páginas da aplicação
│   │   ├── services/        # Serviços e API
│   │   └── utils/           # Utilitários
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 🔒 Validações Implementadas

- ✅ Comprovantes duplicados são detectados automaticamente
- ✅ Comprovantes já creditados não podem ser aprovados novamente
- ✅ Validação de campos obrigatórios
- ✅ Controle de saldo por cliente
- ✅ Histórico completo de transações

## 📝 API Endpoints

### Clientes
- `GET /clients` - Listar todos os clientes
- `GET /clients/{id}` - Obter cliente específico
- `POST /clients` - Criar novo cliente
- `PUT /clients/{id}` - Atualizar cliente
- `DELETE /clients/{id}` - Deletar cliente

### Comprovantes
- `GET /proofs/clients/{client_id}` - Listar comprovantes do cliente
- `POST /proofs/clients/{client_id}/upload` - Upload de comprovante
- `DELETE /proofs/{proof_id}` - Deletar comprovante

### Depósitos
- `POST /deposits/proofs/{proof_id}` - Criar depósito a partir de comprovante

### Saques
- `GET /clients/{client_id}/withdrawals` - Listar saques do cliente
- `POST /clients/{client_id}/withdrawals` - Criar novo saque
- `PUT /clients/{client_id}/withdrawals/{withdrawal_id}` - Atualizar saque
- `DELETE /clients/{client_id}/withdrawals/{withdrawal_id}` - Deletar saque

### Resumo
- `GET /global-balance` - Saldo global do sistema
- `GET /bank-simulation/global` - Resumo bancário completo

## 🎨 Interface

O sistema possui uma interface moderna e responsiva com:
- Dashboard com KPIs em tempo real
- Gestão visual de clientes
- Upload drag-and-drop de comprovantes
- Galeria de comprovantes com preview
- Histórico de transações filtrado
- Notificações toast para feedback

## 🔄 Próximas Melhorias

- [ ] Integração com banco de dados (SQLite/PostgreSQL)
- [ ] Autenticação e autorização de usuários
- [ ] Relatórios em PDF
- [ ] Exportação de dados (Excel/CSV)
- [ ] Notificações por email
- [ ] API de webhooks
- [ ] Backup automático

## 📄 Licença

Este projeto é privado e proprietário.

## 👨‍💻 Desenvolvedor

Desenvolvido com ❤️ para gestão financeira eficiente.
