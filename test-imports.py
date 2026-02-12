"""Script de teste para verificar imports quando frozen"""
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    meipass = Path(sys._MEIPASS)
    api_dir = meipass / "api"
    sys.path.insert(0, str(api_dir))
    sys.path.insert(0, str(meipass))
    print(f"_MEIPASS: {meipass}")
    print(f"api_dir: {api_dir}")
    print(f"api_dir existe: {api_dir.exists()}")
    if api_dir.exists():
        print(f"Arquivos em api_dir: {list(api_dir.glob('*.py'))[:5]}")
else:
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "api"))
    print(f"Modo desenvolvimento: {root / 'api'}")

try:
    print("\nTestando import main...")
    import main
    print("✓ main importado com sucesso")
    
    print("\nTestando import config...")
    import config
    print("✓ config importado com sucesso")
    print(f"  BASE_DIR: {config.settings.BASE_DIR}")
    
    print("\nTestando import database...")
    from database import database
    print("✓ database importado com sucesso")
    
    print("\nTodos os imports funcionaram!")
except Exception as e:
    import traceback
    print(f"\nERRO: {e}")
    traceback.print_exc()
