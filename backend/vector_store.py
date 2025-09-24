from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from typing import List, Dict, Any

class VectorStoreManager:
    """Manages Qdrant vector store operations"""
    
    def __init__(self):
        # Import configuration from config
        from config import EMBEDDING_MODEL, VECTOR_COLLECTION, VECTOR_SIZE
        
        self.embeddings = None
        self.client = None
        self.vector_store = None
        self.collection_name = VECTOR_COLLECTION
        self.vector_size = VECTOR_SIZE
        self.embedding_model = EMBEDDING_MODEL
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize embeddings, client and vector store"""
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        
        # Initialize Qdrant client (in-memory)
        self.client = QdrantClient(":memory:")
        
        # Create collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        
        # Create vector store
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
    
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]]):
        """Add documents to vector store"""
        print(f"Adding {len(documents)} documents to Qdrant vector store...")
        self.vector_store.add_texts(texts=documents, metadatas=metadatas)
        print("Documents added successfully!")
    
    def similarity_search_with_score(self, query: str, k: int = 3):
        """Search for similar documents"""
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    def get_vector_store(self):
        """Get the vector store instance"""
        return self.vector_store