"""Campo de texto personalizado para entrada de data com formatação automática"""
from PyQt6.QtWidgets import QLineEdit


class DateLineEdit(QLineEdit):
    """Campo de texto personalizado para entrada de data com formatação automática"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("DD/MM/AAAA")
        self.setMaxLength(10)  # DD/MM/AAAA = 10 caracteres
        self.textChanged.connect(self.format_date)
        self._last_text = ""
        
    def format_date(self, text):
        """Formata o texto para padrão DD/MM/AAAA"""
        # Remover caracteres não numéricos
        clean_text = ''.join(filter(str.isdigit, text))
        
        # Formatar com barras
        formatted_text = ""
        for i, char in enumerate(clean_text):
            if i == 2 or i == 4:
                formatted_text += "/" + char
            else:
                formatted_text += char
        
        # Verificar se o texto mudou para evitar recursão infinita
        if formatted_text != self._last_text and formatted_text != text:
            self._last_text = formatted_text
            self.setText(formatted_text)
    
    def get_iso_date(self):
        """Retorna a data no formato ISO (YYYY-MM-DD)"""
        text = self.text()
        if len(text) < 10:  # Verificar se a data está completa
            return ""
        
        try:
            day, month, year = text.split('/')
            # Verificar se os valores são válidos
            day = int(day)
            month = int(month)
            year = int(year)
            
            if day < 1 or day > 31 or month < 1 or month > 12:
                return ""
                
            # Converter para formato ISO
            return f"{year}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            return ""
    
    def set_from_iso_date(self, iso_date):
        """Define o texto a partir de uma data no formato ISO (YYYY-MM-DD)"""
        if not iso_date:
            self.clear()
            return
            
        try:
            year, month, day = iso_date.split('-')
            self.setText(f"{day}/{month}/{year}")
        except (ValueError, IndexError):
            self.clear()

