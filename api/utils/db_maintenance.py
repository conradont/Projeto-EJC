"""Utilitários para manutenção do banco de dados"""
import shutil
from pathlib import Path
from datetime import datetime
from config import settings
from database.database import optimize_database, engine
from sqlalchemy import text


def backup_database():
    """Cria um backup do banco de dados SQLite"""
    if "sqlite" not in settings.DATABASE_URL:
        print("⚠ Backup automático disponível apenas para SQLite")
        return None
    
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    if not db_path.exists():
        print("⚠ Arquivo de banco de dados não encontrado")
        return None
    
    # Criar diretório de backups se não existir
    settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"ejc_registration_backup_{timestamp}.db"
    backup_path = settings.BACKUPS_DIR / backup_filename
    
    try:
        # Copiar arquivo do banco de dados
        shutil.copy2(db_path, backup_path)
        
        # Copiar também o arquivo WAL se existir
        wal_path = Path(str(db_path) + "-wal")
        if wal_path.exists():
            shutil.copy2(wal_path, Path(str(backup_path) + "-wal"))
        
        # Copiar arquivo SHM se existir
        shm_path = Path(str(db_path) + "-shm")
        if shm_path.exists():
            shutil.copy2(shm_path, Path(str(backup_path) + "-shm"))
        
        print(f"✓ Backup criado: {backup_path}")
        return str(backup_path)
    except Exception as e:
        print(f"✗ Erro ao criar backup: {e}")
        return None


def get_database_info():
    """Retorna informações sobre o banco de dados"""
    if "sqlite" not in settings.DATABASE_URL:
        return {"type": "Não SQLite", "info": "Informações disponíveis apenas para SQLite"}
    
    db_path = Path(settings.DATABASE_URL.replace("sqlite:///", ""))
    
    info = {
        "type": "SQLite",
        "path": str(db_path),
        "exists": db_path.exists(),
    }
    
    if db_path.exists():
        info["size"] = db_path.stat().st_size
        info["size_mb"] = round(info["size"] / (1024 * 1024), 2)
        info["modified"] = datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
        
        # Contar registros
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM participants"))
                info["participants_count"] = result.scalar()
        except Exception as e:
            info["participants_count"] = f"Erro: {e}"
    
    return info


def cleanup_old_backups(days_to_keep=30):
    """Remove backups mais antigos que o número de dias especificado"""
    if not settings.BACKUPS_DIR.exists():
        return
    
    cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
    removed_count = 0
    
    for backup_file in settings.BACKUPS_DIR.glob("*.db"):
        if backup_file.stat().st_mtime < cutoff_date:
            try:
                backup_file.unlink()
                # Remover arquivos relacionados (WAL, SHM)
                for ext in ["-wal", "-shm"]:
                    related_file = Path(str(backup_file) + ext)
                    if related_file.exists():
                        related_file.unlink()
                removed_count += 1
            except Exception as e:
                print(f"⚠ Erro ao remover backup antigo {backup_file}: {e}")
    
    if removed_count > 0:
        print(f"✓ {removed_count} backup(s) antigo(s) removido(s)")


if __name__ == "__main__":
    # Executar manutenção quando executado diretamente
    print("=== Manutenção do Banco de Dados ===")
    print("\n1. Informações do banco:")
    info = get_database_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n2. Criando backup...")
    backup_path = backup_database()
    
    print("\n3. Otimizando banco de dados...")
    optimize_database()
    
    print("\n4. Limpando backups antigos...")
    cleanup_old_backups()
    
    print("\n✓ Manutenção concluída!")
