"""
Embeddings and vector database management.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        logger.info(f"Loaded embedding model: {model_name}")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class VectorDatabase:
    """Vector database using ChromaDB."""
    
    def __init__(self, db_path: str, embedding_generator: EmbeddingGenerator):
        """
        Initialize vector database.
        
        Args:
            db_path: Path to ChromaDB database
            embedding_generator: EmbeddingGenerator instance
        """
        self.db_path = db_path
        self.embedding_generator = embedding_generator
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        logger.info(f"Initialized ChromaDB at {db_path}")
    
    def create_collection(self, collection_name: str) -> Any:
        """
        Create or get a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection object
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except Exception:
            # Create new collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        return collection
    
    def insert_chunks(
        self,
        collection: Any,
        chunks: List[Dict[str, Any]],
        skip_duplicates: bool = True
    ) -> int:
        """
        Insert chunks into collection.
        
        Args:
            collection: Collection object
            chunks: List of chunks with text and metadata
            skip_duplicates: Skip chunks that already exist
            
        Returns:
            Number of chunks inserted
        """
        inserted = 0
        
        for i, chunk in enumerate(chunks):
            text = chunk["text"]
            metadata = chunk["metadata"]
            chunk_id = metadata["chunk_id"]
            
            # Check if chunk already exists
            if skip_duplicates:
                try:
                    existing = collection.get(ids=[chunk_id])
                    if existing and existing["ids"]:
                        logger.debug(f"Skipping duplicate chunk: {chunk_id}")
                        continue
                except Exception:
                    pass
            
            # Generate embedding
            embedding = self.embedding_generator.embed([text])[0]
            
            # Add to collection
            try:
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata],
                )
                inserted += 1
            except Exception as e:
                logger.error(f"Error inserting chunk {chunk_id}: {e}")
        
        logger.info(f"Inserted {inserted} chunks into collection")
        return inserted
    
    def search(
        self,
        collection: Any,
        query_text: str,
        top_k: int = 5,
        where_filter: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            collection: Collection object
            query_text: Query text
            top_k: Number of results to return
            where_filter: Metadata filter (e.g., {"region": "Kerala"})
            
        Returns:
            List of search results with text, metadata, and scores
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.embed([query_text])[0]
        
        # Search
        try:
            if where_filter:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"]
                )
            else:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
        except Exception as e:
            logger.error(f"Error searching collection: {e}")
            return []
        
        # Convert to standard format
        formatted_results = []
        
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, chunk_id in enumerate(results["ids"][0]):
                # Convert distance to similarity score (cosine distance to similarity)
                distance = results["distances"][0][i]
                score = 1 - distance  # Convert to similarity
                
                formatted_results.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "score": score,
                    "metadata": results["metadatas"][0][i],
                })
        
        return formatted_results
    
    def get_collection_size(self, collection: Any) -> int:
        """Get number of chunks in collection."""
        return collection.count()
