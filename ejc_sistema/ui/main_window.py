from pathlib import Path
import datetime
import shutil
import traceback

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidgetItem, QMessageBox, QDialog,
    QTextEdit, QFileDialog, QCheckBox, QRadioButton, QButtonGroup,
    QScrollArea, QGridLayout, QTabWidget, QInputDialog, QComboBox, QGroupBox, QProgressBar
)
from PyQt6.QtGui import QPixmap, QCursor, QIcon, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray
from PIL import Image

from config import WINDOW_TITLE, WINDOW_GEOMETRY, DB_PATH, EJC_DATA_DIR, PHOTOS_DIR
from ui.style import StyleHelper
from ui.widgets.date_line_edit import DateLineEdit
from ui.widgets.participant_table import ParticipantTable
from ui.widgets.photo_widget import PhotoWidget
from database.db_manager import DatabaseManager
from reports.pdf_generator import PDFGenerator
from utils.validators import validate_participant_data
from utils.logger import log_error, log_warning, log_info
from utils.backup_manager import BackupManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        x, y, w, h = WINDOW_GEOMETRY
        self.setGeometry(x, y, w, h)
        self.setStyleSheet(StyleHelper.get_style())

        # Paths e DB
        self.data_dir = EJC_DATA_DIR
        self.photos_dir = PHOTOS_DIR
        self.db_path = DB_PATH
        self.logo_path = None

        # Garantir diretórios e DB
        self.db = DatabaseManager(self.db_path)
        self.backup_manager = BackupManager(self.db_path)
        
        # Criar backup automático na inicialização (apenas se DB já existe)
        if self.db_path.exists():
            try:
                self.backup_manager.create_backup(prefix="init")
            except Exception as e:
                log_error(e, "Erro ao criar backup na inicialização")

        # Widget e layout principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        header = QLabel("EJC - Sistema de Registro")
        header.setObjectName("appHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.registration_tab = QWidget()
        self.participants_tab = QWidget()
        self.reports_tab = QWidget()
        self.logo_tab = QWidget()

        self.tab_widget.addTab(self.registration_tab, "Novo Registro")
        self.tab_widget.addTab(self.participants_tab, "Lista de Participantes")
        self.tab_widget.addTab(self.reports_tab, "Relatórios")
        self.tab_widget.addTab(self.logo_tab, "Logo do Evento")

        self.setup_registration_tab()
        self.setup_participants_tab()
        self.setup_reports_tab()
        self.setup_logo_tab()

        self.load_participants()
    
    def _create_icon_from_svg(self, svg_string: str, size: int = 16) -> QIcon:
        """Cria um QIcon a partir de uma string SVG"""
        try:
            svg_data = QByteArray(svg_string.encode('utf-8'))
            renderer = QSvgRenderer(svg_data)
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except:
            # Fallback: retornar ícone vazio
            return QIcon()

    def setup_registration_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setSpacing(15)

        section_personal = QLabel("Informações Pessoais")
        section_personal.setObjectName("sectionHeader")
        form_layout.addWidget(section_personal, 0, 0, 1, 2)

        current_row = 1

        self.add_form_field(form_layout, current_row, "Nome Completo:", "name_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Nome Usual:", "common_name_input"); current_row += 1

        form_layout.addWidget(QLabel("Data de Nascimento:"), current_row, 0)
        self.birth_date_input = DateLineEdit()
        form_layout.addWidget(self.birth_date_input, current_row, 1)
        current_row += 1

        self.add_form_field(form_layout, current_row, "Instagram:", "instagram_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Endereço:", "address_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Bairro / Comunidade:", "neighborhood_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Email:", "email_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Celular:", "phone_input"); current_row += 1

        section_sacraments = QLabel("Sacramentos")
        section_sacraments.setObjectName("sectionHeader")
        form_layout.addWidget(section_sacraments, current_row, 0, 1, 2)
        current_row += 1

        sacraments = ["Batismo", "Primeira Eucaristia", "Crisma"]
        options = ["Concluído", "Não Concluído", "Em Processo"]
        self.sacrament_options = {}
        for sacrament in sacraments:
            form_layout.addWidget(QLabel(sacrament + ":"), current_row, 0)
            option_widget = QWidget()
            option_layout = QHBoxLayout(option_widget)
            sacrament_checkboxes = []
            for option in options:
                checkbox = QCheckBox(option)
                sacrament_checkboxes.append(checkbox)
                option_layout.addWidget(checkbox)
                # Quando um checkbox é marcado, desmarca os outros do mesmo grupo
                checkbox.clicked.connect(lambda checked, cb=checkbox, checkboxes=sacrament_checkboxes: self.handle_sacrament_checkbox(cb, checkboxes))
            self.sacrament_options[sacrament] = sacrament_checkboxes
            form_layout.addWidget(option_widget, current_row, 1)
            current_row += 1

        section_church = QLabel("Informações da Igreja")
        section_church.setObjectName("sectionHeader")
        form_layout.addWidget(section_church, current_row, 0, 1, 2)
        current_row += 1
        
        self.church_movement_yes = QCheckBox("Sim")
        self.church_movement_no = QCheckBox("Não")
        church_movement_container = QWidget()
        church_movement_layout = QHBoxLayout(church_movement_container)
        church_movement_layout.addWidget(QLabel("Participa de algum movimento da igreja:"))
        church_movement_layout.addWidget(self.church_movement_yes)
        church_movement_layout.addWidget(self.church_movement_no)
        form_layout.addWidget(church_movement_container, current_row, 0, 1, 2)
        current_row += 1
        self.church_movement_yes.clicked.connect(self.toggle_church_movement)
        self.church_movement_no.clicked.connect(self.toggle_church_movement)
        
        self.church_movement_input = QLineEdit()
        self.church_movement_input.setPlaceholderText("Nome do movimento da igreja")
        self.church_movement_input.hide()
        form_layout.addWidget(self.church_movement_input, current_row, 0, 1, 2)
        current_row += 1

        section_family = QLabel("Informações Familiares")
        section_family.setObjectName("sectionHeader")
        form_layout.addWidget(section_family, current_row, 0, 1, 2)
        current_row += 1
        self.add_form_field(form_layout, current_row, "Nome do Pai:", "father_name_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Contato do Pai:", "father_contact_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Nome da Mãe:", "mother_name_input"); current_row += 1
        self.add_form_field(form_layout, current_row, "Contato da Mãe:", "mother_contact_input"); current_row += 1

        self.ecc_participant_yes = QCheckBox("Sim")
        self.ecc_participant_no = QCheckBox("Não")
        ecc_checkbox_widget = QWidget()
        ecc_checkbox_layout = QHBoxLayout(ecc_checkbox_widget)
        ecc_checkbox_layout.addWidget(QLabel("Pais são encontristas do ECC:"))
        ecc_checkbox_layout.addWidget(self.ecc_participant_yes)
        ecc_checkbox_layout.addWidget(self.ecc_participant_no)
        form_layout.addWidget(ecc_checkbox_widget, current_row, 0, 1, 2)
        current_row += 1
        self.ecc_participant_yes.clicked.connect(self.toggle_ecc_participant)
        self.ecc_participant_no.clicked.connect(self.toggle_ecc_participant)

        self.ecc_info_input = QLineEdit()
        self.ecc_info_input.setPlaceholderText("Informações adicionais sobre ECC")
        self.ecc_info_input.hide()
        form_layout.addWidget(self.ecc_info_input, current_row, 0, 1, 2)
        current_row += 1

        section_additional = QLabel("Informações Adicionais")
        section_additional.setObjectName("sectionHeader")
        form_layout.addWidget(section_additional, current_row, 0, 1, 2)
        current_row += 1

        restrictions_container = QWidget()
        restrictions_layout = QHBoxLayout(restrictions_container)
        restrictions_layout.addWidget(QLabel("Possui restrições alimentares ou alergias:"))
        self.restrictions_yes = QCheckBox("Sim")
        self.restrictions_no = QCheckBox("Não")
        restrictions_layout.addWidget(self.restrictions_yes)
        restrictions_layout.addWidget(self.restrictions_no)
        form_layout.addWidget(restrictions_container, current_row, 0, 1, 2)
        current_row += 1
        self.restrictions_yes.clicked.connect(self.toggle_restrictions)
        self.restrictions_no.clicked.connect(self.toggle_restrictions)

        self.restrictions_info_input = QLineEdit()
        self.restrictions_info_input.setPlaceholderText("Detalhes sobre restrições alimentares ou alergias")
        self.restrictions_info_input.hide()
        form_layout.addWidget(self.restrictions_info_input, current_row, 0, 1, 2)
        current_row += 1

        self.photo_widget = PhotoWidget(self.photos_dir)
        form_layout.addWidget(self.photo_widget, current_row, 0, 1, 2)
        current_row += 1

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(10)
        
        register_button = QPushButton("Registrar Participante")
        register_button.clicked.connect(self.register_participant)
        register_button.setObjectName("btnSuccess")
        buttons_layout.addWidget(register_button)
        
        clear_button = QPushButton("Limpar Formulário")
        clear_button.clicked.connect(self.clear_form)
        clear_button.setObjectName("btnSecondary")
        buttons_layout.addWidget(clear_button)
        
        buttons_layout.addStretch()
        form_layout.addWidget(buttons_widget, current_row, 0, 1, 2)

        scroll.setWidget(form_widget)
        layout = QVBoxLayout(self.registration_tab)
        layout.addWidget(scroll)

    def setup_participants_tab(self):
        # Criar scrollarea para todo o conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Widget container para todo o conteúdo
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        header = QLabel("Lista de Participantes Registrados")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        search_section = QGroupBox("Pesquisa e Filtros Avançados")
        search_layout = QGridLayout()
        
        # Busca por texto
        search_layout.addWidget(QLabel("Pesquisar:"), 0, 0)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para pesquisar por nome, email, telefone, instagram...")
        self.search_input.textChanged.connect(self.filter_participants)
        search_layout.addWidget(self.search_input, 0, 1, 1, 3)
        
        # Filtro por sacramento
        search_layout.addWidget(QLabel("Sacramento:"), 1, 0)
        self.sacrament_filter = QComboBox()
        self.sacrament_filter.addItem("Todos os Sacramentos")
        self.sacrament_filter.addItem("Batismo: Concluído")
        self.sacrament_filter.addItem("Primeira Eucaristia: Concluído")
        self.sacrament_filter.addItem("Crisma: Concluído")
        self.sacrament_filter.addItem("Sacramentos Incompletos")
        self.sacrament_filter.currentIndexChanged.connect(self.filter_participants)
        search_layout.addWidget(self.sacrament_filter, 1, 1)
        
        # Filtro por movimento da igreja
        search_layout.addWidget(QLabel("Movimento:"), 1, 2)
        self.movement_filter = QComboBox()
        self.movement_filter.addItem("Todos")
        self.movement_filter.addItem("Com Movimento")
        self.movement_filter.addItem("Sem Movimento")
        self.movement_filter.currentIndexChanged.connect(self.filter_participants)
        search_layout.addWidget(self.movement_filter, 1, 3)
        
        # Filtro por ECC
        search_layout.addWidget(QLabel("Pais ECC:"), 2, 0)
        self.ecc_filter = QComboBox()
        self.ecc_filter.addItem("Todos")
        self.ecc_filter.addItem("Sim")
        self.ecc_filter.addItem("Não")
        self.ecc_filter.currentIndexChanged.connect(self.filter_participants)
        search_layout.addWidget(self.ecc_filter, 2, 1)
        
        # Filtro por restrições
        search_layout.addWidget(QLabel("Restrições:"), 2, 2)
        self.restrictions_filter = QComboBox()
        self.restrictions_filter.addItem("Todos")
        self.restrictions_filter.addItem("Com Restrições")
        self.restrictions_filter.addItem("Sem Restrições")
        self.restrictions_filter.currentIndexChanged.connect(self.filter_participants)
        search_layout.addWidget(self.restrictions_filter, 2, 3)
        
        # Botão limpar filtros
        clear_filters_button = QPushButton("Limpar Filtros")
        clear_filters_button.clicked.connect(self.clear_filters)
        clear_filters_button.setObjectName("btnSecondary")
        search_layout.addWidget(clear_filters_button, 3, 0, 1, 4)
        
        search_section.setLayout(search_layout)
        layout.addWidget(search_section)

        # Container para centralizar a tabela (estilo igual ao dos filtros)
        table_container = QGroupBox("Lista de Participantes")
        table_layout = QHBoxLayout()
        table_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.participant_table = ParticipantTable()
        table_layout.addWidget(self.participant_table)
        table_container.setLayout(table_layout)
        
        layout.addWidget(table_container)
        
        # Controles de paginação - com melhor visibilidade
        pagination_widget = QWidget()
        pagination_widget.setObjectName("paginationWidget")
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.setSpacing(16)
        pagination_layout.setContentsMargins(20, 20, 20, 20)
        
        self.pagination_info = QLabel("Página 1 de 1")
        self.pagination_info.setObjectName("paginationInfo")
        self.pagination_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.pagination_info)
        
        pagination_layout.addSpacing(20)
        
        self.prev_page_button = QPushButton("◄ Anterior")
        self.prev_page_button.clicked.connect(self.go_to_prev_page)
        self.prev_page_button.setEnabled(False)
        pagination_layout.addWidget(self.prev_page_button)
        
        self.next_page_button = QPushButton("Próximo ►")
        self.next_page_button.clicked.connect(self.go_to_next_page)
        self.next_page_button.setEnabled(False)
        pagination_layout.addWidget(self.next_page_button)
        
        layout.addWidget(pagination_widget)
        
        # Variáveis de paginação
        self.current_page = 1
        self.items_per_page = 10
        self.all_participants = []  # Armazena todos os participantes filtrados
        
        # Configurar scrollarea e adicionar ao layout da aba
        scroll.setWidget(content_widget)
        tab_layout = QVBoxLayout(self.participants_tab)
        tab_layout.addWidget(scroll)

    def setup_reports_tab(self):
        layout = QVBoxLayout()
        header = QLabel("Geração de Relatórios")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        generate_pdf_button = QPushButton("Gerar PDF Individual")
        generate_pdf_button.clicked.connect(self.generate_individual_pdf)
        layout.addWidget(generate_pdf_button)

        generate_complete_pdf_button = QPushButton("Gerar PDF Completo")
        generate_complete_pdf_button.clicked.connect(self.generate_complete_pdf)
        layout.addWidget(generate_complete_pdf_button)

        layout.addStretch()
        self.reports_tab.setLayout(layout)

    def setup_logo_tab(self):
        layout = QVBoxLayout()
        header = QLabel("Gerenciamento do Logo do Evento")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumSize(200, 200)
        self.logo_label.setObjectName("imageDrop")
        layout.addWidget(self.logo_label)

        upload_logo_button = QPushButton("Carregar Logo")
        upload_logo_button.clicked.connect(self.upload_logo)
        layout.addWidget(upload_logo_button)

        layout.addStretch()
        self.logo_tab.setLayout(layout)

    def add_form_field(self, layout, row, label_text, input_name):
        label = QLabel(label_text)
        setattr(self, input_name, QLineEdit())
        layout.addWidget(label, row, 0)
        layout.addWidget(getattr(self, input_name), row, 1)

    def get_db_connection(self):
        return self.db.get_connection()

    def load_participants(self):
        """Carrega todos os participantes e exibe a primeira página"""
        conn = self.get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participants ORDER BY name")
            self.all_participants = cursor.fetchall()
            self.current_page = 1
            self.display_page()
        finally:
            conn.close()
    
    def display_page(self):
        """Exibe a página atual da tabela (10 registros por página)"""
        total_pages = (len(self.all_participants) + self.items_per_page - 1) // self.items_per_page if self.all_participants else 1
        
        # Calcular índices dos participantes a exibir
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.all_participants))
        page_participants = self.all_participants[start_idx:end_idx]
        
        # Sempre exibir 10 linhas na tabela
        self.participant_table.setRowCount(self.items_per_page)
        
        # Preencher linhas com dados
        for row in range(self.items_per_page):
            if row < len(page_participants):
                participant = page_participants[row]
                
                self.participant_table.setItem(row, 0, QTableWidgetItem(participant['name']))
                
                birth_date = participant['birth_date'] or ""
                if birth_date:
                    try:
                        date_obj = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                        birth_date = date_obj.strftime("%d/%m/%Y")
                    except ValueError:
                        pass
                self.participant_table.setItem(row, 1, QTableWidgetItem(birth_date))
                
                phone_display = participant['phone'] or ""
                self.participant_table.setItem(row, 2, QTableWidgetItem(phone_display))
                
                # Ações com ícones
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(8, 4, 8, 4)
                actions_layout.setSpacing(8)
                actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Ícone de lápis (SVG)
                edit_icon_svg = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M11.3333 2.00004C11.5084 1.82492 11.7163 1.68698 11.9444 1.59527C12.1726 1.50357 12.4161 1.46021 12.6611 1.46804C12.9061 1.47588 13.1471 1.53473 13.3691 1.64104C13.5911 1.74735 13.7893 1.89877 13.9519 2.08638C14.1145 2.27398 14.2378 2.49373 14.3147 2.73139C14.3916 2.96906 14.4204 3.21963 14.399 3.46804C14.3776 3.71645 14.3065 3.95741 14.19 4.17538C14.0736 4.39335 13.9146 4.58341 13.7233 4.73338L5.44444 13.0117L1.33333 14.0004L2.32222 9.88932L10.6011 1.61171L11.3333 2.00004Z" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
                edit_button = QPushButton()
                edit_button.setProperty("variant", "action")
                edit_button.setProperty("actionType", "edit")
                edit_icon = self._create_icon_from_svg(edit_icon_svg, 14)
                if not edit_icon.isNull():
                    edit_button.setIcon(edit_icon)
                else:
                    edit_button.setText("✏")
                edit_button.setToolTip("Editar")
                edit_button.setFixedSize(30, 25)
                edit_button.clicked.connect(lambda _, p=participant: self.edit_participant(p))
                
                # Ícone de lixeira (SVG)
                delete_icon_svg = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 4H14M12.6667 4V13.3333C12.6667 13.687 12.5262 14.0261 12.2761 14.2762C12.026 14.5263 11.6869 14.6667 11.3333 14.6667H4.66667C4.31305 14.6667 3.97391 14.5263 3.72381 14.2762C3.47371 14.0261 3.33333 13.687 3.33333 13.3333V4M5.33333 4V2.66667C5.33333 2.31305 5.47371 1.97391 5.72381 1.72381C5.97391 1.47371 6.31305 1.33333 6.66667 1.33333H9.33333C9.68695 1.33333 10.0261 1.47371 10.2762 1.72381C10.5263 1.97391 10.6667 2.31305 10.6667 2.66667V4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
                delete_button = QPushButton()
                delete_button.setProperty("variant", "action")
                delete_button.setProperty("actionType", "delete")
                delete_icon = self._create_icon_from_svg(delete_icon_svg, 14)
                if not delete_icon.isNull():
                    delete_button.setIcon(delete_icon)
                else:
                    delete_button.setText("🗑")
                delete_button.setToolTip("Excluir")
                delete_button.setFixedSize(30, 25)
                delete_button.clicked.connect(lambda _, p=participant: self.delete_participant(p))
                
                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                
                self.participant_table.setCellWidget(row, 3, actions_widget)
            else:
                # Preencher linhas vazias quando não há mais participantes
                for col in range(4):
                    self.participant_table.setItem(row, col, QTableWidgetItem(""))
                # Remover widget de ações se existir
                self.participant_table.setCellWidget(row, 3, None)
        
        # Atualizar controles de paginação
        self.update_pagination_controls(total_pages)
    
    def update_pagination_controls(self, total_pages):
        """Atualiza os controles de paginação"""
        if total_pages == 0:
            total_pages = 1
        
        self.pagination_info.setText(f"Página {self.current_page} de {total_pages} | Total: {len(self.all_participants)} participantes")
        
        # Habilitar/desabilitar botões
        self.prev_page_button.setEnabled(self.current_page > 1)
        self.next_page_button.setEnabled(self.current_page < total_pages)
    
    def go_to_prev_page(self):
        """Vai para a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()
    
    def go_to_next_page(self):
        """Vai para a próxima página"""
        total_pages = (len(self.all_participants) + self.items_per_page - 1) // self.items_per_page if self.all_participants else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_page()

    def filter_participants(self):
        """Filtra participantes com múltiplos critérios"""
        search_text = self.search_input.text().lower()
        sacrament_filter = self.sacrament_filter.currentText()
        movement_filter = self.movement_filter.currentText()
        ecc_filter = self.ecc_filter.currentText()
        restrictions_filter = self.restrictions_filter.currentText()
        
        conn = self.get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM participants"
            params = []
            conditions = []
            
            # Busca por texto
            if search_text:
                conditions.append(
                    "(LOWER(name) LIKE ? OR LOWER(common_name) LIKE ? OR "
                    "LOWER(email) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(instagram) LIKE ? OR "
                    "LOWER(address) LIKE ? OR LOWER(neighborhood) LIKE ?)"
                )
                search_param = f"%{search_text}%"
                params.extend([search_param] * 7)
            
            # Filtro por movimento da igreja
            if movement_filter == "Com Movimento":
                conditions.append("(church_movement IS NOT NULL AND church_movement != '')")
            elif movement_filter == "Sem Movimento":
                conditions.append("(church_movement IS NULL OR church_movement = '')")
            
            # Filtro por ECC
            if ecc_filter == "Sim":
                conditions.append("ecc_participant = 1")
            elif ecc_filter == "Não":
                conditions.append("(ecc_participant = 0 OR ecc_participant IS NULL)")
            
            # Filtro por restrições
            if restrictions_filter == "Com Restrições":
                conditions.append("has_restrictions = 1")
            elif restrictions_filter == "Sem Restrições":
                conditions.append("(has_restrictions = 0 OR has_restrictions IS NULL)")
            
            # Adicionar WHERE se houver condições
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            participants = cursor.fetchall()
            
            # Filtro por sacramento (processado após query pois requer análise do campo)
            if sacrament_filter != "Todos os Sacramentos":
                if sacrament_filter == "Sacramentos Incompletos":
                    filtered = []
                    for p in participants:
                        sacraments = p['sacraments'].split(',') if p['sacraments'] else []
                        if any(("Não Concluído" in s or "Em Processo" in s) for s in sacraments):
                            filtered.append(p)
                    participants = filtered
                else:
                    sacrament_name, status = sacrament_filter.split(": ")
                    filtered = []
                    for p in participants:
                        sacraments = p['sacraments'].split(',') if p['sacraments'] else []
                        for s in sacraments:
                            if s.startswith(f"{sacrament_name}:") and status in s:
                                filtered.append(p)
                                break
                    participants = filtered
            
            # Armazenar todos os participantes filtrados e resetar para primeira página
            self.all_participants = participants
            self.current_page = 1
            self.display_page()
        finally:
            conn.close()

    def clear_filters(self):
        """Limpa todos os filtros de busca"""
        self.search_input.clear()
        self.sacrament_filter.setCurrentIndex(0)
        self.movement_filter.setCurrentIndex(0)
        self.ecc_filter.setCurrentIndex(0)
        self.restrictions_filter.setCurrentIndex(0)
        self.load_participants()

    def add_photo(self):
        pass

    def register_participant(self):
        """Registra um novo participante com validação e feedback visual"""
        try:
            # Coletar dados do formulário
            name = self.name_input.text().strip()
            common_name = self.common_name_input.text().strip()
            birth_date = self.birth_date_input.get_iso_date()
            instagram = self.instagram_input.text().strip()
            father_contact = self.father_contact_input.text().strip()
            mother_contact = self.mother_contact_input.text().strip()
            address = self.address_input.text().strip()
            neighborhood = self.neighborhood_input.text().strip()
            email = self.email_input.text().strip()
            phone = self.phone_input.text().strip()
            sacraments = []
            for sacrament, checkboxes in self.sacrament_options.items():
                selected = next((cb.text() for cb in checkboxes if cb.isChecked()), "Não Informado")
                sacraments.append(f"{sacrament}:{selected}")
            church_movement = self.church_movement_input.text().strip() if self.church_movement_input.isVisible() else ""
            father_name = self.father_name_input.text().strip()
            mother_name = self.mother_name_input.text().strip()
            ecc_participant = self.ecc_participant_yes.isChecked()
            ecc_info = self.ecc_info_input.text().strip() if self.ecc_info_input.isVisible() else ""
            has_restrictions = self.restrictions_yes.isChecked()
            restrictions_info = self.restrictions_info_input.text().strip() if self.restrictions_info_input.isVisible() else ""
            photo_path = self.photo_widget.get_photo_path()
            
            # Preparar dados para validação
            participant_data = {
                'name': name,
                'common_name': common_name,
                'birth_date': birth_date,
                'instagram': instagram,
                'father_contact': father_contact,
                'mother_contact': mother_contact,
                'email': email,
                'phone': phone
            }
            
            # Validar dados
            is_valid, error_message = validate_participant_data(participant_data)
            if not is_valid:
                QMessageBox.warning(self, "Validação", error_message)
                log_warning(f"Tentativa de registro com dados inválidos: {error_message}")
                return
            
            # Feedback visual: cursor de loading
            self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
            try:
                conn = self.get_db_connection()
                if not conn:
                    QMessageBox.critical(self, "Erro de Conexão", 
                                       "Não foi possível conectar ao banco de dados. "
                                       "Verifique os logs para mais detalhes.")
                    log_error(Exception("Falha na conexão com banco de dados"), "register_participant")
                    return
                
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        '''
                        INSERT INTO participants (
                            name, common_name, birth_date, instagram, address, neighborhood,
                            email, phone, sacraments, church_movement,
                            father_name, father_contact, mother_name, mother_contact, ecc_participant, ecc_info,
                            has_restrictions, restrictions_info,
                            photo_path
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            name, common_name, birth_date, instagram, address, neighborhood,
                            email, phone, ','.join(sacraments), church_movement,
                            father_name, father_contact, mother_name, mother_contact, ecc_participant, ecc_info,
                            has_restrictions, restrictions_info,
                            photo_path
                        )
                    )
                    conn.commit()
                    participant_id = cursor.lastrowid
                    log_info(f"Participante registrado com sucesso: ID {participant_id}, Nome: {name}")
                    
                    # Criar backup automático após registro bem-sucedido
                    try:
                        self.backup_manager.create_backup(prefix="post_register")
                    except Exception as backup_error:
                        log_error(backup_error, "Erro ao criar backup após registro")
                    
                    QMessageBox.information(self, "Sucesso", "Participante registrado com sucesso!")
                    self.load_participants()
                    self.clear_form()
                    
                except Exception as db_error:
                    conn.rollback()
                    error_msg = f"Erro ao salvar no banco de dados: {str(db_error)}"
                    log_error(db_error, f"register_participant - Database error para {name}")
                    QMessageBox.critical(self, "Erro no Banco de Dados", 
                                       error_msg + "\n\nOs dados não foram salvos. "
                                       "Verifique os logs para mais detalhes.")
                finally:
                    conn.close()
            finally:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
                
        except Exception as e:
            error_msg = log_error(e, "register_participant - Erro geral")
            QMessageBox.critical(self, "Erro Inesperado", 
                               f"Ocorreu um erro inesperado ao registrar o participante.\n\n"
                               f"Detalhes: {str(e)}\n\n"
                               f"Verifique os logs para mais informações.")

    def has_form_data(self) -> bool:
        """Verifica se o formulário tem dados preenchidos"""
        return bool(
            self.name_input.text().strip() or
            self.common_name_input.text().strip() or
            self.email_input.text().strip() or
            self.phone_input.text().strip() or
            self.address_input.text().strip() or
            any(cb.isChecked() for checkboxes in self.sacrament_options.values() for cb in checkboxes)
        )
    
    def clear_form(self):
        """Limpa o formulário com confirmação se houver dados"""
        # Verificar se há dados no formulário
        if self.has_form_data():
            reply = QMessageBox.question(
                self, "Confirmar Limpeza",
                "O formulário contém dados não salvos.\n\n"
                "Deseja realmente limpar todos os campos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Limpar todos os campos
        self.name_input.clear()
        self.common_name_input.clear()
        self.birth_date_input.clear()
        self.instagram_input.clear()
        self.address_input.clear()
        self.neighborhood_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.church_movement_input.clear()
        self.church_movement_input.hide()
        self.church_movement_yes.setChecked(False)
        self.church_movement_no.setChecked(False)
        self.father_name_input.clear()
        self.father_contact_input.clear()
        self.mother_name_input.clear()
        self.mother_contact_input.clear()
        self.ecc_info_input.clear()
        self.restrictions_info_input.clear()
        self.ecc_participant_yes.setChecked(False)
        self.ecc_participant_no.setChecked(False)
        self.ecc_info_input.hide()
        self.restrictions_yes.setChecked(False)
        self.restrictions_no.setChecked(False)
        self.restrictions_info_input.hide()
        for checkboxes in self.sacrament_options.values():
            for checkbox in checkboxes:
                checkbox.setChecked(False)
        self.photo_widget.set_photo_path(None)
        log_info("Formulário limpo")

    def edit_participant(self, participant):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Participante")
        dialog.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout()
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        form_widget = QWidget(); form_layout = QGridLayout(form_widget)
        name_input = QLineEdit(participant['name']); form_layout.addWidget(QLabel("Nome Completo:"), 0, 0); form_layout.addWidget(name_input, 0, 1)
        common_name_input = QLineEdit(participant['common_name'] or ''); form_layout.addWidget(QLabel("Nome Usual:"), 1, 0); form_layout.addWidget(common_name_input, 1, 1)
        birth_date_input = DateLineEdit();
        if participant['birth_date']:
            birth_date_input.set_from_iso_date(participant['birth_date'])
        form_layout.addWidget(QLabel("Data de Nascimento:"), 2, 0); form_layout.addWidget(birth_date_input, 2, 1)
        instagram_input = QLineEdit(participant['instagram'] or ''); form_layout.addWidget(QLabel("Instagram:"), 3, 0); form_layout.addWidget(instagram_input, 3, 1)
        address_input = QLineEdit(participant['address'] or ''); form_layout.addWidget(QLabel("Endereço:"), 4, 0); form_layout.addWidget(address_input, 4, 1)
        neighborhood_input = QLineEdit(participant['neighborhood'] or ''); form_layout.addWidget(QLabel("Bairro / Comunidade:"), 5, 0); form_layout.addWidget(neighborhood_input, 5, 1)
        email_input = QLineEdit(participant['email'] or ''); form_layout.addWidget(QLabel("Email:"), 7, 0); form_layout.addWidget(email_input, 7, 1)
        phone_input = QLineEdit(participant['phone'] or ''); form_layout.addWidget(QLabel("Celular:"), 8, 0); form_layout.addWidget(phone_input, 8, 1)
        sacraments = participant['sacraments'].split(',') if participant['sacraments'] else []
        form_layout.addWidget(QLabel("Sacramentos:"), 9, 0)
        sacrament_widget = QWidget(); sacrament_layout = QVBoxLayout(sacrament_widget)
        sacrament_options = {}
        for sacrament in ["Batismo", "Primeira Eucaristia", "Crisma"]:
            sacrament_label = QLabel(sacrament + ":"); sacrament_layout.addWidget(sacrament_label)
            option_widget = QWidget(); option_layout = QHBoxLayout(option_widget)
            selected_option = "Não Informado"
            for s in sacraments:
                if s.startswith(f"{sacrament}:"):
                    selected_option = s.split(':')[1].strip(); break
            sacrament_checkboxes = []
            for option in ["Concluído", "Não Concluído", "Em Processo"]:
                checkbox = QCheckBox(option); checkbox.setChecked(option == selected_option)
                sacrament_checkboxes.append(checkbox)
                option_layout.addWidget(checkbox)
                # Quando um checkbox é marcado, desmarca os outros do mesmo grupo
                checkbox.clicked.connect(lambda checked, cb=checkbox, checkboxes=sacrament_checkboxes: self.handle_sacrament_checkbox(cb, checkboxes))
            sacrament_options[sacrament] = sacrament_checkboxes; sacrament_layout.addWidget(option_widget)
        form_layout.addWidget(sacrament_widget, 9, 1)
        church_movement_yes = QCheckBox("Sim"); church_movement_no = QCheckBox("Não")
        has_movement = bool(participant['church_movement'])
        church_movement_yes.setChecked(has_movement); church_movement_no.setChecked(not has_movement)
        church_movement_container = QWidget(); church_movement_layout = QHBoxLayout(church_movement_container)
        church_movement_layout.addWidget(QLabel("Participa de algum movimento da igreja:")); church_movement_layout.addWidget(church_movement_yes); church_movement_layout.addWidget(church_movement_no)
        form_layout.addWidget(church_movement_container, 10, 0, 1, 2)
        church_movement_input = QLineEdit(participant['church_movement'] or '')
        church_movement_input.setPlaceholderText("Nome do movimento da igreja")
        church_movement_input.setVisible(has_movement)
        form_layout.addWidget(church_movement_input, 11, 0, 1, 2)
        def toggle_church_movement_dialog():
            if church_movement_yes.isChecked():
                church_movement_no.setChecked(False)
                church_movement_input.show()
            else:
                church_movement_input.hide()
                church_movement_input.clear()
        def toggle_church_movement_no():
            if church_movement_no.isChecked():
                church_movement_yes.setChecked(False)
                church_movement_input.hide()
                church_movement_input.clear()
        church_movement_yes.clicked.connect(toggle_church_movement_dialog)
        church_movement_no.clicked.connect(toggle_church_movement_no)
        father_name_input = QLineEdit(participant['father_name'] or ''); form_layout.addWidget(QLabel("Nome do Pai:"), 12, 0); form_layout.addWidget(father_name_input, 12, 1)
        father_contact_input = QLineEdit(participant['father_contact'] or ''); form_layout.addWidget(QLabel("Contato do Pai:"), 13, 0); form_layout.addWidget(father_contact_input, 13, 1)
        mother_name_input = QLineEdit(participant['mother_name'] or ''); form_layout.addWidget(QLabel("Nome da Mãe:"), 14, 0); form_layout.addWidget(mother_name_input, 14, 1)
        mother_contact_input = QLineEdit(participant['mother_contact'] or ''); form_layout.addWidget(QLabel("Contato da Mãe:"), 15, 0); form_layout.addWidget(mother_contact_input, 15, 1)
        ecc_participant_yes = QCheckBox("Sim"); ecc_participant_no = QCheckBox("Não")
        ecc_participant_yes.setChecked(participant['ecc_participant']); ecc_participant_no.setChecked(not participant['ecc_participant'])
        ecc_widget = QWidget(); ecc_layout = QHBoxLayout(ecc_widget)
        ecc_layout.addWidget(QLabel("Pais são encontristas do ECC:")); ecc_layout.addWidget(ecc_participant_yes); ecc_layout.addWidget(ecc_participant_no)
        form_layout.addWidget(ecc_widget, 16, 0, 1, 2)
        ecc_info_input = QLineEdit(participant['ecc_info'] or '')
        ecc_info_input.setPlaceholderText("Informações adicionais sobre ECC")
        ecc_info_input.setVisible(participant['ecc_participant'])
        form_layout.addWidget(ecc_info_input, 17, 0, 1, 2)
        def toggle_ecc_dialog():
            if ecc_participant_yes.isChecked():
                ecc_participant_no.setChecked(False)
                ecc_info_input.show()
            else:
                ecc_info_input.hide()
                ecc_info_input.clear()
        def toggle_ecc_no():
            if ecc_participant_no.isChecked():
                ecc_participant_yes.setChecked(False)
                ecc_info_input.hide()
                ecc_info_input.clear()
        ecc_participant_yes.clicked.connect(toggle_ecc_dialog)
        ecc_participant_no.clicked.connect(toggle_ecc_no)
        restrictions_yes = QCheckBox("Sim"); restrictions_no = QCheckBox("Não")
        restrictions_yes.setChecked(participant['has_restrictions']); restrictions_no.setChecked(not participant['has_restrictions'])
        restrictions_yes.clicked.connect(lambda: restrictions_no.setChecked(False))
        restrictions_no.clicked.connect(lambda: restrictions_yes.setChecked(False))
        restrictions_widget = QWidget(); restrictions_layout = QHBoxLayout(restrictions_widget)
        restrictions_layout.addWidget(QLabel("Possui restrições alimentares ou alergias:")); restrictions_layout.addWidget(restrictions_yes); restrictions_layout.addWidget(restrictions_no)
        form_layout.addWidget(restrictions_widget, 18, 0, 1, 2)
        restrictions_info_input = QLineEdit(participant['restrictions_info'] or '')
        form_layout.addWidget(QLabel("Detalhes sobre restrições:"), 19, 0); form_layout.addWidget(restrictions_info_input, 19, 1)
        restrictions_info_input.setVisible(participant['has_restrictions'])
        restrictions_yes.clicked.connect(lambda: restrictions_info_input.setVisible(True))
        restrictions_no.clicked.connect(lambda: restrictions_info_input.setVisible(False))
        observations_input = QTextEdit(participant['observations'] or '')
        form_layout.addWidget(QLabel("Observações:"), 20, 0); form_layout.addWidget(observations_input, 20, 1)
        
        # Widget de foto com preview
        photo_label = QLabel("Foto:")
        form_layout.addWidget(photo_label, 21, 0)
        
        photo_container = QWidget()
        photo_container_layout = QVBoxLayout(photo_container)
        photo_container_layout.setSpacing(10)
        
        # Preview da foto atual
        photo_preview = QLabel()
        photo_preview.setFixedSize(150, 150)
        photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_preview.setStyleSheet("border: 2px solid #dee2e6; border-radius: 8px; background-color: #f8f9fa;")
        
        if participant['photo_path']:
            try:
                pixmap = QPixmap(participant['photo_path'])
                if not pixmap.isNull():
                    photo_preview.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    photo_preview.setText("Foto não\nencontrada")
                    photo_preview.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 8px; color: #6c757d;")
            except Exception as e:
                photo_preview.setText(f"Erro ao\ncarregar")
                photo_preview.setStyleSheet("border: 2px dashed #dc3545; border-radius: 8px; color: #dc3545;")
        else:
            photo_preview.setText("Nenhuma foto\ncarregada")
            photo_preview.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 8px; color: #6c757d;")
        
        photo_container_layout.addWidget(photo_preview)
        
        # Widget para trocar foto
        photo_widget = PhotoWidget(self.photos_dir)
        photo_widget.set_photo_path(participant['photo_path'])
        
        # Função para atualizar preview quando foto mudar
        def update_photo_preview():
            photo_path = photo_widget.get_photo_path()
            if photo_path:
                try:
                    pixmap = QPixmap(photo_path)
                    if not pixmap.isNull():
                        photo_preview.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        photo_preview.setStyleSheet("border: 2px solid #28a745; border-radius: 8px; background-color: #f8f9fa;")
                    else:
                        photo_preview.setText("Foto inválida")
                        photo_preview.setStyleSheet("border: 2px dashed #dc3545; border-radius: 8px; color: #dc3545;")
                except Exception as e:
                    photo_preview.setText(f"Erro:\n{str(e)[:20]}")
                    photo_preview.setStyleSheet("border: 2px dashed #dc3545; border-radius: 8px; color: #dc3545;")
            else:
                photo_preview.setText("Nenhuma foto\ncarregada")
                photo_preview.setStyleSheet("border: 2px dashed #dee2e6; border-radius: 8px; color: #6c757d;")
        
        # Timer para atualizar preview periodicamente (quando foto muda)
        update_timer = QTimer()
        update_timer.timeout.connect(update_photo_preview)
        update_timer.start(500)  # Verifica a cada 500ms
        
        photo_container_layout.addWidget(photo_widget)
        form_layout.addWidget(photo_container, 21, 1)
        scroll.setWidget(form_widget); layout.addWidget(scroll)
        buttons = QHBoxLayout()
        save_button = QPushButton("Salvar"); save_button.setObjectName("btnSuccess")
        cancel_button = QPushButton("Cancelar"); cancel_button.setObjectName("btnDanger")
        buttons.addWidget(save_button); buttons.addWidget(cancel_button)
        layout.addLayout(buttons); dialog.setLayout(layout)
        def save_changes():
            sacraments_data = []
            for sacrament, checkboxes in sacrament_options.items():
                selected = next((cb.text() for cb in checkboxes if cb.isChecked()), "Não Informado")
                sacraments_data.append(f"{sacrament}:{selected}")
            self.save_edited_participant(
                participant,
                name_input.text(), common_name_input.text(), birth_date_input.get_iso_date(), instagram_input.text(),
                address_input.text(), neighborhood_input.text(), email_input.text(), phone_input.text(), ','.join(sacraments_data),
                church_movement_input.text(), father_name_input.text(), father_contact_input.text(), mother_name_input.text(),
                mother_contact_input.text(), ecc_participant_yes.isChecked(), ecc_info_input.text(), restrictions_yes.isChecked(),
                restrictions_info_input.text(), observations_input.toPlainText(), photo_widget.get_photo_path(), dialog
            )
        save_button.clicked.connect(save_changes); cancel_button.clicked.connect(dialog.reject)
        if dialog.exec():
            pass

    def save_edited_participant(self, participant, name, common_name, birth_date, instagram, address, neighborhood, email, phone, sacraments, church_movement, father_name, father_contact, mother_name, mother_contact, ecc_participant, ecc_info, has_restrictions, restrictions_info, observations, photo_path, dialog):
        """Salva alterações de um participante editado"""
        # Validar dados
        participant_data = {
            'name': name.strip(),
            'common_name': common_name.strip(),
            'birth_date': birth_date,
            'instagram': instagram.strip(),
            'father_contact': father_contact.strip(),
            'mother_contact': mother_contact.strip(),
            'email': email.strip(),
            'phone': phone.strip()
        }
        
        is_valid, error_message = validate_participant_data(participant_data)
        if not is_valid:
            QMessageBox.warning(dialog, "Validação", error_message)
            log_warning(f"Tentativa de edição com dados inválidos: {error_message}")
            return
        
        # Feedback visual
        self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            conn = self.get_db_connection()
            if not conn:
                QMessageBox.critical(dialog, "Erro de Conexão", 
                                   "Não foi possível conectar ao banco de dados.")
                log_error(Exception("Falha na conexão com banco de dados"), "save_edited_participant")
                return
            
            try:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    UPDATE participants
                    SET name = ?, common_name = ?, birth_date = ?, instagram = ?, address = ?, 
                        neighborhood = ?, email = ?, phone = ?, sacraments = ?, 
                        church_movement = ?, father_name = ?, father_contact = ?, mother_name = ?, 
                        mother_contact = ?, ecc_participant = ?, ecc_info = ?, has_restrictions = ?, 
                        restrictions_info = ?, observations = ?, photo_path = ?
                    WHERE id = ?
                    ''', (
                        name, common_name, birth_date, instagram, address, neighborhood, email, phone, sacraments, church_movement,
                        father_name, father_contact, mother_name, mother_contact, ecc_participant, ecc_info, has_restrictions,
                        restrictions_info, observations, photo_path, participant['id']
                    )
                )
                conn.commit()
                log_info(f"Participante atualizado: ID {participant['id']}, Nome: {name}")
                
                # Criar backup automático após edição bem-sucedida
                try:
                    self.backup_manager.create_backup(prefix="post_edit")
                except Exception as backup_error:
                    log_error(backup_error, "Erro ao criar backup após edição")
                
                QMessageBox.information(dialog, "Sucesso", "Participante atualizado com sucesso!")
                self.load_participants()
                dialog.accept()
            except Exception as db_error:
                conn.rollback()
                log_error(db_error, f"save_edited_participant - Erro ao atualizar ID {participant['id']}")
                QMessageBox.critical(dialog, "Erro de Banco de Dados", 
                                   f"Erro ao atualizar dados: {str(db_error)}\n\n"
                                   "As alterações não foram salvas. Verifique os logs para mais detalhes.")
            finally:
                conn.close()
        finally:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def delete_participant(self, participant):
        """Exclui um participante com confirmação"""
        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Tem certeza que deseja excluir {participant['name']}?\n\n"
            "Esta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Feedback visual
            self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
            try:
                conn = self.get_db_connection()
                if not conn:
                    QMessageBox.critical(self, "Erro de Conexão", 
                                       "Não foi possível conectar ao banco de dados.")
                    log_error(Exception("Falha na conexão com banco de dados"), "delete_participant")
                    return
                try:
                    cursor = conn.cursor()
                    # Criar backup antes de excluir
                    try:
                        self.backup_manager.create_backup(prefix="pre_delete")
                    except Exception as backup_error:
                        log_error(backup_error, "Erro ao criar backup antes de exclusão")
                    
                    cursor.execute("DELETE FROM participants WHERE id = ?", (participant['id'],))
                    conn.commit()
                    log_info(f"Participante excluído: ID {participant['id']}, Nome: {participant['name']}")
                    QMessageBox.information(self, "Sucesso", "Participante excluído com sucesso!")
                    self.load_participants()
                except Exception as e:
                    conn.rollback()
                    log_error(e, f"delete_participant - Erro ao excluir ID {participant['id']}")
                    QMessageBox.critical(self, "Erro de Banco de Dados", 
                                       f"Erro ao excluir dados: {str(e)}\n\n"
                                       "Verifique os logs para mais detalhes.")
                finally:
                    conn.close()
            finally:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def generate_individual_pdf(self):
        """Gera PDF individual de um participante"""
        if not self.participant_table.rowCount():
            QMessageBox.warning(self, "Aviso", "Não há participantes registrados.")
            return
        participant_names = []
        participant_ids = []
        conn = self.get_db_connection()
        if not conn:
            QMessageBox.critical(self, "Erro de Conexão", 
                               "Não foi possível conectar ao banco de dados.")
            log_error(Exception("Falha na conexão com banco de dados"), "generate_individual_pdf")
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM participants ORDER BY name")
            participants = cursor.fetchall()
            for p in participants:
                participant_names.append(p['name'])
                participant_ids.append(p['id'])
        except Exception as e:
            log_error(e, "generate_individual_pdf - Erro ao buscar participantes")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar lista de participantes: {str(e)}")
            return
        finally:
            conn.close()
            
        participant_name, ok = QInputDialog.getItem(
            self, "Selecionar Participante", "Escolha o participante:", participant_names, 0, False
        )
        if not ok or not participant_name:
            return
        participant_id = None
        for i, name in enumerate(participant_names):
            if name == participant_name:
                participant_id = participant_ids[i]
                break
        if participant_id is None:
            QMessageBox.warning(self, "Erro", "Participante não encontrado.")
            log_warning(f"Participante não encontrado: {participant_name}")
            return
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF", str(self.data_dir / f"{participant_name}_ficha.pdf"), "PDF Files (*.pdf)"
        )
        if not file_name:
            return
        
        # Feedback visual
        self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            pdf_generator = PDFGenerator(db_path=self.db_path, photos_dir=self.photos_dir, logo_path=self.logo_path)
            success = pdf_generator.generate_individual_pdf(participant_id, file_name)
            if success:
                log_info(f"PDF individual gerado: {file_name} para participante ID {participant_id}")
                QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso!\n\n{file_name}")
            else:
                log_warning(f"Falha ao gerar PDF individual para participante ID {participant_id}")
                QMessageBox.critical(self, "Erro", "Ocorreu um erro ao gerar o PDF.\n\nVerifique os logs para mais detalhes.")
        except Exception as e:
            log_error(e, f"generate_individual_pdf - Erro ao gerar PDF para ID {participant_id}")
            QMessageBox.critical(self, "Erro", f"Erro inesperado ao gerar PDF:\n{str(e)}\n\nVerifique os logs para mais detalhes.")
        finally:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def generate_complete_pdf(self):
        """Gera PDF completo com todos os participantes"""
        if not self.participant_table.rowCount():
            QMessageBox.warning(self, "Aviso", "Não há participantes registrados.")
            return
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Salvar PDF Completo", str(self.data_dir / "fichas_completas.pdf"), "PDF Files (*.pdf)"
        )
        if not file_name:
            return
        
        # Feedback visual
        self.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        try:
            pdf_generator = PDFGenerator(db_path=self.db_path, photos_dir=self.photos_dir, logo_path=self.logo_path)
            success = pdf_generator.generate_complete_pdf(file_name)
            if success:
                log_info(f"PDF completo gerado: {file_name}")
                QMessageBox.information(self, "Sucesso", f"PDF completo gerado com sucesso!\n\n{file_name}")
            else:
                log_warning("Falha ao gerar PDF completo")
                QMessageBox.critical(self, "Erro", "Ocorreu um erro ao gerar o PDF completo.\n\nVerifique os logs para mais detalhes.")
        except Exception as e:
            log_error(e, "generate_complete_pdf - Erro ao gerar PDF completo")
            QMessageBox.critical(self, "Erro", f"Erro inesperado ao gerar PDF completo:\n{str(e)}\n\nVerifique os logs para mais detalhes.")
        finally:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def upload_logo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Selecionar Logo", "", "Imagens (*.png *.jpg *.jpeg)")
        if file_name:
            try:
                img = Image.open(file_name); img.verify()
                self.logo_path = file_name
                pixmap = QPixmap(file_name)
                self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                QMessageBox.information(self, "Sucesso", "Logo carregado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao processar a imagem: {e}")

    def toggle_church_movement(self):
        sender = self.sender()
        if sender == self.church_movement_yes:
            if self.church_movement_yes.isChecked():
                self.church_movement_no.setChecked(False)
                self.church_movement_input.show()
            else:
                # Desmarcou o "Sim": esconder e limpar os detalhes
                self.church_movement_input.hide()
                self.church_movement_input.clear()
        elif sender == self.church_movement_no:
            if self.church_movement_no.isChecked():
                self.church_movement_yes.setChecked(False)
                self.church_movement_input.hide()
                self.church_movement_input.clear()

    def toggle_ecc_participant(self):
        sender = self.sender()
        if sender == self.ecc_participant_yes:
            if self.ecc_participant_yes.isChecked():
                self.ecc_participant_no.setChecked(False)
                self.ecc_info_input.show()
            else:
                # Desmarcou o "Sim": esconder e limpar os detalhes
                self.ecc_info_input.hide()
                self.ecc_info_input.clear()
        elif sender == self.ecc_participant_no:
            if self.ecc_participant_no.isChecked():
                self.ecc_participant_yes.setChecked(False)
                self.ecc_info_input.hide()
                self.ecc_info_input.clear()

    def toggle_restrictions(self):
        sender = self.sender()
        if sender == self.restrictions_yes:
            if self.restrictions_yes.isChecked():
                self.restrictions_no.setChecked(False)
                self.restrictions_info_input.show()
            else:
                # Desmarcou o "Sim": esconder e limpar os detalhes
                self.restrictions_info_input.hide()
                self.restrictions_info_input.clear()
        elif sender == self.restrictions_no:
            if self.restrictions_no.isChecked():
                self.restrictions_yes.setChecked(False)
                self.restrictions_info_input.hide()
                self.restrictions_info_input.clear()

    def handle_sacrament_checkbox(self, checkbox: QCheckBox, checkboxes: list):
        """Gerencia o comportamento dos checkboxes de sacramento, permitindo desmarcar"""
        # Se o checkbox foi marcado, desmarca todos os outros do mesmo grupo
        if checkbox.isChecked():
            for cb in checkboxes:
                if cb != checkbox:
                    cb.blockSignals(True)  # Bloqueia sinais para evitar loop infinito
                    cb.setChecked(False)
                    cb.blockSignals(False)
        # Se foi desmarcado, não faz nada - permite ficar sem seleção

