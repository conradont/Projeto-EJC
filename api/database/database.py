"""Configuração do banco de dados"""
from sqlalchemy import create_engine, text, inspect, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Detectar tipo de banco de dados
IS_SQLITE = "sqlite" in settings.DATABASE_URL
IS_POSTGRES = "postgresql" in settings.DATABASE_URL or "postgres" in settings.DATABASE_URL

# Configuração específica por tipo de banco
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,  # Verifica conexões antes de usar
    "echo": False,  # Desabilita logs SQL (mude para True para debug)
}

if IS_SQLITE:
    # Configuração otimizada do SQLite
    connect_args = {
        "check_same_thread": False,
        "timeout": 20,  # Timeout de 20 segundos para operações
    }
elif IS_POSTGRES:
    # Configuração otimizada do PostgreSQL (Neon)
    # Neon usa connection pooling, então não precisamos de pool muito grande
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 300,  # Recicla conexões após 5 minutos
    })
    print("✓ Usando PostgreSQL (Neon)")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Configurar otimizações do SQLite após conexão
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Aplica otimizações do SQLite ao conectar"""
    if IS_SQLITE:
        cursor = dbapi_conn.cursor()
        # WAL mode para melhor concorrência (permite leituras simultâneas)
        cursor.execute("PRAGMA journal_mode=WAL")
        # Otimizações de performance
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance entre segurança e performance
        cursor.execute("PRAGMA cache_size=-64000")  # Cache de 64MB
        cursor.execute("PRAGMA foreign_keys=ON")  # Habilita foreign keys
        cursor.execute("PRAGMA temp_store=MEMORY")  # Armazena temporários em memória
        cursor.execute("PRAGMA mmap_size=268435456")  # Memory-mapped I/O (256MB)
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def optimize_database():
    """Otimiza o banco de dados (SQLite ou PostgreSQL)"""
    try:
        with engine.connect() as conn:
            if IS_SQLITE:
                # Analisa tabelas para melhorar performance de queries
                conn.execute(text("ANALYZE"))
                # Compacta o banco de dados
                conn.execute(text("VACUUM"))
                conn.commit()
                print("✓ Banco de dados SQLite otimizado com sucesso")
            elif IS_POSTGRES:
                # Para PostgreSQL, executar VACUUM ANALYZE
                conn.execute(text("VACUUM ANALYZE"))
                conn.commit()
                print("✓ Banco de dados PostgreSQL otimizado com sucesso")
    except Exception as e:
        print(f"⚠ Aviso ao otimizar banco de dados: {e}")


def init_db():
    """Inicializa o banco de dados criando as tabelas e aplicando migrações"""
    from models.participant import Participant
    
    # Criar todas as tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    print(f"✓ Tabelas criadas/verificadas no banco de dados ({'PostgreSQL' if IS_POSTGRES else 'SQLite'})")
    
    # Aplicar migrações manuais para adicionar novas colunas
    inspector = inspect(engine)
    
    if 'participants' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('participants')]
        
        # Migração: adicionar coluna church_movement_info se não existir
        if 'church_movement_info' not in columns:
            try:
                with engine.connect() as conn:
                    if IS_SQLITE:
                        conn.execute(text("ALTER TABLE participants ADD COLUMN church_movement_info TEXT"))
                    elif IS_POSTGRES:
                        conn.execute(text("ALTER TABLE participants ADD COLUMN church_movement_info TEXT"))
                    conn.commit()
                    print("✓ Coluna 'church_movement_info' adicionada com sucesso")
            except Exception as e:
                print(f"⚠ Aviso ao adicionar coluna 'church_movement_info': {e}")
        
        # Executar análise inicial para melhorar performance
        try:
            with engine.connect() as conn:
                if IS_SQLITE:
                    conn.execute(text("ANALYZE"))
                elif IS_POSTGRES:
                    conn.execute(text("ANALYZE participants"))
                conn.commit()
        except Exception as e:
            print(f"⚠ Aviso ao analisar banco de dados: {e}")
