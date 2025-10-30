"""Estilos da interface do sistema EJC"""


class StyleHelper:
    """Classe estática para fornecer estilos da interface"""
    
    @staticmethod
    def get_style():
        """Retorna o estilo CSS da aplicação"""
        return """
        QMainWindow, QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #0f1419, stop:1 #1a1d21);
            color: #e8e9ea;
        }
        
        /* Cabeçalho principal do app */
        QLabel#appHeader {
            font-size: 28px;
            font-weight: 700;
            color: #6366f1;
            padding: 24px;
            background: transparent;
            letter-spacing: 0.5px;
        }
        
        QTabWidget::pane {
            border: none;
            background: transparent;
            border-radius: 12px;
            padding: 20px;
        }
        
        QTabBar::tab {
            background-color: #1e2228;
            color: #9ca3af;
            padding: 14px 28px;
            border: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin-right: 4px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        QTabBar::tab:hover {
            background-color: #252831;
            color: #d1d5db;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #6366f1, stop:1 #8b5cf6);
            color: #ffffff;
            font-weight: 600;
        }
        
        QLabel {
            color: #e8e9ea;
            font-size: 14px;
            font-weight: 500;
            padding: 6px 0;
        }
        
        /* Títulos de seção em formulários */
        QLabel#sectionHeader {
            font-size: 20px;
            font-weight: 700;
            color: #8b5cf6;
            padding: 20px 0 12px 0;
            background: transparent;
            letter-spacing: 0.3px;
        }
        
        QLineEdit, QTextEdit, QDateEdit, QComboBox {
            padding: 12px 16px;
            border: 2px solid #2d3239;
            border-radius: 10px;
            background-color: #1e2228;
            color: #ffffff;
            font-size: 14px;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
        }
        
        QLineEdit:focus, QTextEdit:focus, QDateEdit:focus, QComboBox:focus {
            border-color: #6366f1;
            background-color: #252831;
            outline: none;
        }
        
        QTextEdit {
            min-height: 80px;
        }
        
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #6366f1, stop:1 #4f46e5);
            color: white;
            padding: 14px 32px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }
        
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #7c7ff0, stop:1 #6366f1);
            transform: translateY(-1px);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #4f46e5, stop:1 #4338ca);
        }
        
        /* Variantes por id */
        QPushButton#btnSecondary { 
            background: #374151;
        }
        QPushButton#btnSecondary:hover { 
            background: #4b5563;
        }
        
        QPushButton#btnSuccess { 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #10b981, stop:1 #059669);
        }
        QPushButton#btnSuccess:hover { 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #12d98f, stop:1 #10b981);
        }
        
        QPushButton#btnWarning { 
            background: #f59e0b;
            color: #000;
        }
        QPushButton#btnWarning:hover { 
            background: #fbbf24;
        }
        
        QPushButton#btnDanger { 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #ef4444, stop:1 #dc2626);
        }
        QPushButton#btnDanger:hover { 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #f87171, stop:1 #ef4444);
        }
        
        QPushButton#btnMuted { 
            background: #1f2937;
        }
        QPushButton#btnMuted:hover { 
            background: #374151;
        }
        
        QCheckBox {
            spacing: 10px;
            color: #e8e9ea;
            font-size: 14px;
            font-weight: 500;
        }
        
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid #374151;
            border-radius: 6px;
            background-color: #1e2228;
        }
        
        QCheckBox::indicator:checked {
            background-color: #6366f1;
            border-color: #6366f1;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzQgNEw2IDExLjMzMzQgMi42NjY3NCA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        
        QRadioButton {
            color: #e8e9ea;
            font-size: 14px;
            font-weight: 500;
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid #374151;
            background-color: #1e2228;
        }
        
        QRadioButton::indicator:checked {
            background-color: #6366f1;
            border-color: #6366f1;
        }
        
        QTableWidget {
            border: none;
            background-color: transparent; /* remove aparência de card */
            color: #e8e9ea;
            gridline-color: #2d3239;
            selection-background-color: rgba(99, 102, 241, 0.2);
            alternate-background-color: transparent;
        }
        
        QTableWidget::item {
            padding: 12px 16px;
            color: #e8e9ea;
            border: none;
            font-size: 14px;
        }
        
        QTableWidget::item:selected {
            background-color: rgba(99, 102, 241, 0.3);
            color: #ffffff;
        }
        
        QTableWidget::item:hover {
            background-color: #2d3239;
        }
        
        QTableWidget::item:alternate {
            background-color: #252831;
        }
        
        QHeaderView::section {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #0f1419, stop:1 #1a1d21);
            color: #8b5cf6;
            padding: 14px 16px;
            border: none;
            border-bottom: 2px solid #374151;
            font-weight: 700;
            font-size: 13px;
            letter-spacing: 0.5px;
        }
        
        QHeaderView::section:first {
            border-top-left-radius: 12px;
        }
        
        QHeaderView::section:last {
            border-top-right-radius: 12px;
        }
        
        /* Estilo para os botões dentro da tabela */
        QTableWidget QPushButton {
            padding: 0px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 4px;
            border: none;
            min-width: 36px;
            min-height: 36px;
            max-width: 36px;
            max-height: 36px;
        }

        /* Botões de ação com ícones - centralizados e com tamanho fixo */
        QPushButton[variant="action"] {
            background: transparent;
            border: none;
            color: white;
            padding: 0px;
            min-width: 30px;
            max-width: 30px;
            min-height: 25px;
            max-height: 25px;
            border-radius: 6px;
        }
        
        /* Botão de editar - fundo azul sólido */
        QPushButton[variant="action"][actionType="edit"] {
            background-color: #3b82f6;
            border: none;
            color: white;
        }
        QPushButton[variant="action"][actionType="edit"]:hover {
            background-color: #2563eb;
        }
        QPushButton[variant="action"][actionType="edit"]:pressed {
            background-color: #1d4ed8;
        }
        
        /* Botão de excluir - fundo vermelho sólido */
        QPushButton[variant="action"][actionType="delete"] {
            background-color: #ef4444;
            border: none;
            color: white;
        }
        QPushButton[variant="action"][actionType="delete"]:hover {
            background-color: #dc2626;
        }
        QPushButton[variant="action"][actionType="delete"]:pressed {
            background-color: #b91c1c;
        }
        
        QScrollArea {
            border: none;
            background: transparent;
        }
        
        QScrollBar:vertical {
            width: 12px;
            background: #1e2228;
            border-radius: 6px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #6366f1;
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #818cf8;
        }
        
        QScrollBar::handle:vertical:pressed {
            background: #4f46e5;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;
        }
        
        QScrollBar:horizontal {
            height: 12px;
            background: #1e2228;
            border-radius: 6px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #6366f1;
            border-radius: 6px;
            min-width: 30px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #818cf8;
        }
        
        QScrollBar::handle:horizontal:pressed {
            background: #4f46e5;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
        }
        
        QMessageBox {
            background-color: #1e2228;
            color: #e8e9ea;
        }
        
        QMessageBox QPushButton {
            min-width: 100px;
        }
        
        QDateEdit::drop-down {
            border: none;
            width: 25px;
            subcontrol-origin: padding;
            subcontrol-position: right center;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 25px;
            subcontrol-origin: padding;
            subcontrol-position: right center;
        }
        
        QComboBox QAbstractItemView {
            background-color: #1e2228;
            color: #e8e9ea;
            selection-background-color: #6366f1;
            selection-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #374151;
        }
        
        QGroupBox {
            color: #8b5cf6;
            font-weight: 700;
            border: 2px solid #374151;
            border-radius: 12px;
            margin-top: 24px;
            padding-top: 24px;
            background-color: #1e2228;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 12px;
            font-size: 15px;
        }
        
        /* Pré-visualização de imagem/área drop */
        QLabel#photoPreview, QLabel#imageDrop {
            border: 3px dashed #4b5563;
            border-radius: 12px;
            background: rgba(99, 102, 241, 0.05);
        }
        
        QLabel#imageDrop {
            padding: 20px;
        }
        
        /* Controles de paginação mais visíveis */
        QWidget#paginationWidget {
            background-color: transparent; /* remove aparência de card */
            border: none;
            padding: 16px;
            margin-top: 16px;
        }
        
        QLabel#paginationInfo {
            font-size: 15px;
            font-weight: 600;
            color: #8b5cf6;
            padding: 12px 20px;
            background-color: rgba(139, 92, 246, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        
        QPushButton:disabled {
            background: #374151;
            color: #6b7280;
            opacity: 0.5;
        }
        """