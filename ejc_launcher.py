"""
Ponto de entrada para o .exe (PyInstaller).
Configura paths e diretório de trabalho, depois inicia a API e abre o navegador.
"""
import os
import sys
from pathlib import Path


def _setup_paths():
    """Configura sys.path e cwd para desenvolvimento ou .exe."""
    if getattr(sys, "frozen", False):
        meipass = Path(sys._MEIPASS)
        api_dir = meipass / "api"
        sys.path.insert(0, str(api_dir))
        os.chdir(Path(sys.executable).parent)
    else:
        root = Path(__file__).resolve().parent
        sys.path.insert(0, str(root / "api"))
        os.chdir(root)


def _open_browser():
    """Abre o navegador após 2 segundos (em thread separada)."""
    import threading
    import webbrowser
    import time

    def _run():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def main():
    _setup_paths()
    _open_browser()
    import uvicorn
    # Importar main faz o PyInstaller incluir a API e dependências
    import main  # noqa: F401
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
