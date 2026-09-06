from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class DocumentCreate(BaseModel):
    name: str
    doc_type: str

class DocumentResponse(BaseModel):
    id: str
    name: str
    doc_type: str
    file_path: str
    chunk_count: int
    file_size: int
    upload_date: datetime

    model_config = {"from_attributes": True}

class DocumentDetail(DocumentResponse):
    parsed_content: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    collection: str = 'knowledge_base'
    top_k: int = 10

class SearchResult(BaseModel):
    chunk_text: str
    metadata: Dict[str, Any]
    score: float
