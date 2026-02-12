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
        try:
            meipass = Path(sys._MEIPASS)
            api_dir = meipass / "api"
            if not api_dir.exists():
                raise FileNotFoundError(f"Pasta api não encontrada em {meipass}")
            
            # Adicionar api_dir ao path para que 'import main' funcione
            # E também adicionar meipass para imports relativos funcionarem
            sys.path.insert(0, str(api_dir))
            sys.path.insert(0, str(meipass))
            
            exe_dir = Path(sys.executable).parent
            os.chdir(exe_dir)
            print(f"✓ Executável: {sys.executable}")
            print(f"✓ Diretório de trabalho: {exe_dir}")
            print(f"✓ API em: {api_dir}")
            print(f"✓ _MEIPASS: {meipass}")
        except Exception as e:
            print(f"ERRO ao configurar paths: {e}")
            import traceback
            traceback.print_exc()
            raise
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
    try:
        print("Iniciando EJC Sistema...")
        _setup_paths()
        
        # Verificar se dist existe quando frozen
        if getattr(sys, "frozen", False):
            meipass = Path(sys._MEIPASS)
            dist_dir = meipass / "dist"
            if not dist_dir.exists():
                print(f"AVISO: Pasta dist não encontrada em {dist_dir}")
            else:
                print(f"✓ Frontend encontrado em: {dist_dir}")
        
        _open_browser()
        
        print("Carregando módulos...")
        import uvicorn
        # Importar main faz o PyInstaller incluir a API e dependências
        print("Importando módulo main...")
        import main  # noqa: F401
        print("✓ Módulos carregados")
        
        print("Iniciando servidor em http://localhost:8000...")
        uvicorn.run("main:app", host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print("ERRO ao iniciar o aplicativo:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        print("\nInformações de debug:")
        print(f"  Frozen: {getattr(sys, 'frozen', False)}")
        if getattr(sys, "frozen", False):
            print(f"  _MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
            print(f"  Executável: {sys.executable}")
        print(f"  CWD: {os.getcwd()}")
        print(f"  sys.path: {sys.path[:3]}...")
        print("=" * 60)
        input("\nPressione Enter para fechar...")
        sys.exit(1)


if __name__ == "__main__":
    main()
