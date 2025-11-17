"""
Database models for FLUXO CASH proof management system
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class ProofStatus(str, Enum):
    """Status de extração do comprovante"""
    UPLOADED = "UPLOADED"          # Arquivo enviado, não processado
    EXTRACTING = "EXTRACTING"      # Processando extração
    EXTRACTED = "EXTRACTED"        # Valor extraído com sucesso
    FAILED = "FAILED"              # Falha na extração
    MANUAL_ENTRY = "MANUAL_ENTRY"  # Valor inserido manualmente


class Proof:
    """
    Modelo de comprovante/prova de transação
    
    Campos:
        - id: identificador único
        - client_id: cliente associado
        - filename: nome do arquivo original
        - file_path: caminho local do arquivo
        - file_type: tipo MIME (PDF, image)
        - file_size: tamanho em bytes
        - file_hash: SHA-256 do conteúdo (para dedup)
        - description: descrição opcional
        - is_duplicate: se é duplicado
        - original_proof_id: referência ao original se duplicado
        - extracted_value: valor monetário extraído (em reais)
        - extraction_confidence: confiança da extração (0-1)
        - extraction_status: status do processamento
        - beneficiary: nome do beneficiário extraído
        - endtoend: ID da transação PIX extraído
        - uploaded_at: quando foi enviado
        - created_at: quando foi criado no BD
    """
    
    def __init__(
        self,
        id: int,
        client_id: int,
        filename: str,
        file_path: str,
        file_type: str,
        file_size: int,
        file_hash: str,
        description: Optional[str] = None,
        is_duplicate: bool = False,
        original_proof_id: Optional[int] = None,
        extracted_value: Optional[float] = None,
        extraction_confidence: float = 0.0,
        extraction_status: str = ProofStatus.UPLOADED,
        beneficiary: Optional[str] = None,
        endtoend: Optional[str] = None,
        uploaded_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.client_id = client_id
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.file_hash = file_hash
        self.description = description
        self.is_duplicate = is_duplicate
        self.original_proof_id = original_proof_id
        self.extracted_value = extracted_value
        self.extraction_confidence = extraction_confidence
        self.extraction_status = extraction_status
        self.beneficiary = beneficiary
        self.endtoend = endtoend
        self.uploaded_at = uploaded_at or datetime.now()
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        """Converte modelo para dicionário"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'description': self.description,
            'is_duplicate': self.is_duplicate,
            'original_proof_id': self.original_proof_id,
            'extracted_value': self.extracted_value,
            'extraction_confidence': self.extraction_confidence,
            'extraction_status': self.extraction_status,
            'beneficiary': self.beneficiary,
            'endtoend': self.endtoend,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Client:
    """Modelo simples de cliente"""
    
    def __init__(
        self,
        id: int,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        account: Optional[str] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.account = account
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.proofs = []
    
    def to_dict(self):
        """Converte modelo para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'account': self.account,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
