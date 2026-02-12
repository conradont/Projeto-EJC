"""Serviço para geração de PDFs"""
import datetime
import tempfile
import urllib.request
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from sqlalchemy.orm import Session
from typing import Optional
from config import settings
from database import crud


class PDFService:
    """Classe responsável pela geração de PDFs"""
    
    def __init__(self, db: Session):
        self.db = db
        # Criar estilo de parágrafo para quebra de texto
        self.paragraph_style = ParagraphStyle(
            'Custom',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=12,
            alignment=0,  # LEFT
        )
    
    def _resolve_image_to_path(self, path_or_url: Optional[str]) -> Optional[Path]:
        """Converte path ou URL em Path local. URL = baixa para temp; path Supabase = signed URL depois baixa."""
        if not path_or_url or not str(path_or_url).strip():
            return None
        s = str(path_or_url).strip()
        if s.startswith("http://") or s.startswith("https://"):
            return self._download_url_to_temp(s)
        try:
            from services.storage_service import use_supabase_storage, get_signed_url, BUCKET_PHOTOS
            if use_supabase_storage():
                signed_url = get_signed_url(BUCKET_PHOTOS, s)
                if signed_url:
                    return self._download_url_to_temp(signed_url)
        except Exception as e:
            print(f"⚠ Erro ao obter signed URL para foto ({s}): {e}")
        if Path(s).is_absolute():
            p = Path(s)
        else:
            p = settings.PHOTOS_DIR / s
            if not p.exists():
                p = settings.PHOTOS_DIR / Path(s).name
            if not p.exists():
                p = settings.LOGO_DIR / s
            if not p.exists():
                p = settings.LOGO_DIR / Path(s).name
        return p if p.exists() else None

    def _download_url_to_temp(self, url: str) -> Optional[Path]:
        """Baixa uma URL para arquivo temporário e retorna o Path."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EJC-API/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            suffix = Path(url).suffix or ".png"
            if suffix not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                suffix = ".png"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(data)
            tmp.close()
            return Path(tmp.name)
        except Exception as e:
            print(f"⚠ Erro ao baixar imagem de URL: {e}")
            return None

    def _get_logo_path(self) -> Optional[Path]:
        """Busca a logo: Supabase = path no banco → signed URL → download; senão diretório local."""
        try:
            from services.storage_service import (
                use_supabase_storage,
                get_logo_path_from_db,
                get_signed_url,
                BUCKET_LOGO,
            )
            if use_supabase_storage():
                logo_path = get_logo_path_from_db(self.db)
                if logo_path:
                    signed_url = get_signed_url(BUCKET_LOGO, logo_path)
                    if signed_url:
                        return self._resolve_image_to_path(signed_url)
        except Exception as e:
            print(f"⚠ Erro ao obter logo do banco: {e}")
        logo_dir = settings.DATA_DIR / "logo"
        if not logo_dir.exists():
            return None
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']
        for logo_file in logo_dir.glob("*"):
            if logo_file.suffix.lower() in image_extensions and logo_file.exists():
                return logo_file
        return None
    
    def _wrap_text(self, text, max_width):
        """Envolve texto longo usando Paragraph para quebra automática"""
        if not text:
            return ""
        # Escapar caracteres especiais para XML/HTML
        text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        para = Paragraph(text, self.paragraph_style)
        return para
    
    def _draw_table_with_height(self, c, table, x, y, width):
        """Desenha uma tabela e retorna sua altura real após wrapOn"""
        table.wrapOn(c, width, 400)
        table.drawOn(c, x, y)
        return table._height
    
    def _check_page_break(self, c, y_position, threshold=100):
        """Verifica se precisa quebrar página e retorna nova y_position"""
        if y_position < threshold:
            c.showPage()
            return A4[1] - 50
        return y_position
    
    def generate_individual_pdf(self, participant_id: int) -> Optional[Path]:
        """Gera um PDF individual para um participante específico"""
        participant = crud.get_participant(self.db, participant_id)
        if not participant:
            return None
        
        # Log para debug - verificar dados do participante
        print(f"🔍 Debug - Dados do Participante ID {participant_id}:")
        print(f"   Nome: {participant.name}")
        print(f"   Data Nascimento: {participant.birth_date} (tipo: {type(participant.birth_date)})")
        print(f"   Email: {participant.email} (tipo: {type(participant.email)})")
        print(f"   Telefone: {participant.phone} (tipo: {type(participant.phone)})")
        print(f"   Contato Pai: {participant.father_contact} (tipo: {type(participant.father_contact)})")
        print(f"   Contato Mãe: {participant.mother_contact} (tipo: {type(participant.mother_contact)})")
        
        # Criar nome do arquivo
        filename = f"ficha_{participant.id}_{participant.name.replace(' ', '_')}.pdf"
        pdf_path = settings.PDFS_DIR / filename
        
        try:
            # Criar o PDF
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            width, height = A4
            
            # Configurações iniciais
            c.setTitle(f"Ficha de Inscrição - {participant.name}")
            
            # Adicionar cabeçalho
            self._add_header(c, width, height, participant.photo_path)
            
            # Posição inicial após o cabeçalho
            y_position = height - 100
            
            # Seções do formulário
            y_position = self._add_personal_info_section(c, participant, width, y_position)
            y_position = self._add_sacraments_section(c, participant, width, y_position)
            y_position = self._add_church_movements_section(c, participant, width, y_position)
            y_position = self._add_family_info_section(c, participant, width, y_position)
            y_position = self._add_ecc_section(c, participant, width, y_position)
            y_position = self._add_restrictions_section(c, participant, width, y_position)
            
            # Adicionar seção de observações se houver
            if participant.observations:
                y_position = self._add_observations_section(c, participant, width, y_position)
            
            # Adicionar área de assinatura
            self._add_signature_area(c, width, y_position)
            
            c.save()
            return pdf_path
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_complete_pdf(self) -> Optional[Path]:
        """Gera um PDF com todos os participantes"""
        participants = crud.get_participants(self.db, skip=0, limit=1000)
        
        if not participants:
            return None
        
        # Criar nome do arquivo
        pdf_path = settings.PDFS_DIR / f"fichas_completas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            # Criar o PDF
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            
            for i, participant in enumerate(participants):
                if i > 0:
                    c.showPage()
                
                width, height = A4
                
                # Adicionar cabeçalho
                self._add_header(c, width, height, participant.photo_path)
                
                # Posição inicial após o cabeçalho
                y_position = height - 100
                
                # Seções do formulário
                y_position = self._add_personal_info_section(c, participant, width, y_position)
                y_position = self._add_sacraments_section(c, participant, width, y_position)
                y_position = self._add_church_movements_section(c, participant, width, y_position)
                y_position = self._add_family_info_section(c, participant, width, y_position)
                y_position = self._add_ecc_section(c, participant, width, y_position)
                y_position = self._add_restrictions_section(c, participant, width, y_position)
                
                # Adicionar seção de observações se houver
                if participant.observations:
                    y_position = self._add_observations_section(c, participant, width, y_position)
                
                # Adicionar área de assinatura
                self._add_signature_area(c, width, y_position)
            
            c.save()
            return pdf_path
            
        except Exception as e:
            print(f"Erro ao gerar PDF completo: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_header(self, c, width, height, participant_photo_path=None):
        """Adiciona o cabeçalho ao PDF"""
        # Desenhar retângulo de fundo preto para o cabeçalho
        c.setFillColor(HexColor('#000000'))
        c.rect(0, height - 80, width, 80, fill=True, stroke=False)
        
        # Resetar cor para texto
        c.setFillColor(white)
        
        # Adicionar foto do participante (à esquerda)
        photo_x_position = 20  # Posição X para a foto (à esquerda)
        photo_width = 70
        photo_height = 70
        photo_full_path = None
        photo_exists = False
        
        if participant_photo_path:
            photo_full_path = self._resolve_image_to_path(participant_photo_path)
            if photo_full_path and photo_full_path.exists():
                try:
                    from PIL import Image
                    img_valid = True
                    try:
                        img = Image.open(photo_full_path)
                        img.verify()
                        img.close()
                    except Exception as img_error:
                        print(f"⚠ Foto inválida ou corrompida: {photo_full_path} - {img_error}")
                        img_valid = False
                    
                    if img_valid:
                        try:
                            c.drawImage(
                                str(photo_full_path),
                                photo_x_position,
                                height - 75,
                                width=photo_width,
                                height=photo_height,
                                preserveAspectRatio=True,
                                mask='auto'
                            )
                            photo_exists = True
                            print(f"✓ Foto adicionada ao PDF: {photo_full_path}")
                        except Exception as draw_error:
                            print(f"✗ Erro ao desenhar foto no PDF ({photo_full_path}): {draw_error}")
                            import traceback
                            traceback.print_exc()
                except Exception as e:
                    print(f"✗ Erro ao processar foto do participante ({photo_full_path}): {e}")
                    import traceback
                    traceback.print_exc()
        
        # Título centralizado em branco
        title_x = width / 2
        if participant_photo_path and photo_full_path and photo_full_path.exists():
            title_x = (width + photo_x_position + photo_width) / 2
        
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(title_x, height - 45, "Ficha de Inscrição EJC")
        
        # Adicionar logo se disponível (à direita)
        logo_path = self._get_logo_path()
        if logo_path and logo_path.exists():
            print(f"🔍 Logo encontrada: {logo_path}")
            try:
                from PIL import Image
                img_valid = True
                try:
                    img = Image.open(logo_path)
                    img.verify()
                    img.close()
                except Exception as img_error:
                    print(f"⚠ Logo inválida ou corrompida: {logo_path} - {img_error}")
                    img_valid = False
                
                if img_valid:
                    try:
                        c.drawImage(
                            str(logo_path),
                            width - 90,
                            height - 75,
                            width=70,
                            height=70,
                            preserveAspectRatio=True,
                            mask='auto'
                        )
                        print(f"✓ Logo adicionada ao PDF: {logo_path}")
                    except Exception as draw_error:
                        print(f"✗ Erro ao desenhar logo no PDF ({logo_path}): {draw_error}")
                        import traceback
                        traceback.print_exc()
            except Exception as e:
                print(f"✗ Erro ao processar logo: {e}")
                import traceback
                traceback.print_exc()
        
        # Resetar cor de preenchimento
        c.setFillColor(black)
    
    def _add_personal_info_section(self, c, participant, width, y_position):
        """Adiciona a seção de informações pessoais"""
        y_position = self._check_page_break(c, y_position)
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Informações Pessoais")
        
        # Função auxiliar para converter valores para string de forma segura
        def safe_str(value):
            if value is None:
                return ""
            value_str = str(value).strip()
            if value_str == "None" or value_str == "":
                return ""
            return value_str
        
        # Converter valores para string e garantir que não sejam None
        birth_date_raw = getattr(participant, 'birth_date', None)
        email_raw = getattr(participant, 'email', None)
        phone_raw = getattr(participant, 'phone', None)
        
        birth_date_str = safe_str(birth_date_raw)
        email_str = safe_str(email_raw)
        phone_str = safe_str(phone_raw)
        
        # Log para debug
        print(f"🔍 Debug - Informações Pessoais (processando):")
        print(f"   birth_date raw: {repr(birth_date_raw)} -> formatted: {repr(self._format_date(birth_date_str))}")
        print(f"   email raw: {repr(email_raw)} -> final: {repr(email_str)}")
        print(f"   phone raw: {repr(phone_raw)} -> final: {repr(phone_str)}")
        
        # Usar Paragraph para campos que podem ser longos
        data = [
            ["Nome Completo", safe_str(getattr(participant, 'name', None))],
            ["Nome Usual", safe_str(getattr(participant, 'common_name', None))],
            ["Data de Nascimento", self._format_date(birth_date_str)],
            ["Instagram", safe_str(getattr(participant, 'instagram', None))],
            ["Endereço", self._wrap_text(safe_str(getattr(participant, 'address', None)), width - 160)],
            ["Bairro/Comunidade", safe_str(getattr(participant, 'neighborhood', None))],
            ["Email", email_str],
            ["Celular", phone_str]
        ]
        
        # Log final dos dados que serão exibidos
        print(f"🔍 Debug - Dados finais da tabela:")
        for row in data:
            print(f"   {row[0]}: {repr(row[1])}")
        
        y_position -= 10
        table = Table(data, colWidths=[120, width - 160])
        table.setStyle(self._get_table_style())
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_sacraments_section(self, c, participant, width, y_position):
        """Adiciona a seção de sacramentos"""
        y_position = self._check_page_break(c, y_position)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Sacramentos")
        
        sacraments = participant.sacraments.split(',') if participant.sacraments else []
        sacrament_data = []
        
        for sacrament_name in ["Batismo", "Primeira Eucaristia", "Crisma"]:
            status = "Não Informado"
            for s in sacraments:
                if s.startswith(f"{sacrament_name}:"):
                    status = s.split(':')[1].strip()
                    break
            sacrament_data.append([sacrament_name, status])
        
        y_position -= 10
        table = Table(sacrament_data, colWidths=[120, width - 160])
        table.setStyle(self._get_table_style())
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_church_movements_section(self, c, participant, width, y_position):
        """Adiciona a seção de movimentos da igreja"""
        y_position = self._check_page_break(c, y_position)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Movimentos da Igreja")
        
        # Verificar se participa de movimento
        has_movement = bool(participant.church_movement)
        
        data = [
            ["Participa de algum movimento da igreja?", "SIM", "NÃO"],
            ["", "X" if has_movement else "", "X" if not has_movement else ""]
        ]
        
        if has_movement:
            # Usar toda a largura disponível para o texto, combinando rótulo e texto
            movement_label_text = f"Qual movimento?: {participant.church_movement or ''}"
            movement_text = self._wrap_text(movement_label_text, width - 60)
            data.append([movement_text, "", ""])
            if participant.church_movement_info:
                info_label_text = f"Informações adicionais: {participant.church_movement_info or ''}"
                info_text = self._wrap_text(info_label_text, width - 60)
                data.append([info_text, "", ""])
        
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.15, (width - 60) * 0.15])
        
        style = self._get_table_style()
        style.add('ALIGN', (1, 0), (2, -1), 'CENTER')
        style.add('SPAN', (0, 0), (0, 1))  # Mesclar primeira coluna nas duas primeiras linhas
        
        # Mesclar todas as colunas para linhas com informações adicionais (para ocupar toda a largura)
        if has_movement:
            # Linha "Qual movimento?" está no índice 2 - mesclar todas as 3 colunas
            style.add('SPAN', (0, 2), (2, 2))  # Mesclar todas as colunas na linha do movimento
            if participant.church_movement_info:
                # Linha "Informações adicionais:" está no índice 3 - mesclar todas as 3 colunas
                style.add('SPAN', (0, 3), (2, 3))  # Mesclar todas as colunas na linha de informações
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_family_info_section(self, c, participant, width, y_position):
        """Adiciona a seção de informações familiares"""
        y_position = self._check_page_break(c, y_position)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Informações Familiares")
        
        # Função auxiliar para converter valores para string de forma segura
        def safe_str(value):
            if value is None:
                return ""
            value_str = str(value).strip()
            if value_str == "None" or value_str == "":
                return ""
            return value_str
        
        # Converter valores para string e garantir que não sejam None
        father_name_raw = getattr(participant, 'father_name', None)
        father_contact_raw = getattr(participant, 'father_contact', None)
        mother_name_raw = getattr(participant, 'mother_name', None)
        mother_contact_raw = getattr(participant, 'mother_contact', None)
        
        father_name_str = safe_str(father_name_raw)
        father_contact_str = safe_str(father_contact_raw)
        mother_name_str = safe_str(mother_name_raw)
        mother_contact_str = safe_str(mother_contact_raw)
        
        # Log para debug
        print(f"🔍 Debug - Informações Familiares (processando):")
        print(f"   father_name raw: {repr(father_name_raw)} -> final: {repr(father_name_str)}")
        print(f"   father_contact raw: {repr(father_contact_raw)} -> final: {repr(father_contact_str)}")
        print(f"   mother_name raw: {repr(mother_name_raw)} -> final: {repr(mother_name_str)}")
        print(f"   mother_contact raw: {repr(mother_contact_raw)} -> final: {repr(mother_contact_str)}")
        
        data = [
            ["Nome do Pai", "Contato"],
            [father_name_str, father_contact_str],
            ["Nome da Mãe", "Contato"],
            [mother_name_str, mother_contact_str]
        ]
        
        # Log final dos dados que serão exibidos
        print(f"🔍 Debug - Dados finais da tabela familiar:")
        for row in data:
            print(f"   {row}")
        
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.3])
        
        style = self._get_table_style()
        style.add('BACKGROUND', (0, 0), (1, 0), HexColor('#f2f2f2'))
        style.add('BACKGROUND', (0, 2), (1, 2), HexColor('#f2f2f2'))
        style.add('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold')
        style.add('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold')
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_ecc_section(self, c, participant, width, y_position):
        """Adiciona a seção de informações do ECC"""
        y_position = self._check_page_break(c, y_position)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Informações do ECC")
        
        data = [
            ["Seus pais são encontristas do ECC?", "SIM", "NÃO"],
            ["", "X" if participant.ecc_participant else "", "X" if not participant.ecc_participant else ""]
        ]
        
        if participant.ecc_info:
            # Combinar rótulo e texto na mesma célula para ocupar toda a largura
            info_label_text = f"Informações ECC: {participant.ecc_info}"
            info_text = self._wrap_text(info_label_text, width - 60)
            data.append([info_text, "", ""])
        
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.15, (width - 60) * 0.15])
        
        style = self._get_table_style()
        style.add('ALIGN', (1, 0), (2, -1), 'CENTER')
        style.add('SPAN', (0, 0), (0, 1))  # Mesclar primeira coluna nas duas primeiras linhas
        
        # Mesclar todas as colunas para linha com informações adicionais
        if participant.ecc_info:
            style.add('SPAN', (0, 2), (2, 2))  # Mesclar todas as colunas na linha de informações
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_restrictions_section(self, c, participant, width, y_position):
        """Adiciona a seção de restrições e alergias"""
        y_position = self._check_page_break(c, y_position)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Restrições e Alergias")
        
        data = [
            ["Possui alguma restrição alimentar ou alergia?", "SIM", "NÃO"],
            ["", "X" if participant.has_restrictions else "", "X" if not participant.has_restrictions else ""]
        ]
        
        if participant.has_restrictions and participant.restrictions_info:
            # Combinar rótulo e texto na mesma célula para ocupar toda a largura
            info_label_text = f"Quais restrições?: {participant.restrictions_info}"
            info_text = self._wrap_text(info_label_text, width - 60)
            data.append([info_text, "", ""])
        
        y_position -= 10
        table = Table(data, colWidths=[(width - 60) * 0.7, (width - 60) * 0.15, (width - 60) * 0.15])
        
        style = self._get_table_style()
        style.add('ALIGN', (1, 0), (2, -1), 'CENTER')
        style.add('SPAN', (0, 0), (0, 1))  # Mesclar primeira coluna nas duas primeiras linhas
        
        # Mesclar todas as colunas para linha com informações adicionais
        if participant.has_restrictions and participant.restrictions_info:
            style.add('SPAN', (0, 2), (2, 2))  # Mesclar todas as colunas na linha de informações
        
        table.setStyle(style)
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_observations_section(self, c, participant, width, y_position):
        """Adiciona a seção de observações"""
        y_position = self._check_page_break(c, y_position)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y_position, "Observações")
        
        obs_text = self._wrap_text(participant.observations or "", width - 60)
        data = [[obs_text]]
        
        y_position -= 10
        table = Table(data, colWidths=[width - 60])
        table.setStyle(self._get_table_style())
        table.wrapOn(c, width - 60, 400)
        table_height = table._height
        y_position -= table_height
        table.drawOn(c, 30, y_position)
        
        return y_position - 20
    
    def _add_signature_area(self, c, width, y_position):
        """Adiciona a área de assinatura"""
        if y_position < 50:
            c.showPage()
            y_position = A4[1] - 50
        
        y_position -= 30
        c.setFont("Helvetica", 10)
        
        signature_x = 30
        date_x = width/2 + 30
        
        line_height = 20
        c.drawString(signature_x, y_position - line_height, "_" * 40)
        c.drawString(date_x, y_position - line_height, "_" * 7 + " / " + "_" * 7 + " / " + "_" * 7)
        
        c.drawString(signature_x, y_position - line_height - 15, "Assinatura")
        c.drawString(date_x, y_position - line_height - 15, "Data")
    
    def _format_date(self, date_str):
        """Formata a data do formato ISO para o formato brasileiro"""
        if not date_str or date_str == "None" or date_str == "":
            return ""
        
        # Converter para string se não for
        date_str = str(date_str).strip()
        
        if not date_str:
            return ""
        
        try:
            # Tentar formato ISO primeiro (YYYY-MM-DD)
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            # Se não for formato ISO, tentar outros formatos comuns
            try:
                # Tentar formato brasileiro (DD/MM/YYYY)
                date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                return date_str  # Já está no formato correto
            except ValueError:
                # Se não conseguir parsear, retornar como está
                print(f"⚠ Aviso: Não foi possível formatar a data: {date_str}")
                return date_str
    
    def _get_table_style(self):
        """Retorna o estilo padrão para tabelas"""
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Mudado de MIDDLE para TOP
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('BOX', (0, 0), (-1, -1), 1, black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),  # Aumentado de 3 para 6
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Aumentado de 3 para 6
        ])
