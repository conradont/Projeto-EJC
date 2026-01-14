"""Configurações da API"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os


class Settings(BaseSettings):
    # API
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Detectar ambiente
    IS_VERCEL: bool = os.getenv("VERCEL") == "1"
    IS_PRODUCTION: bool = os.getenv("ENVIRONMENT") == "production" or IS_VERCEL
    
    # CORS - Adicionar domínios dinamicamente
    _default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Adicionar domínio do Vercel se estiver configurado
    _vercel_url = os.getenv("VERCEL_URL")
    if _vercel_url:
        _default_origins.append(f"https://{_vercel_url}")
    
    # Permitir adicionar origens via variável de ambiente
    _custom_origins = os.getenv("CORS_ORIGINS", "")
    if _custom_origins:
        _default_origins.extend([origin.strip() for origin in _custom_origins.split(",")])
    
    CORS_ORIGINS: List[str] = _default_origins
    
    # Database
    # Neon PostgreSQL: usar DATABASE_URL do ambiente (Vercel ou .env)
    # Local: SQLite como fallback se DATABASE_URL não estiver configurado
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ejc_registration.db")
    
    # Detectar tipo de banco
    IS_POSTGRES: bool = "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL
    IS_SQLITE: bool = "sqlite" in DATABASE_URL
    
    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent
    
    # Usar armazenamento local quando não estiver no Vercel
    # No Vercel, usar /tmp (temporário) ou manter local se possível
    if IS_VERCEL:
        # No Vercel, tentar usar /tmp (mas será temporário)
        # Para persistência, você precisaria de um serviço externo
        DATA_DIR: Path = Path("/tmp/data")
    else:
        # Local: usar diretório do projeto
        DATA_DIR: Path = BASE_DIR / "data"
    
    PHOTOS_DIR: Path = DATA_DIR / "photos"
    PDFS_DIR: Path = DATA_DIR / "pdfs"
    BACKUPS_DIR: Path = DATA_DIR / "backups"
    LOGO_DIR: Path = DATA_DIR / "logo"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Criar diretórios necessários
# No Vercel, isso criará em /tmp (temporário)
# Localmente, criará na pasta do projeto
try:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    settings.PDFS_DIR.mkdir(parents=True, exist_ok=True)
    settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGO_DIR.mkdir(parents=True, exist_ok=True)
    if not settings.IS_VERCEL:
        print(f"✓ Armazenamento local configurado em: {settings.DATA_DIR}")
    else:
        print(f"⚠ Vercel detectado - usando /tmp (temporário)")
except Exception as e:
    print(f"⚠ Aviso ao criar diretórios: {e}")
