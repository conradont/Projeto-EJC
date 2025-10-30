import re
from datetime import datetime
from typing import Optional, Tuple

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_REGEX = re.compile(r"^[0-9\s()+-]{10,20}$")
INSTAGRAM_REGEX = re.compile(r"^@?[a-zA-Z0-9._]+$")


def is_valid_email(email: str) -> bool:
    """Valida formato de email"""
    if not email:
        return True
    return bool(EMAIL_REGEX.match(email.strip()))


def is_valid_phone(phone: str) -> bool:
    """Valida formato de telefone (10-20 dígitos com caracteres permitidos)"""
    if not phone:
        return True
    # Remove espaços e caracteres permitidos para contar apenas dígitos
    digits_only = re.sub(r'[^\d]', '', phone)
    return len(digits_only) >= 10 and bool(PHONE_REGEX.match(phone.strip()))


def is_valid_instagram(instagram: str) -> bool:
    """Valida formato de Instagram (opcionalmente com @ no início)"""
    if not instagram:
        return True
    instagram = instagram.strip()
    if instagram.startswith('@'):
        instagram = instagram[1:]
    return bool(INSTAGRAM_REGEX.match(instagram)) and len(instagram) >= 1


def is_valid_date(date_str: str) -> bool:
    """Valida formato de data ISO (YYYY-MM-DD)"""
    if not date_str:
        return True
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def validate_participant_data(data: dict) -> Tuple[bool, Optional[str]]:
    """
    Valida todos os dados de um participante
    Retorna (is_valid, error_message)
    """
    # Nome obrigatório
    if not data.get('name') or not data['name'].strip():
        return False, "O campo 'Nome Completo' é obrigatório."
    
    # Validação de email
    email = data.get('email', '').strip()
    if email and not is_valid_email(email):
        return False, "O email informado não é válido. Por favor, verifique o formato."
    
    # Validação de telefone
    phone = data.get('phone', '').strip()
    if phone and not is_valid_phone(phone):
        return False, "O telefone informado não é válido. Use apenas números e caracteres como +, -, ( e )."
    
    # Validação de telefone do pai
    father_contact = data.get('father_contact', '').strip()
    if father_contact and not is_valid_phone(father_contact):
        return False, "O contato do pai não é válido. Use apenas números e caracteres como +, -, ( e )."
    
    # Validação de telefone da mãe
    mother_contact = data.get('mother_contact', '').strip()
    if mother_contact and not is_valid_phone(mother_contact):
        return False, "O contato da mãe não é válido. Use apenas números e caracteres como +, -, ( e )."
    
    # Validação de Instagram
    instagram = data.get('instagram', '').strip()
    if instagram and not is_valid_instagram(instagram):
        return False, "O Instagram informado não é válido. Use apenas letras, números, pontos e underlines."
    
    # Validação de data de nascimento
    birth_date = data.get('birth_date', '').strip()
    if birth_date and not is_valid_date(birth_date):
        return False, "A data de nascimento não é válida. Use o formato DD/MM/AAAA."
    
    return True, None

