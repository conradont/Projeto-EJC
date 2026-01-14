"""API FastAPI para o Sistema EJC"""
from fastapi import FastAPI, HTTPException, Depends, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import shutil
from pathlib import Path
import uuid

from database.database import get_db, init_db
from models.participant import ParticipantResponse, ParticipantCreate, ParticipantUpdate
from services.pdf_service import PDFService
from config import settings

app = FastAPI(
    title="EJC Sistema API",
    description="API para gerenciamento de participantes do EJC",
    version="1.0.0"
)

# Handler para erros de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Retorna detalhes dos erros de validação"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "EJC Sistema API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Rotas de participantes
@app.get("/api/participants", response_model=List[ParticipantResponse])
async def get_participants(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os participantes com paginação e busca"""
    from database import crud
    
    participants = crud.get_participants(db, skip=skip, limit=limit, search=search)
    return participants

@app.get("/api/participants/{participant_id}", response_model=ParticipantResponse)
async def get_participant(participant_id: int, db: Session = Depends(get_db)):
    """Obtém um participante específico"""
    from database import crud
    
    participant = crud.get_participant(db, participant_id=participant_id)
    if participant is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return participant

@app.post("/api/participants", response_model=ParticipantResponse, status_code=201)
async def create_participant(
    participant: ParticipantCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo participante"""
    from database import crud
    
    return crud.create_participant(db=db, participant=participant)

@app.put("/api/participants/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: int,
    participant: ParticipantUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um participante"""
    from database import crud
    
    db_participant = crud.update_participant(db, participant_id=participant_id, participant=participant)
    if db_participant is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return db_participant

@app.delete("/api/participants/{participant_id}", status_code=204)
async def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    """Exclui um participante"""
    from database import crud
    
    success = crud.delete_participant(db, participant_id=participant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return None

# Rotas de upload de fotos
@app.post("/api/photos/upload")
async def upload_photo(file: UploadFile = File(...)):
    """Faz upload de uma foto e retorna o nome do arquivo salvo"""
    # Validar tipo de arquivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Gerar nome único para o arquivo
    file_extension = Path(file.filename).suffix if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = settings.PHOTOS_DIR / unique_filename
    
    try:
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"filename": unique_filename, "path": str(file_path.relative_to(settings.DATA_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar foto: {str(e)}")

@app.get("/api/photos/{filename}")
async def get_photo(filename: str):
    """Retorna uma foto pelo nome do arquivo"""
    file_path = settings.PHOTOS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Foto não encontrada")
    
    # Determinar tipo de conteúdo baseado na extensão
    content_type = "image/jpeg"
    if filename.lower().endswith('.png'):
        content_type = "image/png"
    elif filename.lower().endswith('.gif'):
        content_type = "image/gif"
    elif filename.lower().endswith('.webp'):
        content_type = "image/webp"
    
    return FileResponse(file_path, media_type=content_type)

# Rotas de logo do evento
@app.post("/api/logo/upload")
async def upload_logo(file: UploadFile = File(...)):
    """Faz upload da logo do evento e retorna o nome do arquivo salvo"""
    # Validar tipo de arquivo
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    # Limpar diretório de logo (manter apenas uma logo)
    for existing_file in settings.LOGO_DIR.glob("*"):
        try:
            existing_file.unlink()
        except Exception as e:
            print(f"⚠ Erro ao remover logo antiga: {e}")
    
    # Gerar nome único para o arquivo
    file_extension = Path(file.filename).suffix if file.filename else '.png'
    logo_filename = f"logo{file_extension}"
    file_path = settings.LOGO_DIR / logo_filename
    
    try:
        # Salvar arquivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"filename": logo_filename, "path": str(file_path.relative_to(settings.DATA_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar logo: {str(e)}")

@app.get("/api/logo")
async def get_logo():
    """Retorna a logo do evento"""
    # Procurar qualquer arquivo de imagem no diretório de logo
    logo_files = list(settings.LOGO_DIR.glob("*"))
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']
    
    for logo_file in logo_files:
        if logo_file.suffix.lower() in image_extensions:
            # Determinar tipo de conteúdo baseado na extensão
            content_type = "image/png"
            if logo_file.suffix.lower() in ['.jpg', '.jpeg']:
                content_type = "image/jpeg"
            elif logo_file.suffix.lower() == '.gif':
                content_type = "image/gif"
            elif logo_file.suffix.lower() == '.webp':
                content_type = "image/webp"
            elif logo_file.suffix.lower() == '.svg':
                content_type = "image/svg+xml"
            
            return FileResponse(logo_file, media_type=content_type)
    
    raise HTTPException(status_code=404, detail="Logo não encontrada")

@app.delete("/api/logo")
async def delete_logo():
    """Remove a logo do evento"""
    logo_files = list(settings.LOGO_DIR.glob("*"))
    deleted_count = 0
    
    for logo_file in logo_files:
        try:
            logo_file.unlink()
            deleted_count += 1
        except Exception as e:
            print(f"⚠ Erro ao remover logo: {e}")
    
    if deleted_count > 0:
        return {"status": "success", "message": "Logo removida com sucesso"}
    else:
        raise HTTPException(status_code=404, detail="Nenhuma logo encontrada para remover")

# Rotas de PDF
@app.get("/api/pdf/participant/{participant_id}")
async def generate_participant_pdf(participant_id: int, db: Session = Depends(get_db)):
    """Gera PDF individual de um participante"""
    from database import crud
    
    participant = crud.get_participant(db, participant_id=participant_id)
    if participant is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    
    pdf_service = PDFService(db=db)
    pdf_path = pdf_service.generate_individual_pdf(participant_id)
    
    if not pdf_path:
        raise HTTPException(status_code=500, detail="Erro ao gerar PDF")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"ficha_{participant.name.replace(' ', '_')}.pdf"
    )

@app.get("/api/pdf/complete")
async def generate_complete_pdf(db: Session = Depends(get_db)):
    """Gera PDF completo com todos os participantes"""
    pdf_service = PDFService(db=db)
    pdf_path = pdf_service.generate_complete_pdf()
    
    if not pdf_path:
        raise HTTPException(status_code=500, detail="Erro ao gerar PDF")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="fichas_completas.pdf"
    )

# Rotas de manutenção do banco de dados (opcionais)
@app.get("/api/db/info")
async def database_info():
    """Retorna informações sobre o banco de dados"""
    from utils import get_database_info
    return get_database_info()

@app.post("/api/db/backup")
async def create_backup():
    """Cria um backup do banco de dados"""
    from utils import backup_database
    backup_path = backup_database()
    if backup_path:
        return {"status": "success", "backup_path": backup_path}
    else:
        raise HTTPException(status_code=500, detail="Erro ao criar backup")

@app.post("/api/db/optimize")
async def optimize_db():
    """Otimiza o banco de dados (compactação e análise)"""
    from utils import optimize_database
    optimize_database()
    return {"status": "success", "message": "Banco de dados otimizado"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
