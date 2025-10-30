"""Sistema de logging para o EJC"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import config

# Criar diretório de logs se não existir
LOG_DIR = config.EJC_DATA_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configurar logging
LOG_FILE = LOG_DIR / f'ejc_system_{datetime.now().strftime("%Y%m%d")}.log'

# Criar logger
logger = logging.getLogger('EJC_System')
logger.setLevel(logging.DEBUG)

# Evitar handlers duplicados
if not logger.handlers:
    # Handler para arquivo
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato das mensagens
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_error(error: Exception, context: str = ""):
    """Registra um erro com contexto"""
    message = f"{context}: {type(error).__name__}: {str(error)}"
    logger.error(message, exc_info=True)
    return message


def log_warning(message: str):
    """Registra um aviso"""
    logger.warning(message)


def log_info(message: str):
    """Registra uma informação"""
    logger.info(message)


def log_debug(message: str):
    """Registra uma mensagem de debug"""
    logger.debug(message)



