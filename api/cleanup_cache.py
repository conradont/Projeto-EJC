"""Script para limpar arquivos __pycache__ existentes"""
import os
import shutil
from pathlib import Path

def cleanup_pycache():
    """Remove todos os diretórios __pycache__ e move para trash"""
    api_dir = Path(__file__).parent
    trash_dir = api_dir / "trash"
    trash_dir.mkdir(exist_ok=True)
    
    removed_count = 0
    
    # Procurar todos os __pycache__ recursivamente
    for pycache_dir in api_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            try:
                # Criar estrutura de diretórios equivalente em trash
                relative_path = pycache_dir.relative_to(api_dir)
                target_dir = trash_dir / relative_path
                target_dir.parent.mkdir(parents=True, exist_ok=True)
                
                # Mover o diretório para trash
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.move(str(pycache_dir), str(target_dir))
                removed_count += 1
                print(f"✓ Movido: {relative_path} -> trash/{relative_path}")
            except Exception as e:
                print(f"✗ Erro ao mover {pycache_dir}: {e}")
    
    # Também procurar arquivos .pyc, .pyo, .pyd soltos
    for pyc_file in api_dir.rglob("*.pyc"):
        if pyc_file.is_file():
            try:
                relative_path = pyc_file.relative_to(api_dir)
                target_file = trash_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(pyc_file), str(target_file))
                print(f"✓ Movido: {relative_path} -> trash/{relative_path}")
            except Exception as e:
                print(f"✗ Erro ao mover {pyc_file}: {e}")
    
    print(f"\n✓ Limpeza concluída! {removed_count} diretórios __pycache__ movidos para trash/")

if __name__ == "__main__":
    cleanup_pycache()
