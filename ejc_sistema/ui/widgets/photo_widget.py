from pathlib import Path
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PIL import Image
from utils.file_utils import copy_image_validated


class PhotoWidget(QWidget):
    def __init__(self, photos_dir: Path, parent=None):
        super().__init__(parent)
        self.photos_dir = photos_dir
        self.photo_path: str | None = None
        layout = QHBoxLayout(self)
        self.button = QPushButton("Adicionar Foto")
        self.preview = QLabel(); self.preview.setFixedSize(100, 100)
        self.preview.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 8px;")
        layout.addWidget(self.button); layout.addWidget(self.preview); layout.addStretch()
        self.button.clicked.connect(self._on_add_photo)

    def _on_add_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", "", "Imagens (*.png *.jpg *.jpeg)")
        if not file_name:
            return
        try:
            with Image.open(file_name) as img:
                img.verify()
            target_path = copy_image_validated(file_name, self.photos_dir)
            self.photo_path = str(target_path)
            pixmap = QPixmap(file_name)
            self.preview.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            QMessageBox.information(self, "Sucesso", "Foto adicionada com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar a imagem: {e}")

    def get_photo_path(self) -> str:
        return self.photo_path or ""

    def set_photo_path(self, path: str | None) -> None:
        self.photo_path = path or None
        if self.photo_path and Path(self.photo_path).exists():
            pixmap = QPixmap(self.photo_path)
            self.preview.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.preview.clear()
            self.preview.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 8px;")

