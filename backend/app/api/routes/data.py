import uuid
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import numpy as np

from app.core.database import get_db
from app.core.config import settings
from app.models.data_file import DataFile
from app.services.file_storage import FileStorageService

router = APIRouter(prefix="/data", tags=["Radar Data"])
file_storage = FileStorageService(base_dir=settings.UPLOAD_DIR)

@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db)
):
    file_path = file_storage.save_upload(file, "radar_data")
    file_id = str(uuid.uuid4())
    file_size = os.path.getsize(file_path)
    
    data_file = DataFile(
        id=file_id,
        name=file.filename,
        file_path=file_path,
        file_size=file_size,
        description=description
    )
    
    db.add(data_file)
    await db.commit()
    await db.refresh(data_file)
    return data_file

@router.get("/files")
async def list_data_files(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DataFile))
    return list(result.scalars().all())

@router.get("/files/{file_id}")
async def get_data_file(file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DataFile).where(DataFile.id == file_id))
    data_file = result.scalar_one_or_none()
    if not data_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    info = {
        "id": data_file.id,
        "name": data_file.name,
        "file_path": data_file.file_path,
        "file_size": data_file.file_size,
        "description": data_file.description,
        "upload_date": data_file.upload_date
    }
    
    if data_file.name.endswith('.npy'):
        try:
            arr = np.load(data_file.file_path)
            info["shape"] = list(arr.shape)
            info["dtype"] = str(arr.dtype)
        except Exception:
            pass
            
    return info

@router.delete("/files/{file_id}")
async def delete_data_file(file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DataFile).where(DataFile.id == file_id))
    data_file = result.scalar_one_or_none()
    if not data_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    file_storage.delete_file(data_file.file_path)
    await db.delete(data_file)
    await db.commit()
    return {"message": "File deleted"}
