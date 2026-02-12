"""
Ponto de entrada para o .exe (PyInstaller).
Configura paths e diretório de trabalho, depois inicia a API e abre o navegador.
"""
import os
import sys
import time
from pathlib import Path
from threading import Thread, Event
from typing import Optional


class LoadingIndicator:
    """Indicador de progresso visual para o CLI."""
    
    def __init__(self, message: str = "Carregando"):
        self.message = message
        self.stop_event = Event()
        self.thread = None
        self.spinner_chars = "|/-\\"
        self.current_char = 0
    
    def _animate(self):
        """Anima o spinner enquanto não for parado."""
        while not self.stop_event.is_set():
            char = self.spinner_chars[self.current_char % len(self.spinner_chars)]
            sys.stdout.write(f"\r{self.message}... {char}")
            sys.stdout.flush()
            self.current_char += 1
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()
    
    def start(self):
        """Inicia a animação."""
        self.stop_event.clear()
        self.thread = Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self, success_message: Optional[str] = None):
        """Para a animação e mostra mensagem de sucesso."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=0.5)
        if success_message:
            sys.stdout.write(f"\r✓ {success_message}\n")
            sys.stdout.flush()
        else:
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()


def print_header():
    """Imprime cabeçalho estilizado."""
    print("\n" + "=" * 60)
    print(" " * 15 + "EJC Sistema")
    print(" " * 10 + "Sistema de Gerenciamento")
    print("=" * 60 + "\n")


def print_step(step_num: int, total_steps: int, message: str):
    """Imprime uma etapa do processo."""
    print(f"[{step_num}/{total_steps}] {message}...", end=" ", flush=True)


def print_success(message: str = ""):
    """Imprime mensagem de sucesso."""
    print(f"✓ {message}" if message else "✓ Concluído")


def print_error(message: str):
    """Imprime mensagem de erro."""
    print(f"✗ {message}")


def _setup_paths():
    """Configura sys.path e cwd para desenvolvimento ou .exe."""
    loading = LoadingIndicator("Configurando ambiente")
    loading.start()
    
    try:
        if getattr(sys, "frozen", False):
            # _MEIPASS é adicionado dinamicamente pelo PyInstaller
            meipass_str = getattr(sys, "_MEIPASS", None)
            if not meipass_str:
                loading.stop()
                raise RuntimeError("_MEIPASS não encontrado - PyInstaller pode não estar configurado corretamente")
            meipass = Path(meipass_str)
            api_dir = meipass / "api"
            if not api_dir.exists():
                loading.stop()
                raise FileNotFoundError(f"Pasta api não encontrada em {meipass}")
            
            # Adicionar api_dir ao path para que 'import main' funcione
            # E também adicionar meipass para imports relativos funcionarem
            sys.path.insert(0, str(api_dir))
            sys.path.insert(0, str(meipass))
            
            exe_dir = Path(sys.executable).parent
            os.chdir(exe_dir)
            loading.stop("Ambiente configurado")
            time.sleep(0.2)  # Pequena pausa para melhor visualização
        else:
            root = Path(__file__).resolve().parent
            sys.path.insert(0, str(root / "api"))
            os.chdir(root)
            loading.stop("Ambiente configurado")
    except Exception as e:
        loading.stop()
        print_error(f"Erro ao configurar paths: {e}")
        import traceback
        traceback.print_exc()
        raise


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
        print_header()
        
        total_steps = 5
        current_step = 1
        
        # Passo 1: Configurar ambiente
        print_step(current_step, total_steps, "Configurando ambiente")
        _setup_paths()
        current_step += 1
        time.sleep(0.3)
        
        # Passo 2: Verificar frontend
        if getattr(sys, "frozen", False):
            print_step(current_step, total_steps, "Verificando frontend")
            loading = LoadingIndicator("Verificando arquivos")
            loading.start()
            time.sleep(0.5)
            
            meipass_str = getattr(sys, "_MEIPASS", None)
            if meipass_str:
                meipass = Path(meipass_str)
                dist_dir = meipass / "dist"
                if not dist_dir.exists():
                    loading.stop()
                    print_error("Pasta dist não encontrada")
                else:
                    loading.stop("Frontend encontrado")
            else:
                loading.stop("Modo desenvolvimento")
            current_step += 1
            time.sleep(0.3)
        
        # Passo 3: Carregar módulos
        print_step(current_step, total_steps, "Carregando módulos Python")
        loading = LoadingIndicator("Importando dependências")
        loading.start()
        time.sleep(0.5)
        
        import uvicorn
        # Importar main faz o PyInstaller incluir a API e dependências
        # O path é configurado dinamicamente em _setup_paths()
        # O módulo main está em api/main.py e é adicionado ao path em _setup_paths()
        import main  # type: ignore # noqa: F401
        
        loading.stop("Módulos carregados")
        current_step += 1
        time.sleep(0.3)
        
        # Passo 4: Inicializar servidor
        print_step(current_step, total_steps, "Inicializando servidor")
        loading = LoadingIndicator("Iniciando API")
        loading.start()
        time.sleep(0.8)
        loading.stop("Servidor pronto")
        current_step += 1
        time.sleep(0.3)
        
        # Passo 5: Abrir navegador
        print_step(current_step, total_steps, "Abrindo navegador")
        _open_browser()
        print_success("Navegador será aberto em breve")
        time.sleep(0.3)
        
        print("\n" + "=" * 60)
        print(" " * 10 + "Servidor rodando em http://localhost:8000")
        print(" " * 15 + "Pressione Ctrl+C para encerrar")
        print("=" * 60 + "\n")
        
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
            # _MEIPASS é adicionado dinamicamente pelo PyInstaller
            meipass_debug = getattr(sys, "_MEIPASS", "N/A")
            print(f"  _MEIPASS: {meipass_debug}")
            print(f"  Executável: {sys.executable}")
        print(f"  CWD: {os.getcwd()}")
        print(f"  sys.path: {sys.path[:3]}...")
        print("=" * 60)
        input("\nPressione Enter para fechar...")
        sys.exit(1)


if __name__ == "__main__":
    main()
