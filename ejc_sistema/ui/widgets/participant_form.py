from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit
from ui.widgets.date_line_edit import DateLineEdit


class ParticipantForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._rows = 0
        self._add_field("Nome Completo:", "name")
        self._add_field("Nome Usual:", "common_name")
        self._add_label("Data de Nascimento:")
        self.birth_date = DateLineEdit(); self._layout.addWidget(self.birth_date, self._rows, 1); self._rows += 1
        self._add_field("Instagram:", "instagram")
        self._add_field("Endereço:", "address")
        self._add_field("Bairro / Comunidade:", "neighborhood")
        self._add_field("Email:", "email")
        self._add_field("Celular:", "phone")

    def _add_label(self, text: str) -> None:
        self._layout.addWidget(QLabel(text), self._rows, 0)

    def _add_field(self, label: str, attr: str) -> None:
        self._add_label(label)
        editor = QLineEdit(); setattr(self, attr, editor)
        self._layout.addWidget(editor, self._rows, 1)
        self._rows += 1

    def get_data(self) -> dict:
        return {
            "name": self.name.text(),
            "common_name": self.common_name.text(),
            "birth_date": self.birth_date.get_iso_date(),
            "instagram": self.instagram.text(),
            "address": self.address.text(),
            "neighborhood": self.neighborhood.text(),
            "email": self.email.text(),
            "phone": self.phone.text(),
        }

    def set_data(self, data: dict) -> None:
        self.name.setText(data.get("name", ""))
        self.common_name.setText(data.get("common_name", ""))
        self.birth_date.set_from_iso_date(data.get("birth_date", ""))
        self.instagram.setText(data.get("instagram", ""))
        self.address.setText(data.get("address", ""))
        self.neighborhood.setText(data.get("neighborhood", ""))
        self.email.setText(data.get("email", ""))
        self.phone.setText(data.get("phone", ""))

