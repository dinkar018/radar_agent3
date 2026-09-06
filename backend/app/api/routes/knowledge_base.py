import uuid
import os
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentDetail, SearchRequest, SearchResult
from app.services.file_storage import FileStorageService
from app.services.pdf_parser import parse_pdf_to_markdown
from app.services.rag_service import RAGService
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])

vector_store = VectorStoreService(persist_dir=settings.CHROMA_PERSIST_DIR)
rag_service = RAGService(vector_store=vector_store)
file_storage = FileStorageService(base_dir=settings.UPLOAD_DIR)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    file_path = file_storage.save_upload(file, "knowledge_base")
    
    try:
        parsed_content = parse_pdf_to_markdown(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {e}")
        
    doc_id = str(uuid.uuid4())
    
    chunk_count = rag_service.ingest_document(
        doc_id=doc_id,
        doc_name=file.filename,
        doc_type=doc_type,
        text=parsed_content,
        collection_name="knowledge_base"
    )
    
    file_size = os.path.getsize(file_path)
    document = Document(
        id=doc_id,
        name=file.filename,
        doc_type=doc_type,
        file_path=file_path,
        parsed_content=parsed_content,
        chunk_count=chunk_count,
        file_size=file_size,
        collection_name="knowledge_base"
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return document

@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(doc_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Document)
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    result = await db.execute(query)
    documents = result.scalars().all()
    return list(documents)

@router.get("/documents/{doc_id}", response_model=DocumentDetail)
async def get_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    rag_service.delete_document(doc_id, document.collection_name)
    file_storage.delete_file(document.file_path)
    
    await db.delete(document)
    await db.commit()
    return {"message": "Document deleted successfully"}

@router.post("/search", response_model=list[SearchResult])
async def search_documents(request: SearchRequest):
    results = vector_store.search(
        collection_name=request.collection,
        query=request.query,
        top_k=request.top_k
    )
    
    search_results = []
    for res in results:
        search_results.append(
            SearchResult(
                chunk_text=res.get("text", ""),
                metadata=res.get("metadata", {}),
                score=res.get("score", 0.0)
            )
        )
    return search_results
