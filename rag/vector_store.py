"""
Vector store operations for RAG functionality.
"""
from typing import List, Dict, Any, Optional
import logging
import numpy as np
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class VectorStore:
    """Abstract base class for vector store operations."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the vector store."""
        raise NotImplementedError
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store."""
        raise NotImplementedError
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        raise NotImplementedError
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store."""
        raise NotImplementedError
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        raise NotImplementedError

class PineconeStore(VectorStore):
    """Pinecone vector store implementation."""
    
    def __init__(self):
        super().__init__()
        self.index = None
        
    async def initialize(self) -> bool:
        """Initialize Pinecone connection."""
        if not PINECONE_AVAILABLE:
            logger.error("Pinecone not available")
            return False
        
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            logger.error("Pinecone API key not configured")
            return False
        
        try:
            pinecone.init(
                api_key=api_key,
                environment=os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
            )
            
            index_name = os.getenv("PINECONE_INDEX_NAME", "hazardsafe-kg")
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI ada-002 embedding dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(index_name)
            self.initialized = True
            logger.info("Pinecone vector store initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            return False
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Pinecone."""
        if not self.initialized:
            return False
        
        try:
            vectors = []
            for doc in documents:
                vectors.append({
                    "id": doc["id"],
                    "values": doc["embedding"],
                    "metadata": {
                        "text": doc["text"],
                        "source": doc.get("source", ""),
                        "type": doc.get("type", "document")
                    }
                })
            
            self.index.upsert(vectors=vectors)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Pinecone: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search Pinecone for similar documents."""
        if not self.initialized:
            return []
        
        try:
            # Note: This requires query embedding to be passed
            # For now, return empty results
            return []
            
        except Exception as e:
            logger.error(f"Failed to search Pinecone: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from Pinecone."""
        if not self.initialized:
            return False
        
        try:
            self.index.delete(ids=[doc_id])
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from Pinecone: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Pinecone statistics."""
        if not self.initialized:
            return {"error": "Not initialized"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "index_fullness": stats.get("index_fullness", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {"error": str(e)}

class LocalVectorStore(VectorStore):
    """Local file-based vector store for development."""
    
    def __init__(self):
        super().__init__()
        self.store_path = Path("data/rag/vector_db/local")
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.documents = {}
        self.embeddings = {}
        
    async def initialize(self) -> bool:
        """Initialize local vector store."""
        try:
            # Load existing data
            docs_file = self.store_path / "documents.json"
            if docs_file.exists():
                with open(docs_file, 'r') as f:
                    self.documents = json.load(f)
            
            embeddings_file = self.store_path / "embeddings.json"
            if embeddings_file.exists():
                with open(embeddings_file, 'r') as f:
                    self.embeddings = json.load(f)
            
            self.initialized = True
            logger.info("Local vector store initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize local vector store: {e}")
            return False
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to local store."""
        try:
            for doc in documents:
                doc_id = doc["id"]
                self.documents[doc_id] = {
                    "text": doc["text"],
                    "source": doc.get("source", ""),
                    "type": doc.get("type", "document"),
                    "created_at": doc.get("created_at", "")
                }
                
                if "embedding" in doc:
                    self.embeddings[doc_id] = doc["embedding"]
            
            # Save to disk
            await self._save_data()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to local store: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search local store (simplified - returns recent documents)."""
        try:
            # For now, return recent documents
            # In a real implementation, this would compute embeddings and similarity
            recent_docs = list(self.documents.items())[-top_k:]
            return [
                {
                    "id": doc_id,
                    "text": doc_data["text"],
                    "source": doc_data["source"],
                    "type": doc_data["type"],
                    "score": 0.8  # Placeholder similarity score
                }
                for doc_id, doc_data in recent_docs
            ]
            
        except Exception as e:
            logger.error(f"Failed to search local store: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from local store."""
        try:
            if doc_id in self.documents:
                del self.documents[doc_id]
            if doc_id in self.embeddings:
                del self.embeddings[doc_id]
            
            await self._save_data()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from local store: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get local store statistics."""
        return {
            "total_documents": len(self.documents),
            "total_embeddings": len(self.embeddings),
            "store_type": "local"
        }
    
    async def _save_data(self):
        """Save data to disk."""
        try:
            with open(self.store_path / "documents.json", 'w') as f:
                json.dump(self.documents, f, indent=2)
            
            with open(self.store_path / "embeddings.json", 'w') as f:
                json.dump(self.embeddings, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

class WeaviateStore(VectorStore):
    """Weaviate vector store implementation."""
    
    def __init__(self):
        super().__init__()
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize Weaviate connection."""
        if not WEAVIATE_AVAILABLE:
            logger.error("Weaviate not available")
            return False
        
        try:
            url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            api_key = os.getenv("WEAVIATE_API_KEY")
            
            if api_key:
                self.client = weaviate.Client(url, auth_client_secret=weaviate.AuthApiKey(api_key))
            else:
                self.client = weaviate.Client(url)
            
            # Create schema if it doesn't exist
            await self._create_schema()
            
            self.initialized = True
            logger.info("Weaviate vector store initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {e}")
            return False
    
    async def _create_schema(self):
        """Create Weaviate schema for documents."""
        try:
            schema = {
                "class": "Document",
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                    {"name": "type", "dataType": ["text"]},
                    {"name": "created_at", "dataType": ["date"]}
                ],
                "vectorizer": "text2vec-openai"
            }
            
            self.client.schema.create_class(schema)
            
        except Exception as e:
            logger.warning(f"Could not create Weaviate schema: {e}")
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to Weaviate."""
        if not self.initialized:
            return False
        
        try:
            for doc in documents:
                self.client.data_object.create(
                    class_name="Document",
                    data_object={
                        "text": doc["text"],
                        "source": doc.get("source", ""),
                        "type": doc.get("type", "document"),
                        "created_at": doc.get("created_at", "")
                    }
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Weaviate: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search Weaviate for similar documents."""
        if not self.initialized:
            return []
        
        try:
            result = self.client.query.get("Document", ["text", "source", "type"]).with_near_text({
                "concepts": [query]
            }).with_limit(top_k).do()
            
            return result["data"]["Get"]["Document"]
            
        except Exception as e:
            logger.error(f"Failed to search Weaviate: {e}")
            return []
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document from Weaviate."""
        if not self.initialized:
            return False
        
        try:
            self.client.data_object.delete(doc_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from Weaviate: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Weaviate statistics."""
        if not self.initialized:
            return {"error": "Not initialized"}
        
        try:
            result = self.client.query.aggregate("Document").with_meta_count().do()
            count = result["data"]["Aggregate"]["Document"][0]["meta"]["count"]
            
            return {
                "total_documents": count,
                "store_type": "weaviate"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Weaviate stats: {e}")
            return {"error": str(e)}

def get_vector_store() -> VectorStore:
    """Get the appropriate vector store based on configuration."""
    vector_db_type = os.getenv("VECTOR_DB_TYPE", "local")
    
    if vector_db_type == "pinecone" and PINECONE_AVAILABLE:
        return PineconeStore()
    elif vector_db_type == "weaviate" and WEAVIATE_AVAILABLE:
        return WeaviateStore()
    elif vector_db_type == "chroma" and CHROMA_AVAILABLE:
        # TODO: Implement ChromaStore
        return LocalVectorStore()
    else:
        return LocalVectorStore()

# Global vector store instance
vector_store = get_vector_store()

async def init_vector_store():
    """Initialize vector store."""
    await vector_store.initialize() 