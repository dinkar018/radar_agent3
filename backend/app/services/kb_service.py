import os
import uuid
import logging
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import Settings
from app.models.document import Document
from app.services.rag_service import RAGService
from app.services.pdf_parser import parse_pdf_to_markdown

logger = logging.getLogger(__name__)

class KBService:
    def __init__(self, rag_service: RAGService, settings: Settings):
        self.rag_service = rag_service
        self.settings = settings
        
        # Ensure base directories exist
        if not hasattr(self.settings, 'UPLOAD_DIR'):
            # Fallback if UPLOAD_DIR is not present in settings
            self.settings.UPLOAD_DIR = "uploads"
            
        os.makedirs(os.path.join(self.settings.UPLOAD_DIR, "knowledge_base"), exist_ok=True)
        os.makedirs(os.path.join(self.settings.UPLOAD_DIR, "papers"), exist_ok=True)
        logger.info("Initialized KBService")

    async def upload_document(self, file: UploadFile, doc_type: str, db: AsyncSession) -> Document:
        """
        Saves file, parses to markdown, ingests to vector store, and creates Document record.
        """
        if doc_type not in ["knowledge_base", "research_papers"]:
            raise ValueError(f"Invalid doc_type: {doc_type}")
            
        doc_id = str(uuid.uuid4())
        
        # Save file to disk
        subdir = "knowledge_base" if doc_type == "knowledge_base" else "papers"
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".txt"
        file_path = os.path.join(self.settings.UPLOAD_DIR, subdir, f"{doc_id}{file_ext}")
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
            
        # Parse content
        try:
            if file_ext.lower() == ".pdf":
                text = parse_pdf_to_markdown(file_path)
            elif file_ext.lower() in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file extension: {file_ext}")
        except Exception as e:
            # Clean up on parse failure
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

        # Ingest to vector store
        try:
            chunk_count = self.rag_service.ingest_document(
                doc_id=doc_id,
                doc_name=file.filename or "unknown",
                doc_type=doc_type,
                text=text,
                collection_name=doc_type
            )
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

        # Create DB record
        doc = Document(
            id=doc_id,
            filename=file.filename or "unknown",
            file_path=file_path,
            doc_type=doc_type,
            chunk_count=chunk_count
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        
        return doc

    async def list_documents(self, db: AsyncSession, doc_type: Optional[str] = None) -> List[Document]:
        """Lists documents, optionally filtered by type."""
        query = select(Document)
        if doc_type:
            query = query.where(Document.doc_type == doc_type)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_document(self, db: AsyncSession, doc_id: str) -> Document:
        """Gets a document by ID."""
        result = await db.execute(select(Document).where(Document.id == doc_id))
        doc = result.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    async def delete_document(self, db: AsyncSession, doc_id: str):
        """Deletes from ChromaDB + SQLite + disk."""
        doc = await self.get_document(db, doc_id)
        
        # Delete from vector store
        try:
            self.rag_service.delete_document(doc_id, doc.doc_type)
        except Exception as e:
            logger.error(f"Failed to delete document from vector store: {e}")
            
        # Delete from disk
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            
        # Delete from DB
        await db.delete(doc)
        await db.commit()

    async def search(self, query: str, collection: str, top_k: int) -> list[dict]:
        """Wraps vector store search directly to return list of dicts as requested."""
        return self.rag_service.vector_store.search(collection_name=collection, query=query, top_k=top_k)
