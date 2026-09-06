import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.client = chromadb.PersistentClient(path=persist_dir)
        # Initialize the embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info(f"Initialized VectorStoreService with persist_dir: {persist_dir}")

    def get_or_create_collection(self, name: str):
        """Gets or creates a collection with the embedding function."""
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_function
        )

    def add_documents(self, collection_name: str, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Adds chunks to the collection."""
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, collection_name: str, query: str, top_k: int = 10, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Semantic search, returns list of {text, metadata, distance}."""
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )

        formatted_results = []
        if not results["documents"] or not results["documents"][0]:
            return formatted_results

        for i in range(len(results["documents"][0])):
            formatted_results.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0.0,
            })
        
        return formatted_results

    def delete_by_metadata(self, collection_name: str, doc_id: str):
        """Delete all chunks belonging to a document."""
        collection = self.get_or_create_collection(collection_name)
        collection.delete(
            where={"doc_id": doc_id}
        )

    def get_collection_count(self, collection_name: str) -> int:
        """Get total chunks in collection."""
        collection = self.get_or_create_collection(collection_name)
        return collection.count()
