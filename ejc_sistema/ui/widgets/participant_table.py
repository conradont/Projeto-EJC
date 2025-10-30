from PyQt6.QtWidgets import QTableWidget, QAbstractScrollArea
from PyQt6.QtCore import Qt


class ParticipantTable(QTableWidget):
    """Tabela simples para exibir participantes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_table()
    
    def _init_table(self):
        """Inicializa a configuração básica da tabela"""
        # Definições básicas
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Nome", "Data de Nasc.", "Telefone", "Ações"])
        
        # Desabilitar scrollbars (já que sempre exibimos 10 linhas fixas)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Configurar para não permitir scroll automático
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        
        # Aparência
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        
        # Larguras das colunas fixas
        self.setColumnWidth(0, 250)  # Nome
        self.setColumnWidth(1, 140)  # Data de Nasc.
        self.setColumnWidth(2, 180)  # Telefone
        self.setColumnWidth(3, 200)  # Ações
        
        # Fixar largura total da tabela
        total_width = 250 + 140 + 180 + 200
        self.setMaximumWidth(total_width)
        self.setMinimumWidth(total_width)
        
        # Altura fixa para exibir exatamente 10 linhas
        # Dobramos a altura padrão das linhas para acomodar melhor os botões de ações
        self.verticalHeader().setDefaultSectionSize(80)
        # Altura do header geralmente é ~45px, mais 10 linhas de 80px cada = ~845px
        table_height = 845
        self.setFixedHeight(table_height)

