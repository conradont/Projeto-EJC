"""API FastAPI para o Sistema EJC"""
from fastapi import FastAPI, HTTPException, Depends, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import shutil
from pathlib import Path
import sys
import uuid

from database.database import get_db, init_db
from models.participant import ParticipantResponse, ParticipantCreate, ParticipantUpdate


class ParticipantsListResponse(BaseModel):
    participants: List[ParticipantResponse]
    total: int
from services.pdf_service import PDFService
from services.storage_service import (
    use_supabase_storage,
    get_signed_url,
    upload_photo as storage_upload_photo,
    upload_logo as storage_upload_logo,
    delete_logo_storage,
    get_logo_path_from_db,
    set_logo_path_in_db,
    BUCKET_PHOTOS,
    BUCKET_LOGO,
)
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

def _dist_dir() -> Path:
    """Pasta dist: dentro do .exe (PyInstaller) ou ao lado de api/."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "dist"
    return Path(__file__).resolve().parent.parent / "dist"


@app.get("/")
async def root():
    _root_dist = _dist_dir()
    if _root_dist.exists() and (_root_dist / "index.html").exists():
        return FileResponse(_root_dist / "index.html", media_type="text/html")
    return {"message": "EJC Sistema API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Rotas de participantes
@app.get("/api/participants", response_model=ParticipantsListResponse)
async def get_participants(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os participantes com paginação e busca. Retorna total para paginação."""
    from database import crud

    participants = crud.get_participants(db, skip=skip, limit=limit, search=search)
    total = crud.get_participants_count(db, search=search)
    return ParticipantsListResponse(participants=participants, total=total)

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
    """Cria um novo participante. Rejeita e-mail ou telefone duplicados."""
    from database import crud

    if crud.participant_exists_with_email(db, participant.email):
        raise HTTPException(
            status_code=409,
            detail="Já existe um participante cadastrado com este e-mail.",
        )
    if crud.participant_exists_with_phone(db, participant.phone):
        raise HTTPException(
            status_code=409,
            detail="Já existe um participante cadastrado com este telefone.",
        )
    return crud.create_participant(db=db, participant=participant)

@app.put("/api/participants/{participant_id}", response_model=ParticipantResponse)
async def update_participant(
    participant_id: int,
    participant: ParticipantUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um participante. Rejeita e-mail ou telefone duplicados."""
    from database import crud

    if participant.email is not None and crud.participant_exists_with_email(db, participant.email, exclude_id=participant_id):
        raise HTTPException(
            status_code=409,
            detail="Já existe um participante cadastrado com este e-mail.",
        )
    if participant.phone is not None and crud.participant_exists_with_phone(db, participant.phone, exclude_id=participant_id):
        raise HTTPException(
            status_code=409,
            detail="Já existe um participante cadastrado com este telefone.",
        )
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

# Limite de tamanho para upload de imagens (4 MB)
MAX_PHOTO_SIZE_BYTES = 4 * 1024 * 1024

# Rotas de upload de fotos
@app.post("/api/photos/upload")
async def upload_photo(file: UploadFile = File(...)):
    """Faz upload de uma foto (máx. 4 MB). Com Supabase Storage retorna URL pública; senão salva localmente."""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

    content = await file.read()
    if len(content) > MAX_PHOTO_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Foto deve ter no máximo 4 MB. Reduza o tamanho ou a resolução da imagem.",
        )

    file_extension = Path(file.filename).suffix if file.filename else '.jpg'
    content_type = file.content_type or "image/jpeg"

    if use_supabase_storage():
        try:
            path = storage_upload_photo(content, content_type, file_extension)
            if path:
                return {"filename": path, "path": path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao enviar foto: {str(e)}")

    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = settings.PHOTOS_DIR / unique_filename
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        return {"filename": unique_filename, "path": str(file_path.relative_to(settings.DATA_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar foto: {str(e)}")

@app.get("/api/photos/{filename}")
async def get_photo(filename: str):
    """Retorna uma foto: Supabase = redirect para signed URL; senão serve do disco."""
    if use_supabase_storage():
        signed_url = get_signed_url(BUCKET_PHOTOS, filename)
        if signed_url:
            return RedirectResponse(url=signed_url)
    file_path = settings.PHOTOS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Foto não encontrada")
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
async def upload_logo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Faz upload da logo (máx. 4 MB). Com Supabase guarda no Storage e a URL no banco; retorna a URL."""
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")

    content = await file.read()
    if len(content) > MAX_PHOTO_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Logo deve ter no máximo 4 MB. Reduza o tamanho ou a resolução da imagem.",
        )

    file_extension = Path(file.filename).suffix if file.filename else '.png'
    content_type = file.content_type or "image/png"

    if use_supabase_storage():
        try:
            path = storage_upload_logo(content, content_type, file_extension)
            if path:
                set_logo_path_in_db(db, path)
                return {"filename": path, "path": path}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao enviar logo: {str(e)}")

    for existing_file in settings.LOGO_DIR.glob("*"):
        try:
            existing_file.unlink()
        except Exception as e:
            print(f"⚠ Erro ao remover logo antiga: {e}")
    logo_filename = f"logo{file_extension}"
    file_path = settings.LOGO_DIR / logo_filename
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        return {"filename": logo_filename, "path": str(file_path.relative_to(settings.DATA_DIR))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar logo: {str(e)}")

@app.get("/api/logo")
async def get_logo(db: Session = Depends(get_db)):
    """Retorna a logo: Supabase = redirect para signed URL; senão serve do disco.
    Se não houver logo, retorna 204 No Content em vez de 404 para evitar erros no frontend.
    """
    if use_supabase_storage():
        logo_path = get_logo_path_from_db(db)
        if logo_path:
            signed_url = get_signed_url(BUCKET_LOGO, logo_path)
            if signed_url:
                return RedirectResponse(url=signed_url)
    
    # Verificar se o diretório existe antes de listar
    if not settings.LOGO_DIR.exists():
        settings.LOGO_DIR.mkdir(parents=True, exist_ok=True)
    
    logo_files = list(settings.LOGO_DIR.glob("*"))
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']
    for logo_file in logo_files:
        if logo_file.is_file() and logo_file.suffix.lower() in image_extensions:
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
    
    # Retornar 204 No Content quando não há logo (em vez de 404)
    # Isso evita erros nos logs e é mais semântico: "não há conteúdo" vs "não encontrado"
    from fastapi.responses import Response
    return Response(status_code=204)

@app.delete("/api/logo")
async def delete_logo(db: Session = Depends(get_db)):
    """Remove a logo do evento (Storage e banco quando Supabase; ou arquivos locais)."""
    if use_supabase_storage():
        delete_logo_storage()
        set_logo_path_in_db(db, None)
        return {"status": "success", "message": "Logo removida com sucesso"}
    deleted_count = 0
    for logo_file in settings.LOGO_DIR.glob("*"):
        try:
            logo_file.unlink()
            deleted_count += 1
        except Exception as e:
            print(f"⚠ Erro ao remover logo: {e}")
    if deleted_count > 0:
        return {"status": "success", "message": "Logo removida com sucesso"}
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
    """Gera PDF completo com todos os participantes. Desativado na Vercel (timeout 10s)."""
    if getattr(settings, "IS_VERCEL", False):
        raise HTTPException(
            status_code=503,
            detail=(
                "Geração de PDF completo não está disponível neste ambiente devido ao limite de tempo. "
                "Use os PDFs individuais ou execute a API localmente para gerar o PDF completo."
            ),
        )
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

# Servir frontend estático (dist) quando a pasta existir (Vercel ou executável local)
from fastapi.staticfiles import StaticFiles
_dist = _dist_dir()
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
