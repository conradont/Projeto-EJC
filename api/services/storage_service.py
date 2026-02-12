"""Serviço de armazenamento: Supabase Storage com buckets privados e URLs assinadas (temporárias)."""
from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import Optional

from config import settings

# Buckets no Supabase Storage (privados; acesso via signed URL)
BUCKET_PHOTOS = "photos"
BUCKET_LOGO = "logo"

# Tempo de validade da signed URL (1 hora)
SIGNED_URL_EXPIRES_IN = 3600

# Chave na tabela event_settings para o path da logo no bucket
LOGO_URL_KEY = "logo_url"


def _get_client():
    """Retorna o cliente Supabase (lazy import)."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        return None
    try:
        from supabase import create_client
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print(f"⚠ Supabase client: {e}")
        return None


def use_supabase_storage() -> bool:
    """Indica se o Storage do Supabase está configurado."""
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY)


def get_signed_url(bucket: str, path: str, expires_in: int = SIGNED_URL_EXPIRES_IN) -> Optional[str]:
    """
    Gera uma URL assinada (temporária) para um arquivo em um bucket privado.
    Quem tiver o link pode acessar só até expirar.
    """
    if not path or not use_supabase_storage():
        return None
    client = _get_client()
    if not client:
        return None
    try:
        storage = client.storage.from_(bucket)
        result = storage.create_signed_url(path, expires_in)
        if result is None:
            return None
        if isinstance(result, dict):
            return result.get("signedURL") or result.get("signed_url") or result.get("path")
        if hasattr(result, "signed_url"):
            url = getattr(result, "signed_url", None)
            if url:
                return url
        if hasattr(result, "signedURL"):
            url = getattr(result, "signedURL", None)
            if url:
                return url
        if hasattr(result, "path") and str(getattr(result, "path", "")).startswith("http"):
            return getattr(result, "path")
        return str(result) if result and str(result).startswith("http") else None
    except Exception as e:
        print(f"⚠ Erro ao gerar signed URL ({bucket}/{path}): {e}")
        return None


def _upload_bytes_to_storage(bucket: str, path: str, file_content: bytes, content_type: str) -> Optional[str]:
    """Envia bytes para um bucket e retorna o path (para uso com signed URL)."""
    client = _get_client()
    if not client:
        return None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(path).suffix) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        try:
            storage = client.storage.from_(bucket)
            with open(tmp_path, "rb") as f:
                storage.upload(path, f.read(), file_options={"content-type": content_type})
            return path
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        print(f"⚠ Erro ao fazer upload no Supabase ({bucket}): {e}")
        return None


def upload_photo(file_content: bytes, content_type: str, file_extension: str) -> Optional[str]:
    """
    Faz upload de uma foto para o bucket 'photos' e retorna o path no bucket.
    O frontend guarda o path; a API gera signed URL ao servir.
    """
    if not use_supabase_storage():
        return None
    filename = f"{uuid.uuid4().hex}{file_extension}"
    return _upload_bytes_to_storage(BUCKET_PHOTOS, filename, file_content, content_type)


def upload_logo(file_content: bytes, content_type: str, file_extension: str) -> Optional[str]:
    """
    Faz upload da logo para o bucket 'logo' e retorna o path no bucket.
    O path é guardado no banco; a API gera signed URL ao servir.
    """
    if not use_supabase_storage():
        return None
    client = _get_client()
    if not client:
        return None
    filename = f"logo{file_extension}"
    try:
        storage = client.storage.from_(BUCKET_LOGO)
        try:
            existing = storage.list()
            for item in (existing or []):
                name = item.get("name") if isinstance(item, dict) else getattr(item, "name", None)
                if name:
                    storage.remove([name])
        except Exception:
            pass
        return _upload_bytes_to_storage(BUCKET_LOGO, filename, file_content, content_type)
    except Exception as e:
        print(f"⚠ Erro ao fazer upload da logo no Supabase: {e}")
        return None


def delete_logo_storage() -> bool:
    """Remove a logo do bucket 'logo' no Supabase. Retorna True se removido ou bucket vazio."""
    if not use_supabase_storage():
        return False
    client = _get_client()
    if not client:
        return False
    try:
        storage = client.storage.from_(BUCKET_LOGO)
        files = storage.list()
        for item in (files or []):
            name = item.get("name")
            if name:
                storage.remove([name])
        return True
    except Exception as e:
        print(f"⚠ Erro ao remover logo do Supabase: {e}")
        return False


def get_logo_path_from_db(db) -> Optional[str]:
    """Lê o path da logo no bucket (event_settings)."""
    from models.event_setting import EventSetting
    row = db.query(EventSetting).filter(EventSetting.key == LOGO_URL_KEY).first()
    return row.value if row else None


def set_logo_path_in_db(db, path: Optional[str]) -> None:
    """Grava ou remove o path da logo na tabela event_settings."""
    from models.event_setting import EventSetting
    row = db.query(EventSetting).filter(EventSetting.key == LOGO_URL_KEY).first()
    if path:
        if row:
            row.value = path
        else:
            db.add(EventSetting(key=LOGO_URL_KEY, value=path))
    else:
        if row:
            db.delete(row)
    db.commit()
