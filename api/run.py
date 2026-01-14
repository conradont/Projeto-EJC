"""Script para executar a API"""
import os
import sys
from pathlib import Path

# Configurar Python para colocar __pycache__ em uma pasta trash
# Isso deve ser feito ANTES de importar qualquer outro módulo
trash_dir = Path(__file__).parent / "trash"
trash_dir.mkdir(exist_ok=True)
os.environ["PYTHONPYCACHEPREFIX"] = str(trash_dir)

import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
