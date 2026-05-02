import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.documento import Documento
from app.core.dependencies import get_current_user
from app.services.storage_service import storage_service
from pydantic import BaseModel

router = APIRouter()

class DocumentoResponse(BaseModel):
    id: Any
    nombre_original: str
    tipo_documento: str
    storage_url: str

@router.post("/upload", response_model=DocumentoResponse)
async def upload_documento(
    file: UploadFile = File(...),
    tipo_documento: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    # Sube un documento al almacenamiento.
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede el límite de 10MB")

    content = await file.read()
    ext = f".{file.filename.split('.')[-1]}" if '.' in file.filename else ""
    
    # Upload to R2
    storage_key, sha256 = await storage_service.upload(
        content=content,
        extension=ext,
        tenant_id=current_user.tenant_id,
        tipo="documentos"
    )
    
    # Generate temporary URL for response
    url = await storage_service.generate_presigned_url(storage_key)
    
    new_doc = Documento(
        tenant_id=current_user.tenant_id,
        nombre_original=file.filename,
        nombre_storage=storage_key.split('/')[-1],
        storage_url=url,
        storage_key=storage_key,
        mime_type=file.content_type,
        tamaño_bytes=len(content),
        tipo_documento=tipo_documento,
        hash_sha256=sha256,
        subido_por=current_user.id
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return new_doc

@router.get("/", response_model=List[DocumentoResponse])
async def list_documentos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Documento).filter(Documento.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()
