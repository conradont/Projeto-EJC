"""Configurações e constantes do sistema EJC"""
from pathlib import Path

# Diretórios
HOME_DIR = Path.home()
EJC_DATA_DIR = HOME_DIR / 'EJC_Sistema'
PHOTOS_DIR = EJC_DATA_DIR / 'photos'

# Banco de dados
DB_NAME = 'ejc_registration.db'
DB_PATH = EJC_DATA_DIR / DB_NAME

# Configurações da interface
WINDOW_TITLE = "Sistema de Registro EJC"
WINDOW_GEOMETRY = (100, 100, 1200, 800)

# Configurações de foto
PHOTO_MAX_SIZE = 100
PHOTO_PREVIEW_SIZE = (100, 100)

# Configurações de PDF
PDF_PAGE_SIZE = 'A4'
PDF_HEADER_HEIGHT = 80

# Configurações da tabela de participantes
TABLE_COLUMNS = ["Nome", "Data de Nasc.", "Instagram", "Telefone", "Sacramentos", "Ações"]

# Sacramentos disponíveis
SACRAMENTS = ["Batismo", "Primeira Eucaristia", "Crisma"]
SACRAMENT_STATUSES = ["Concluído", "Não Concluído", "Em Processo"]

# Extensões de imagem permitidas
ALLOWED_IMAGE_EXTENSIONS = ['*.png', '*.jpg', '*.jpeg']

