"""Gerenciamento do banco de dados do sistema EJC"""
import sqlite3
import config


class DatabaseManager:
    """Classe responsável pelo gerenciamento do banco de dados"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DB_PATH
        self._ensure_directories()
        self._init_database()
    
    def _ensure_directories(self):
        """Garante que os diretórios necessários existam"""
        config.EJC_DATA_DIR.mkdir(parents=True, exist_ok=True)
        config.PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Inicializa o banco de dados com a estrutura necessária"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='participants'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Verificar se os novos campos existem
            cursor.execute("PRAGMA table_info(participants)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Adicionar novos campos se não existirem
            if "birth_date" not in columns:
                cursor.execute("ALTER TABLE participants ADD COLUMN birth_date TEXT")
            
            if "instagram" not in columns:
                cursor.execute("ALTER TABLE participants ADD COLUMN instagram TEXT")
                
            if "father_contact" not in columns:
                cursor.execute("ALTER TABLE participants ADD COLUMN father_contact TEXT")
                
            if "mother_contact" not in columns:
                cursor.execute("ALTER TABLE participants ADD COLUMN mother_contact TEXT")
                
            # Adicionar campos que podem estar faltando
            required_columns = [
                "name", "common_name", "address", "neighborhood", 
                "email", "phone", "sacraments", "church_movement",
                "father_name", "mother_name", "ecc_participant", 
                "ecc_info", "has_restrictions", "restrictions_info",
                "observations", "photo_path"
            ]
            
            for col in required_columns:
                if col not in columns:
                    cursor.execute(f"ALTER TABLE participants ADD COLUMN {col} TEXT")
        else:
            # Criar tabela com todos os campos
            cursor.execute('''
                CREATE TABLE participants (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    common_name TEXT,
                    birth_date TEXT,
                    instagram TEXT,
                    address TEXT,
                    neighborhood TEXT,
                    email TEXT,
                    phone TEXT,
                    sacraments TEXT,
                    church_movement TEXT,
                    father_name TEXT,
                    father_contact TEXT,
                    mother_name TEXT,
                    mother_contact TEXT,
                    ecc_participant BOOLEAN,
                    ecc_info TEXT,
                    has_restrictions BOOLEAN,
                    restrictions_info TEXT,
                    observations TEXT,
                    photo_path TEXT
                )
            ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Obtém uma conexão com o banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
    
    def insert_participant(self, participant_data):
        """
        Insere um novo participante no banco de dados
        Retorna o ID do participante inserido ou None em caso de erro
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO participants (
                    name, common_name, birth_date, instagram, address, neighborhood,
                    email, phone, sacraments, church_movement,
                    father_name, father_contact, mother_name, mother_contact, 
                    ecc_participant, ecc_info,
                    has_restrictions, restrictions_info,
                    photo_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', participant_data)
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"Erro ao inserir participante: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_participants(self):
        """Retorna todos os participantes"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participants ORDER BY name")
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_participant_by_id(self, participant_id):
        """Retorna um participante específico pelo ID"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM participants WHERE id = ?", (participant_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def update_participant(self, participant_id, participant_data):
        """Atualiza os dados de um participante"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE participants
                SET name = ?, common_name = ?, birth_date = ?, instagram = ?, 
                    address = ?, neighborhood = ?, email = ?, phone = ?, 
                    sacraments = ?, church_movement = ?, father_name = ?, 
                    father_contact = ?, mother_name = ?, mother_contact = ?, 
                    ecc_participant = ?, ecc_info = ?, has_restrictions = ?, 
                    restrictions_info = ?, observations = ?, photo_path = ?
                WHERE id = ?
            ''', (*participant_data, participant_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar participante: {e}")
            return False
        finally:
            conn.close()
    
    def delete_participant(self, participant_id):
        """Exclui um participante do banco de dados"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM participants WHERE id = ?", (participant_id,))
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Erro ao excluir participante: {e}")
            return False
        finally:
            conn.close()
    
    def search_participants(self, search_text):
        """Busca participantes por texto"""
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM participants
                WHERE (
                    LOWER(name) LIKE ? OR 
                    LOWER(common_name) LIKE ? OR 
                    LOWER(email) LIKE ? OR 
                    LOWER(phone) LIKE ? OR
                    LOWER(instagram) LIKE ?
                )
            """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", 
                  f"%{search_text}%", f"%{search_text}%"))
            return cursor.fetchall()
        finally:
            conn.close()

