# 📄 Fluxo Completo de Upload de Comprovante

Documentação detalhada de como o sistema processa um comprovante desde o upload até o crédito.

---

## 🎯 Visão Geral

```
USUÁRIO → FRONTEND → BACKEND → EXTRAÇÃO → VALIDAÇÃO → ARMAZENAMENTO → APROVAÇÃO → CRÉDITO
```

---

## 📊 Fluxo Detalhado

### 1️⃣ **UPLOAD NO FRONTEND**

**Arquivo**: `frontend/src/components/ui/FileUpload.jsx`

**O que acontece:**
- Usuário arrasta ou seleciona arquivo (PDF, PNG, JPG)
- Validação de tamanho (máx 10MB)
- Validação de tipo de arquivo
- Arquivo é enviado via FormData

**Código:**
```javascript
const handleUpload = async (file) => {
  const response = await uploadProof(clientId, file);
  // ...
}
```

---

### 2️⃣ **RECEBIMENTO NO BACKEND**

**Arquivo**: `backend/app/main.py` → Endpoint `/proofs/clients/{client_id}/upload`

**O que acontece:**

#### A. Validações Iniciais
```python
# 1. Verifica se cliente existe
if client_id not in clients_db:
    return {"error": "Cliente não encontrado"}, 404

# 2. Lê conteúdo do arquivo
contents = await file.read()
file_size = len(contents)

# 3. Gera hash SHA-256 para detectar duplicatas
file_hash = hashlib.sha256(contents).hexdigest()
```

#### B. Detecção de Duplicatas
```python
# Verifica se já existe comprovante com mesmo hash para este cliente
is_duplicate = check_duplicate(file_hash, client_id)

if is_duplicate:
    return {
        "success": False,
        "is_duplicate": True,
        "message": "Arquivo duplicado detectado"
    }
```

---

### 3️⃣ **EXTRAÇÃO DE DADOS**

**Arquivo**: `backend/app/extractors.py` → Função `extract_proof_data()`

**O que acontece:**

#### A. Salvar Arquivo Temporário
```python
with tempfile.NamedTemporaryFile(suffix=Path(file.filename).suffix, delete=False) as tmp:
    tmp.write(contents)
    tmp_path = tmp.name
```

#### B. Identificar Tipo de Arquivo
```python
if file_ext == '.pdf':
    raw_text, confidence = extract_text_from_pdf(file_path)
elif file_ext in ['.jpg', '.jpeg', '.png']:
    raw_text, confidence = extract_text_from_image(file_path)
```

#### C. Extração de Texto

**Para PDFs:**
1. Usa `pdfplumber` para extrair texto nativo
2. Se não tiver texto, converte para imagem e faz OCR
3. Confiança alta (0.95) para texto nativo

**Para Imagens:**
1. Pré-processamento com OpenCV:
   - Converte para escala de cinza
   - Redimensiona se necessário (mín 1000px)
   - Remove ruído (denoising)
   - Melhora contraste
   - Aplica threshold adaptativo
2. OCR com Tesseract (idioma português)
3. Confiança baseada no tamanho do texto extraído

#### D. Extração de Valores Específicos

**1. Valor Monetário** (`parse_amount`)
```python
# Regex busca padrões como:
# - "Valor R$ 143.800,00"
# - "R$ 143.800,00"
# - "143.800,00"

# Normalização:
# 143.800,00 → remove pontos → troca vírgula por ponto → 143800.00
# Validação: 0 < valor < 10.000.000
```

**2. Beneficiário** (`parse_beneficiary`)
```python
# Regex busca padrões como:
# - "Favorecido Nome: JOÃO SILVA"
# - "Beneficiário: MARIA SANTOS"
# Remove labels (CPF, CNPJ, etc.)
```

**3. EndToEnd** (`parse_endtoend`)
```python
# Regex busca padrões como:
# - "E12345678901234567890ABCD"
# - "ID da transação: ABC123..."
# Prioriza IDs que começam com 'E' (padrão PIX)
```

**4. Data** (`parse_date`)
```python
# Regex busca padrões como:
# - "03/11/2025"
# - "2025-11-03"
# Converte para formato ISO (YYYY-MM-DD)
```

#### E. Resultado da Extração
```python
{
    'value': 143800.00,           # float ou None
    'date': '2025-11-03',         # string ISO ou None
    'beneficiary': 'JOÃO SILVA',  # string ou None
    'endtoend': 'E123...',        # string ou None
    'raw_text': '...',            # primeiros 500 chars
    'confidence': 0.85,           # 0.0 a 1.0
    'success': True,              # True se extraiu valor
    'error': None                 # mensagem de erro ou None
}
```

---

### 4️⃣ **ARMAZENAMENTO**

**Arquivo**: `backend/app/main.py`

**O que acontece:**

```python
# Cria registro do comprovante
new_proof = {
    "id": new_id,
    "client_id": client_id,
    "filename": file.filename,
    "file_type": file.content_type,
    "file_size": file_size,
    "extracted_value": value,              # ← Valor extraído
    "extraction_confidence": confidence,    # ← Confiança da extração
    "extraction_status": "EXTRACTED",       # ← Status
    "beneficiary": beneficiary,             # ← Beneficiário
    "endtoend": endtoend,                   # ← ID da transação
    "is_duplicate": False,
    "deposited": False,                     # ← Flag importante!
    "file_hash": file_hash,
    "uploaded_at": datetime.now().isoformat()
}

# Armazena em memória (ou banco de dados)
proofs_db[new_id] = new_proof
```

**Resposta ao Frontend:**
```python
return {
    "success": True,
    "proof": new_proof,
    "is_duplicate": False,
    "message": f"Comprovante enviado com sucesso | Valor extraído: R$ {value:.2f}"
}
```

---

### 5️⃣ **VISUALIZAÇÃO NO FRONTEND**

**Arquivo**: `frontend/src/components/ui/ProofGallery.jsx`

**O que acontece:**

```javascript
// Carrega comprovantes do cliente
const response = await getClientProofs(clientId);
setProofs(response.data.proofs);

// Exibe cada comprovante com:
// - Nome do arquivo
// - Tamanho
// - Data de upload
// - Valor extraído (se disponível)
// - Badge "Duplicado" (se is_duplicate)
// - Botão "Depositar" (se extracted_value && !deposited)
// - Badge "✓ Depositado" (se deposited)
```

---

### 6️⃣ **APROVAÇÃO/DEPÓSITO**

**Arquivo**: `frontend/src/components/ui/ProofGallery.jsx` → Função `handleDeposit()`

**O que acontece:**

#### A. Frontend envia requisição
```javascript
const resp = await api.post(`/deposits/proofs/${proofId}`);
```

#### B. Backend processa
**Arquivo**: `backend/app/main.py` → Endpoint `/deposits/proofs/{proof_id}`

```python
# 1. Busca comprovante
proof = proofs_db[proof_id]

# 2. VALIDAÇÃO CRÍTICA: Verifica se já foi depositado
if proof.get('deposited', False):
    return {"error": "Este comprovante já foi creditado anteriormente"}, 400

# 3. Valida status e valor
if proof['extraction_status'] != 'EXTRACTED':
    return {"error": "Comprovante não tem valor extraído"}, 400

if proof['extracted_value'] is None or proof['extracted_value'] == 0:
    return {"error": "Valor inválido"}, 400

# 4. Cria transação
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

# 5. Atualiza saldo do cliente
clients_db[client_id]['saldo'] += value
clients_db[client_id]['total_deposits'] += value

# 6. MARCA COMPROVANTE COMO DEPOSITADO (evita duplicação)
proofs_db[proof_id]['deposited'] = True

# 7. Retorna sucesso
return {
    "success": True,
    "transaction_id": transaction_counter,
    "amount": value,
    "client_saldo": clients_db[client_id]['saldo']
}
```

#### C. Frontend atualiza interface
```javascript
// Atualiza estado local
setProofs(prev => prev.map(p => 
  p.id === proofId ? { ...p, deposited: true } : p
));

// Atualiza saldo do cliente (callback)
onBalanceUpdate(resp.data.client_saldo);

// Mostra notificação
showToast.success('Depósito criado!', `R$ ${value}`);
```

---

## 🔒 Validações de Segurança

### 1. Detecção de Duplicatas
- ✅ Hash SHA-256 do arquivo
- ✅ Verifica por cliente (mesmo arquivo pode ser usado por clientes diferentes)
- ✅ Bloqueia upload se duplicado

### 2. Validação de Depósito Único
- ✅ Flag `deposited` no comprovante
- ✅ Verificação no backend antes de criar transação
- ✅ Botão desaparece no frontend após depósito
- ✅ Erro 400 se tentar depositar novamente via API

### 3. Validação de Valores
- ✅ Valor deve estar entre 0 e 10 milhões
- ✅ Valor deve ser extraído com sucesso
- ✅ Status deve ser "EXTRACTED"

---

## 📈 Fluxo de Estados

```
UPLOAD
  ↓
UPLOADED (extraction_status: "UPLOADED", deposited: false)
  ↓
EXTRACTING (processando OCR)
  ↓
EXTRACTED (extraction_status: "EXTRACTED", deposited: false)
  ↓ [Admin clica "Depositar"]
  ↓
DEPOSITADO (deposited: true)
  ↓
[Botão "Depositar" desaparece]
[Badge "✓ Depositado" aparece]
```

---

## 🎯 Pontos Importantes

1. **Extração é automática** - Acontece no momento do upload
2. **Valor é sugerido** - Admin pode ver antes de aprovar
3. **Depósito é manual** - Admin precisa clicar em "Depositar"
4. **Proteção contra duplicação** - Múltiplas camadas de validação
5. **Rastreabilidade** - Cada transação tem proof_id vinculado
6. **Confiança da extração** - Sistema informa o nível de certeza

---

## 🔧 Tecnologias Usadas

- **OCR**: Tesseract (pytesseract)
- **PDF**: pdfplumber + pdf2image
- **Imagem**: Pillow (PIL) + OpenCV
- **Regex**: Padrões complexos para extração
- **Hash**: SHA-256 para detecção de duplicatas
- **Validação**: Múltiplas camadas (frontend + backend)
