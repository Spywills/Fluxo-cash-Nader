"""
Módulo de extração de valores de comprovantes (baseado em Sistema Nader V2)
Suporta PDFs, JPGs e PNGs
"""

import re
import pytesseract
from PIL import Image
from pathlib import Path
import logging
from typing import Tuple, Optional, Dict
from datetime import datetime

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import pdfplumber
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

logger = logging.getLogger(__name__)

# Regex para extrair valores monetários (baseado em Nader V2)
AMOUNT_RE = re.compile(r"""
(?:
    # Formato "Valor R$ 143.800,00"
    (?:valor|value|amount|total|quantia)\s*
    (?:R\$|BRL|USD|US\$)?\s*
    (\d{1,3}(?:\.\d{3})*,\d{2})
)|
(?:
    # Formato "R$ 143.800,00" isolado
    (?:R\$|BRL)\s*
    (\d{1,3}(?:\.\d{3})*,\d{2})
)|
(?:
    # Formato americano $1,234.56
    (?:US\$|\$)\s*
    (\d{1,3}(?:,\d{3})*\.\d{2})
)|
(?:
    # Números com vírgula decimal (formato brasileiro)
    \b(\d{1,3}(?:\.\d{3})*,\d{2})\b
)
""", re.IGNORECASE | re.VERBOSE)

# Regex para datas
DATE_RE = re.compile(r'''
(?:
    # Formato "03 NOV 2025" ou "03/11/2025"
    (\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})
)|
(?:
    # Formato YYYY-MM-DD
    (\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})
)
''', re.IGNORECASE | re.VERBOSE)

# Regex para nomes de beneficiários
BENEFICIARY_RE = re.compile(r'''
(?:
    # Formato: "Favorecido Nome: NOME"
    Favorecido\s+Nome\s*[:\-]?\s*
    ([A-Z][A-Za-z0-9\.\s\-&]+?)(?=\s+(?:CPF|CNPJ|Institui|Chave|Conta|Data))
)|
(?:
    # Formato: "BeneficiÃ¡rio: NOME"
    (?:BeneficiÃ¡rio|Beneficiario|Para)\s*[:\-]?\s*
    ([A-Z][A-Za-z0-9\.\s\-&]{2,80})
)
''', re.IGNORECASE | re.VERBOSE | re.MULTILINE)

# Regex para EndToEnd (ID da transação PIX)
ENDTOEND_RE = re.compile(r'''
(?:
    # Formato PIX: E + números + letras/números
    \b(E\d{11,20}[a-zA-Z0-9]{10,20})\b
)|
(?:
    # ID da transação explícito
    (?:id\s*(?:da\s*)?transa[çc][ãa]o|end\s*to\s*end|endtoend|e2e)
    \s*[:\-]?\s*
    ([A-Za-z0-9]{15,50})
)
''', re.IGNORECASE | re.VERBOSE)


def parse_amount(text: str) -> Optional[float]:
    """
    Extrai valor monetário do texto do comprovante
    Retorna: float (valor em reais) ou None
    """
    if not text:
        return None
    
    matches = AMOUNT_RE.findall(text)
    if not matches:
        return None
    
    values = []
    for match_groups in matches:
        # match_groups é uma tupla, pega o primeiro grupo não vazio
        raw = next((g for g in match_groups if g), None)
        if not raw:
            continue
        
        clean = raw.strip()
        
        # Se tem vírgula como decimal (formato brasileiro)
        if ',' in clean and '.' in clean:
            # Formato: 143.800,00 -> remove pontos e troca vírgula por ponto
            clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            # Formato: 1800,00 -> troca vírgula por ponto
            clean = clean.replace(',', '.')
        
        try:
            v = float(clean)
            # Validar intervalo (0 a 10 milhões)
            if 0 < v < 10_000_000:
                values.append(v)
        except ValueError:
            continue
    
    return max(values) if values else None


def parse_date(text: str) -> Optional[str]:
    """
    Extrai data do texto do comprovante
    Retorna: string no formato ISO (YYYY-MM-DD) ou None
    """
    if not text:
        return None
    
    matches = DATE_RE.findall(text)
    if not matches:
        return None
    
    for match_groups in matches:
        date_str = next((g for g in match_groups if g), None)
        if not date_str:
            continue
        
        try:
            # Tentar diferentes formatos
            from dateutil import parser as dateparser
            parsed_date = dateparser.parse(date_str, dayfirst=True)
            if parsed_date:
                return parsed_date.date().isoformat()
        except Exception as e:
            logger.warning(f"Erro ao parsear data '{date_str}': {e}")
            continue
    
    return None


def parse_beneficiary(text: str) -> Optional[str]:
    """
    Extrai nome do beneficiário do texto
    Retorna: string com nome ou None
    """
    if not text:
        return None
    
    def clean_name(name: str) -> Optional[str]:
        if not name:
            return None
        # Remover quebras de linha e múltiplos espaços
        cleaned = re.sub(r'\s+', ' ', name).strip()
        
        # Remover rótulos no final
        labels_to_remove = ['CNPJ', 'CPF', 'Valor', 'R$', 'Data', 'Conta', 'Agência']
        for label in labels_to_remove:
            pattern = r'\s+' + re.escape(label) + r'\s*$'
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned if cleaned else None
    
    # Tentar padrões específicos
    match = BENEFICIARY_RE.search(text)
    if match:
        for group in match.groups():
            cleaned = clean_name(group)
            if cleaned and len(cleaned) > 3:
                return cleaned
    
    return None


def parse_endtoend(text: str) -> Optional[str]:
    """
    Extrai EndToEnd (ID da transação PIX) do texto
    Retorna: string com EndToEnd ou None
    """
    if not text:
        return None
    
    matches = ENDTOEND_RE.findall(text)
    if not matches:
        return None
    
    candidates = []
    for match_groups in matches:
        for group in match_groups:
            if group and len(group.strip()) >= 15:
                candidates.append(group.strip())
    
    if not candidates:
        return None
    
    # Priorizar EndToEnd que começam com 'E'
    pix_candidates = [c for c in candidates if c.upper().startswith('E')]
    return pix_candidates[0].upper() if pix_candidates else candidates[0].upper()


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Pré-processa imagem para melhorar OCR
    Baseado em Nader V2
    """
    if not OPENCV_AVAILABLE:
        return image
    
    try:
        # Converter PIL para OpenCV
        img_array = np.array(image)
        
        # Converter para escala de cinza
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Redimensionar se muito pequena
        height, width = gray.shape
        if height < 1000 or width < 1000:
            scale_factor = max(1000 / height, 1000 / width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Aplicar denoising
        gray = cv2.fastNlMeansDenoising(gray)
        
        # Melhorar contraste
        gray = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
        
        # Aplicar threshold adaptativo
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Converter de volta para PIL
        return Image.fromarray(binary)
    
    except Exception as e:
        logger.warning(f"Erro ao pré-processar imagem: {e}")
        return image


def extract_text_from_image(image_path: str) -> Tuple[str, float]:
    """
    Extrai texto de imagem (JPG/PNG) usando Tesseract OCR
    Retorna: (texto extraído, confiança 0-1)
    """
    try:
        image = Image.open(image_path)
        
        # Pré-processar
        processed = preprocess_image(image)
        
        # OCR
        text = pytesseract.image_to_string(processed, lang='por')
        
        # Confidence estimation (simplificado)
        # Texto maior geralmente = mais confiança
        confidence = min(1.0, len(text) / 1000.0)
        
        return text, confidence
    
    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem {image_path}: {e}")
        return "", 0.0


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, float]:
    """
    Extrai texto de PDF usando pdfplumber ou OCR das páginas
    Retorna: (texto extraído, confiança 0-1)
    """
    if not PDF_SUPPORT:
        logger.error("PDF support não disponível. Instale: pip install pdfplumber pdf2image")
        return "", 0.0
    
    try:
        all_text = ""
        confidence = 0.0
        page_count = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Tentar extrair texto nativo primeiro
                page_text = page.extract_text() or ""
                
                if page_text.strip():
                    all_text += page_text + "\n"
                    # Texto nativo = alta confiança
                    confidence += 0.95
                else:
                    # Fallback para OCR
                    try:
                        # Converter página para imagem
                        images = convert_from_path(pdf_path, first_page=page.page_number, last_page=page.page_number, dpi=300)
                        if images:
                            img_text, img_conf = extract_text_from_image_object(images[0])
                            all_text += img_text + "\n"
                            confidence += img_conf
                    except Exception as e:
                        logger.warning(f"Erro ao fazer OCR na página {page.page_number}: {e}")
                
                page_count += 1
        
        if page_count > 0:
            confidence = min(1.0, confidence / page_count)
        
        return all_text, confidence
    
    except Exception as e:
        logger.error(f"Erro ao extrair texto de PDF {pdf_path}: {e}")
        return "", 0.0


def extract_text_from_image_object(image: Image.Image) -> Tuple[str, float]:
    """
    Extrai texto de objeto PIL Image usando OCR
    Retorna: (texto extraído, confiança 0-1)
    """
    try:
        # Pré-processar
        processed = preprocess_image(image)
        
        # OCR
        text = pytesseract.image_to_string(processed, lang='por')
        confidence = min(1.0, len(text) / 1000.0)
        
        return text, confidence
    
    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem: {e}")
        return "", 0.0


def extract_proof_data(file_path: str) -> Dict:
    """
    Extrai todos os dados de um comprovante
    
    Retorna:
    {
        'value': float (valor em reais),
        'date': str (ISO format),
        'beneficiary': str,
        'endtoend': str,
        'raw_text': str,
        'confidence': float (0-1),
        'success': bool
    }
    """
    try:
        file_path = str(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Extrair texto baseado no tipo de arquivo
        if file_ext == '.pdf':
            raw_text, confidence = extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            raw_text, confidence = extract_text_from_image(file_path)
        else:
            return {
                'value': None,
                'date': None,
                'beneficiary': None,
                'endtoend': None,
                'raw_text': '',
                'confidence': 0.0,
                'success': False,
                'error': f'Tipo de arquivo não suportado: {file_ext}'
            }
        
        if not raw_text.strip():
            return {
                'value': None,
                'date': None,
                'beneficiary': None,
                'endtoend': None,
                'raw_text': '',
                'confidence': 0.0,
                'success': False,
                'error': 'Não foi possível extrair texto do arquivo'
            }
        
        # Extrair dados específicos
        value = parse_amount(raw_text)
        date = parse_date(raw_text)
        beneficiary = parse_beneficiary(raw_text)
        endtoend = parse_endtoend(raw_text)
        
        # Determinar sucesso (deve ter pelo menos valor)
        success = value is not None
        
        return {
            'value': value,
            'date': date,
            'beneficiary': beneficiary,
            'endtoend': endtoend,
            'raw_text': raw_text[:500] if raw_text else '',  # Primeiros 500 chars
            'confidence': confidence,
            'success': success,
            'error': None if success else 'Não foi possível extrair valor do comprovante'
        }
    
    except Exception as e:
        logger.error(f"Erro ao extrair dados do comprovante {file_path}: {e}")
        return {
            'value': None,
            'date': None,
            'beneficiary': None,
            'endtoend': None,
            'raw_text': '',
            'confidence': 0.0,
            'success': False,
            'error': str(e)
        }
