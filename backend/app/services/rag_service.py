import logging
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        logger.info("Initialized RAGService")

    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Chunks the text using markdown-aware separators."""
        splitter = RecursiveCharacterTextSplitter(
            separators=['\n## ', '\n### ', '\n#### ', '\n\n', '\n', ' '],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            keep_separator=True
        )
        return splitter.split_text(text)

    def ingest_document(self, doc_id: str, doc_name: str, doc_type: str, text: str, collection_name: str) -> int:
        """Chunks text, generates IDs, creates metadata, and adds to vector store."""
        chunks = self.chunk_text(text)
        
        ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            ids.append(f"{doc_id}_chunk_{i}")
            metadatas.append({
                "doc_id": doc_id,
                "doc_name": doc_name,
                "doc_type": doc_type,
                "chunk_index": i
            })
            
        self.vector_store.add_documents(
            collection_name=collection_name,
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Ingested document {doc_id} with {len(chunks)} chunks into {collection_name}")
        return len(chunks)

    def retrieve(self, query: str, collection_name: str, top_k: int = 10, doc_id: Optional[str] = None) -> str:
        """Searches vector store and formats results into a context string."""
        where = {"doc_id": doc_id} if doc_id else None
        results = self.vector_store.search(
            collection_name=collection_name,
            query=query,
            top_k=top_k,
            where=where
        )
        
        if not results:
            return ""
            
        context_parts = []
        for i, res in enumerate(results):
            text = res.get("text", "")
            metadata = res.get("metadata", {})
            doc_name_info = f" (Source: {metadata.get('doc_name', 'Unknown')})"
            context_parts.append(f"--- Chunk {i+1}{doc_name_info} ---\n{text}\n")
            
        return "\n".join(context_parts)

    def delete_document(self, doc_id: str, collection_name: str):
        """Removes all chunks for a document from vector store."""
        self.vector_store.delete_by_metadata(collection_name, doc_id)
        logger.info(f"Deleted document {doc_id} from {collection_name}")
