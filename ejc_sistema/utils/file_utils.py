from pathlib import Path
import shutil
from uuid import uuid4
from PIL import Image


def ensure_directories(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def generate_unique_filename(original_path: str) -> str:
    ext = Path(original_path).suffix.lower()
    return f"{uuid4().hex}{ext}"


def copy_image_validated(source_path: str, destination_dir: Path) -> Path:
    # Validate image
    with Image.open(source_path) as img:
        img.verify()
    # Copy with unique name
    destination_dir.mkdir(parents=True, exist_ok=True)
    target = destination_dir / generate_unique_filename(source_path)
    shutil.copy2(source_path, target)
    return target

