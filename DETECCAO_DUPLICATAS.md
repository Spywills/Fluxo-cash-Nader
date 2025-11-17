# 🔒 Detecção de Duplicatas - Como Funciona

## ❓ Pergunta Comum

**"Se eu mudar o nome do comprovante, o sistema vai ler como novo ou vai detectar duplicata?"**

---

## ✅ Resposta: O Sistema Detecta pelo CONTEÚDO!

O sistema usa **hash SHA-256 do conteúdo do arquivo**, não o nome. Isso significa:

- ✅ **Renomear o arquivo** → Ainda detecta como duplicado
- ✅ **Mudar a extensão** → Ainda detecta como duplicado
- ✅ **Copiar e colar** → Ainda detecta como duplicado
- ✅ **Baixar novamente** → Ainda detecta como duplicado

**Só NÃO detecta se:**
- ❌ Editar o conteúdo do arquivo (adicionar/remover pixels, texto, etc.)
- ❌ Converter formato (PDF → PNG, por exemplo)
- ❌ Comprimir/descomprimir com perda de qualidade

---

## 🧪 Exemplo Prático

### Cenário 1: Renomear Arquivo
```
Upload 1:
📄 Nome: "comprovante_joao_silva.pdf"
🔐 Hash: "a1b2c3d4e5f6..."
✅ Status: Aceito

Upload 2 (mesmo arquivo, nome diferente):
📄 Nome: "pagamento_123.pdf"
🔐 Hash: "a1b2c3d4e5f6..."  ← MESMO HASH!
❌ Status: DUPLICADO DETECTADO
```

### Cenário 2: Arquivo Diferente
```
Upload 1:
📄 Nome: "comprovante1.pdf"
🔐 Hash: "a1b2c3d4e5f6..."
✅ Status: Aceito

Upload 2 (arquivo diferente):
📄 Nome: "comprovante1.pdf"  ← MESMO NOME!
🔐 Hash: "x9y8z7w6v5u4..."  ← HASH DIFERENTE
✅ Status: Aceito (não é duplicado)
```

---

## 💻 Como o Sistema Faz Isso

### 1️⃣ Geração do Hash

```python
# Quando você faz upload, o sistema:

# 1. Lê o conteúdo COMPLETO do arquivo
contents = await file.read()

# 2. Gera hash SHA-256 do conteúdo (não do nome!)
file_hash = hashlib.sha256(contents).hexdigest()
# Resultado: "a1b2c3d4e5f6789..." (64 caracteres)
```

### 2️⃣ Verificação de Duplicata

```python
def check_duplicate(file_hash: str, client_id: int) -> bool:
    """Verifica se arquivo duplicado já existe para este cliente"""
    for proof in proofs_db.values():
        # Compara HASH + CLIENTE
        if proof['client_id'] == client_id and proof['file_hash'] == file_hash:
            return True  # ❌ DUPLICADO!
    return False  # ✅ NOVO
```

### 3️⃣ Armazenamento

```python
# Se não for duplicado, salva com o hash
new_proof = {
    "id": 1,
    "client_id": 5,
    "filename": "qualquer_nome.pdf",  ← Nome pode ser qualquer um
    "file_hash": "a1b2c3d4e5f6...",   ← Hash é único para o conteúdo
    "is_duplicate": False
}
```

---

## 🔍 O que é Hash SHA-256?

**SHA-256** é uma função criptográfica que:
- Transforma qualquer arquivo em uma "impressão digital" única de 64 caracteres
- Mesmo arquivo = sempre o mesmo hash
- Mudar 1 byte = hash completamente diferente

### Exemplo Visual

```
Arquivo Original:
┌─────────────────────────┐
│ Conteúdo: "Valor R$ 100"│
│ Hash: abc123def456...   │
└─────────────────────────┘

Renomear (mesmo conteúdo):
┌─────────────────────────┐
│ Conteúdo: "Valor R$ 100"│
│ Hash: abc123def456...   │ ← MESMO HASH!
└─────────────────────────┘

Editar (conteúdo diferente):
┌─────────────────────────┐
│ Conteúdo: "Valor R$ 101"│ ← Mudou 1 caractere
│ Hash: xyz789uvw012...   │ ← HASH TOTALMENTE DIFERENTE!
└─────────────────────────┘
```

---

## 🎯 Validação por Cliente

**Importante:** A duplicata é verificada **por cliente**!

```
Cliente A:
- Upload: comprovante.pdf (hash: abc123)
- Status: ✅ Aceito

Cliente B:
- Upload: comprovante.pdf (mesmo hash: abc123)
- Status: ✅ Aceito (cliente diferente!)

Cliente A (novamente):
- Upload: pagamento.pdf (mesmo hash: abc123)
- Status: ❌ DUPLICADO (mesmo cliente + mesmo hash)
```

**Por quê?**
- Clientes diferentes podem ter comprovantes iguais (ex: mesmo banco)
- Mas o mesmo cliente não deve enviar o mesmo comprovante duas vezes

---

## 🛡️ Proteção Contra Fraudes

Esta abordagem protege contra:

1. **Renomear arquivo** para tentar enviar novamente
2. **Copiar e colar** o mesmo arquivo
3. **Baixar novamente** do banco e reenviar
4. **Mudar extensão** (.pdf → .png)

**Não protege contra:**
- Editar o conteúdo do arquivo (mas aí seria outro comprovante)
- Tirar screenshot do comprovante (seria uma imagem diferente)
- Converter formato com perda (PDF → imagem comprimida)

---

## 📊 Fluxo de Validação

```
UPLOAD
  ↓
Ler conteúdo do arquivo
  ↓
Gerar hash SHA-256
  ↓
Buscar no banco: mesmo hash + mesmo cliente?
  ↓
┌─────────────┬─────────────┐
│   SIM       │    NÃO      │
│ (duplicado) │  (novo)     │
└─────────────┴─────────────┘
      ↓              ↓
  ❌ REJEITAR    ✅ ACEITAR
      ↓              ↓
  Retorna erro   Salva arquivo
  "Duplicado"    + hash
```

---

## 🔧 Código Completo

### Backend (main.py)

```python
@app.post("/proofs/clients/{client_id}/upload")
async def upload_proof(client_id: int, file: UploadFile = File(...)):
    # 1. Ler conteúdo
    contents = await file.read()
    
    # 2. Gerar hash do CONTEÚDO (não do nome!)
    file_hash = hashlib.sha256(contents).hexdigest()
    
    # 3. Verificar duplicata
    is_duplicate = check_duplicate(file_hash, client_id)
    
    if is_duplicate:
        return {
            "success": False,
            "is_duplicate": True,
            "message": "Arquivo duplicado detectado"
        }
    
    # 4. Salvar com hash
    new_proof = {
        "file_hash": file_hash,  # ← Chave única
        "filename": file.filename,  # ← Apenas para exibição
        # ...
    }
```

### Função de Verificação

```python
def check_duplicate(file_hash: str, client_id: int) -> bool:
    """Verifica se arquivo duplicado já existe para este cliente"""
    for proof in proofs_db.values():
        if proof['client_id'] == client_id and proof['file_hash'] == file_hash:
            return True
    return False
```

---

## ✅ Conclusão

**Resposta Direta:**
- ❌ **Renomear o arquivo NÃO engana o sistema**
- ✅ **O sistema detecta pelo conteúdo, não pelo nome**
- 🔒 **Hash SHA-256 garante detecção precisa**
- 👥 **Validação é por cliente (mesmo arquivo pode ser usado por clientes diferentes)**

**Segurança:**
- Impossível enviar o mesmo comprovante duas vezes para o mesmo cliente
- Mesmo renomeando, copiando, ou mudando extensão
- Proteção robusta contra duplicação acidental ou intencional

---

## 🎓 Resumo Técnico

| Ação | Nome do Arquivo | Hash | Resultado |
|------|----------------|------|-----------|
| Upload original | `comprovante.pdf` | `abc123...` | ✅ Aceito |
| Renomear e reenviar | `pagamento.pdf` | `abc123...` | ❌ Duplicado |
| Editar e reenviar | `comprovante.pdf` | `xyz789...` | ✅ Aceito (conteúdo diferente) |
| Outro cliente | `comprovante.pdf` | `abc123...` | ✅ Aceito (cliente diferente) |

**Chave da Detecção:** `file_hash + client_id`
