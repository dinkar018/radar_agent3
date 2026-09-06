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
    # Auto-discover files in radar_data directory
    radar_dir = settings.RADAR_DATA_DIR
    if os.path.exists(radar_dir):
        existing_res = await db.execute(select(DataFile))
        existing_paths = {df.file_path for df in existing_res.scalars().all()}
        
        for fname in os.listdir(radar_dir):
            fpath = os.path.join(radar_dir, fname)
            if os.path.isfile(fpath) and fpath not in existing_paths:
                fsize = os.path.getsize(fpath)
                desc = "Pre-generated synthetic SAR dataset" if "sar_data" in fname else "Captured radar dataset"
                new_df = DataFile(
                    id=str(uuid.uuid4()),
                    name=fname,
                    file_path=fpath,
                    file_size=fsize,
                    description=desc
                )
                db.add(new_df)
        await db.commit()

    result = await db.execute(select(DataFile))
    files = result.scalars().all()
    
    file_list = []
    for f in files:
        item = {
            "id": f.id,
            "name": f.name,
            "file_path": f.file_path,
            "file_size": f.file_size,
            "description": f.description,
            "upload_date": f.upload_date.isoformat() if f.upload_date else None,
            "shape": None,
            "dtype": None,
        }
        if f.name.endswith('.npy') and os.path.exists(f.file_path):
            try:
                arr = np.load(f.file_path, mmap_mode='r')
                item["shape"] = list(arr.shape)
                item["dtype"] = str(arr.dtype)
            except Exception:
                pass
        file_list.append(item)
        
    return file_list

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
