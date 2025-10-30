"""Sistema de backup automático do banco de dados"""
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from utils.logger import log_info, log_error, log_warning


class BackupManager:
    """Gerencia backups automáticos e manuais do banco de dados"""
    
    def __init__(self, db_path: Path, backup_dir: Optional[Path] = None):
        self.db_path = db_path
        self.backup_dir = backup_dir or (db_path.parent / 'backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, prefix: str = "auto") -> Optional[Path]:
        """
        Cria um backup do banco de dados
        Retorna o caminho do backup criado ou None em caso de erro
        """
        if not self.db_path.exists():
            log_warning(f"Arquivo de banco de dados não encontrado: {self.db_path}")
            return None
        
        try:
            # Nome do arquivo de backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{prefix}_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Criar backup usando SQLite
            # Primeiro fechar todas as conexões se possível
            source_conn = sqlite3.connect(str(self.db_path))
            backup_conn = sqlite3.connect(str(backup_path))
            
            # Fazer backup
            source_conn.backup(backup_conn)
            backup_conn.close()
            source_conn.close()
            
            log_info(f"Backup criado: {backup_path}")
            
            # Limpar backups antigos (manter apenas os 10 mais recentes)
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            log_error(e, f"create_backup - Erro ao criar backup de {self.db_path}")
            return None
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """Remove backups antigos, mantendo apenas os mais recentes"""
        try:
            backup_files = list(self.backup_dir.glob("*_backup_*.db"))
            if len(backup_files) <= keep_count:
                return
            
            # Ordenar por data de modificação (mais recente primeiro)
            backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remover os mais antigos
            for old_backup in backup_files[keep_count:]:
                try:
                    old_backup.unlink()
                    log_info(f"Backup antigo removido: {old_backup}")
                except Exception as e:
                    log_error(e, f"Erro ao remover backup antigo: {old_backup}")
                    
        except Exception as e:
            log_error(e, "Erro ao limpar backups antigos")
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restaura um backup
        Retorna True se bem-sucedido, False caso contrário
        """
        if not backup_path.exists():
            log_warning(f"Arquivo de backup não encontrado: {backup_path}")
            return False
        
        try:
            # Fazer backup do banco atual antes de restaurar
            current_backup = self.create_backup(prefix="pre_restore")
            if not current_backup:
                log_warning("Não foi possível criar backup antes da restauração")
            
            # Restaurar backup
            if self.db_path.exists():
                self.db_path.unlink()  # Remove banco atual
            
            shutil.copy2(backup_path, self.db_path)
            log_info(f"Backup restaurado: {backup_path}")
            return True
            
        except Exception as e:
            log_error(e, f"Erro ao restaurar backup: {backup_path}")
            return False
    
    def get_available_backups(self) -> list[Path]:
        """Retorna lista de backups disponíveis ordenados por data (mais recente primeiro)"""
        try:
            backup_files = list(self.backup_dir.glob("*_backup_*.db"))
            backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return backup_files
        except Exception as e:
            log_error(e, "Erro ao listar backups")
            return []



