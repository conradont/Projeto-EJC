# Entrypoint para a Vercel: expõe o app FastAPI (API + static frontend na Vercel)
# Inclui api/ no path para que main.py encontre config, database, etc.
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_api = _root / "api"
if str(_api) not in sys.path:
    sys.path.insert(0, str(_api))

# Import main após adicionar api ao path
from main import app  # type: ignore # noqa: E402

__all__ = ["app"]
