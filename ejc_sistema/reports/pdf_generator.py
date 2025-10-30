"""Geração de PDFs para o sistema EJC"""
import datetime
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib.colors import HexColor, black, white
import sqlite3


class PDFGenerator:
    """Classe responsável pela geração de PDFs"""
    
    def __init__(self, db_path, photos_dir, logo_path=None):
        self.db_path = db_path
        self.photos_dir = photos_dir
        self.logo_path = logo_path
        
    def get_db_connection(self):
        """Obtém conexão com o banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
            
    def format_date(self, date_str):
        """Formata a data do formato ISO para o formato brasileiro"""
        if not date_str:
            return ""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            return date_str
            
    def generate_individual_pdf(self, participant_id, output_path):
        """Gera um PDF individual para um participante específico"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
            participant = cursor.fetchone()
            
            if not participant:
                print("Participante não encontrado.")
                return False
                
            # Criar o PDF
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            # Configurações iniciais
            c.setTitle(f"Ficha de Inscrição - {participant['name']}")
            
            # Adicionar cabeçalho com logo e foto do participante
            self._add_header(c, width, height, participant['photo_path'])
            
            # Posição inicial após o cabeçalho
            y_position = height - 100  # Ajustado para começar após o cabeçalho
            
            # Seções do formulário
            y_position = self._add_personal_info_section(c, participant, width, y_position)
            y_position = self._add_sacraments_section(c, participant, width, y_position)
            y_position = self._add_church_movements_section(c, participant, width, y_position)
            y_position = self._add_family_info_section(c, participant, width, y_position)
            y_position = self._add_ecc_section(c, participant, width, y_position)
            y_position = self._add_restrictions_section(c, participant, width, y_position)
            
            # Adicionar área de assinatura
            self._add_signature_area(c, width, y_position)
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return False
        finally:
            conn.close()
    
    def generate_complete_pdf(self, output_path):
        """Gera um PDF com todos os participantes"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM participants ORDER BY name")
            participants = cursor.fetchall()
            
            if not participants:
                print("Nenhum participante encontrado.")
                return False
                
            # Criar o PDF
            c = canvas.Canvas(output_path, pagesize=A4)
            
            for i, participant in enumerate(participants):
                # Gerar página para cada participante
                if i > 0:
                    c.showPage()  # Nova página para cada participante
                
                # Gerar conteúdo para este participante
                self._generate_participant_page(c, participant['id'])
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Erro ao gerar PDF completo: {e}")
            return False
        finally:
            conn.close()
    
    def _generate_participant_page(self, c, participant_id):
        """Gera uma página para um participante específico"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
            participant = cursor.fetchone()
            
            if not participant:
                return
                
            width, height = A4
            
            # Adicionar cabeçalho com logo e foto do participante
            self._add_header(c, width, height, participant['photo_path'])
            
            # Posição inicial após o cabeçalho
            y_position = height - 100  # Ajustado para começar após o cabeçalho
            
            # Seções do formulário
            y_position = self._add_personal_info_section(c, participant, width, y_position)
            y_position = self._add_sacraments_section(c, participant, width, y_position)
            y_position = self._add_church_movements_section(c, participant, width, y_position)
            y_position = self._add_family_info_section(c, participant, width, y_position)
            y_position = self._add_ecc_section(c, participant, width, y_position)
            y_position = self._add_restrictions_section(c, participant, width, y_position)
            
            # Adicionar área de assinatura
            self._add_signature_area(c, width, y_position)
            
        except Exception as e:
            print(f"Erro ao gerar página para participante {participant_id}: {e}")
        finally:
            conn.close()
    
    def _add_header(self, c, width, height, participant_photo_path=None):
        """Adiciona o cabeçalho ao PDF com fundo preto, logo à esquerda e foto à direita"""
        # Desenhar retângulo de fundo preto para o cabeçalho
        c.setFillColor(HexColor('#000000'))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        # Resetar cor para texto
        c.setFillColor(white)
        
        # Título centralizado em branco
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 45, "Ficha de Inscrição EJC")
        
        # Adicionar logo se disponível (à esquerda)
        if self.logo_path and Path(self.logo_path).exists():
            try:
                c.drawImage(
                    str(self.logo_path),
                    20,  # Posição X (esquerda)
                    height - 75,  # Posição Y (topo)
                    width=70,
                    height=70,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                print(f"Logo adicionado: {self.logo_path}")
            except Exception as e:
                print(f"Erro ao processar logo para PDF: {e}")
        else:
            print(f"Logo não encontrado ou não configurado: {self.logo_path}")
        
        # Adicionar foto do participante (à direita)
        if participant_photo_path and Path(participant_photo_path).exists():
            try:
                c.drawImage(
                    str(participant_photo_path),
                    width - 90,  # Posição X (direita)
                    height - 75,  # Posição Y (topo)
                    width=70,
                    height=70,
                    preserveAspectRatio=True,
                    mask='auto'
                )
                print(f"Foto adicionada: {participant_photo_path}")
            except Exception as e:
                print(f"Erro ao processar foto do participante para o cabeçalho: {e}")
        else:
            print(f"Foto não encontrada: {participant_photo_path}")
        
        # Resetar cor de preenchimento para o restante do documento
        c.setFillColor(black)
    
    def _add_personal_info_section(self, c, participant, width, y_position):
        """Adiciona a seção de informações pessoais"""
        # Título da seção
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Informações Pessoais")
        
        # Dados para a tabela
        data = [
            ["Nome Completo", participant['name'] or ""],
            ["Nome Usual", participant['common_name'] or ""],
            ["Data de Nascimento", self.format_date(participant['birth_date'])],
            ["Instagram", participant['instagram'] or ""],
            ["Endereço", participant['address'] or ""],
            ["Bairro/Comunidade", participant['neighborhood'] or ""],
            ["Email", participant['email'] or ""],
            ["Celular", participant['phone'] or ""]
        ]
        
        # Criar e desenhar a tabela
        y_position -= 10
        table = Table(data, colWidths=[120, width - 160])
        table.setStyle(self._get_table_style())
        table.wrapOn(c, width - 60, 400)
        table_height = len(data) * 20  # Altura aproximada baseada no número de linhas
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20  # Retorna a nova posição Y
    
    def _add_sacraments_section(self, c, participant, width, y_position):
        """Adiciona a seção de sacramentos"""
        # Título da seção
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Sacramentos")
        
        # Processar dados dos sacramentos
        sacraments = participant['sacraments'].split(',') if participant['sacraments'] else []
        sacrament_data = []
        
        for sacrament_name in ["Batismo", "Primeira Eucaristia", "Crisma"]:
            status = "Não Informado"
            for s in sacraments:
                if s.startswith(f"{sacrament_name}:"):
                    status = s.split(':')[1].strip()
                    break
            sacrament_data.append([sacrament_name, status])
        
        # Criar e desenhar a tabela
        y_position -= 10
        table = Table(sacrament_data, colWidths=[120, width - 160])
        table.setStyle(self._get_table_style())
        table.wrapOn(c, width - 60, 400)
        table_height = len(sacrament_data) * 20
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_church_movements_section(self, c, participant, width, y_position):
        """Adiciona a seção de movimentos da igreja"""
        # Título da seção
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Movimentos da Igreja")
        
        # Dados para a tabela
        data = [
            ["Participa de algum movimento da igreja? Se sim, qual?"],
            [participant['church_movement'] or ""]
        ]
        
        # Criar e desenhar a tabela
        y_position -= 10
        table = Table(data, colWidths=[width - 60])
        table.setStyle(self._get_table_style())
        table.wrapOn(c, width - 60, 400)
        table_height = len(data) * 20
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_family_info_section(self, c, participant, width, y_position):
        """Adiciona a seção de informações familiares"""
        # Título da seção
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Informações Familiares")
        
        # Dados para a tabela
        data = [
            ["Nome do Pai", "Contato"],
            [participant['father_name'] or "", participant['father_contact'] or ""],
            ["Nome da Mãe", "Contato"],
            [participant['mother_name'] or "", participant['mother_contact'] or ""]
        ]
        
        # Criar e desenhar a tabela
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.3])
        
        # Estilo específico para esta tabela
        style = self._get_table_style()
        style.add('BACKGROUND', (0, 0), (1, 0), HexColor('#f2f2f2'))
        style.add('BACKGROUND', (0, 2), (1, 2), HexColor('#f2f2f2'))
        style.add('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold')
        style.add('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold')
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = len(data) * 20
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_ecc_section(self, c, participant, width, y_position):
        """Adiciona a seção de informações do ECC"""
        # Título da seção
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Informações do ECC")
        
        # Dados para a tabela
        data = [
            ["Seus pais são encontristas do ECC?", "SIM", "NÃO"],
            ["", "X" if participant['ecc_participant'] else "", "X" if not participant['ecc_participant'] else ""]
        ]
        
        if participant['ecc_info']:
            data.append(["Informações ECC:", participant['ecc_info'], ""])
        
        # Criar e desenhar a tabela
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.15, (width - 60) * 0.15])
        
        # Estilo específico para esta tabela
        style = self._get_table_style()
        style.add('ALIGN', (1, 0), (2, -1), 'CENTER')
        style.add('SPAN', (0, 0), (0, 1))
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = len(data) * 20
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_restrictions_section(self, c, participant, width, y_position):
        """Adiciona a seção de restrições e alergias"""
        # Título da seção
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Restrições e Alergias")
        
        # Dados para a tabela
        data = [
            ["Possui alguma restrição alimentar ou alergia?", "SIM", "NÃO"],
            ["", "X" if participant['has_restrictions'] else "", "X" if not participant['has_restrictions'] else ""]
        ]
        
        if participant['has_restrictions'] and participant['restrictions_info']:
            data.append(["Quais restrições?", participant['restrictions_info'], ""])
        
        # Criar e desenhar a tabela
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.15, (width - 60) * 0.15])
        
        # Estilo específico para esta tabela
        style = self._get_table_style()
        style.add('ALIGN', (1, 0), (2, -1), 'CENTER')
        style.add('SPAN', (0, 0), (0, 1))
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = len(data) * 20
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_signature_area(self, c, width, y_position):
        """Adiciona a área de assinatura"""
        if y_position < 50:  # Se não houver espaço suficiente, criar nova página
            c.showPage()
            y_position = A4[1] - 50
        
        y_position -= 30
        
        # Configurar fonte
        c.setFont("Helvetica", 10)
        
        # Calcular posições para alinhar horizontalmente
        signature_x = 30
        date_x = width/2 + 30
        
        # Desenhar linhas para assinatura e data com a mesma altura
        line_height = 20  # Altura fixa para as linhas
        c.drawString(signature_x, y_position - line_height, "_" * 40)  # Linha para assinatura
        c.drawString(date_x, y_position - line_height, "_" * 7 + " / " + "_" * 7 + " / " + "_" * 7)  # Linha para data com barras
        
        # Adicionar textos abaixo das linhas
        c.drawString(signature_x, y_position - line_height - 15, "Assinatura")
        c.drawString(date_x, y_position - line_height - 15, "Data")
    
    def _get_table_style(self):
        """Retorna o estilo padrão para tabelas"""
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('BOX', (0, 0), (-1, -1), 1, black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])

