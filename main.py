"""
Main RAG application for HR policy question answering.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

from config import (
    DATA_DIR,
    VECTOR_DB_DIR,
    BASIC_COLLECTION,
    STRUCTURED_COLLECTION,
    CHROMA_DB_PATH,
    DEFAULT_TOP_K,
    BASIC_CHUNK_CONFIG,
    STRUCTURED_CHUNK_CONFIG,
    EMBEDDING_MODEL,
)

from metadata_extractor import extract_metadata_from_file, extract_document_body
from chunkers import BasicChunker, StructureAwareChunker
from embeddings import EmbeddingGenerator, VectorDatabase
from generator import AnswerGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HRPolicyRAG:
    """Main RAG application."""
    
    def __init__(self):
        """Initialize the RAG application."""
        # Initialize embedding generator
        self.embedding_generator = EmbeddingGenerator(EMBEDDING_MODEL)
        
        # Initialize vector database
        self.vector_db = VectorDatabase(CHROMA_DB_PATH, self.embedding_generator)
        
        # Initialize chunkers
        self.basic_chunker = BasicChunker(**BASIC_CHUNK_CONFIG)
        self.structured_chunker = StructureAwareChunker()
        
        # Initialize answer generator
        self.answer_generator = AnswerGenerator()
        
        # Initialize collections
        self.basic_collection = self.vector_db.create_collection(BASIC_COLLECTION)
        self.structured_collection = self.vector_db.create_collection(STRUCTURED_COLLECTION)
        
        logger.info("HR Policy RAG initialized")
    
    def ingest_documents(self) -> Tuple[int, int]:
        """
        Ingest all policy documents into both chunkers.
        
        Returns:
            Tuple of (basic_chunks_count, structured_chunks_count)
        """
        policy_files = sorted(DATA_DIR.glob("*.md"))
        
        if not policy_files:
            logger.error(f"No policy files found in {DATA_DIR}")
            return 0, 0
        
        total_basic = 0
        total_structured = 0
        
        for file_path in policy_files:
            logger.info(f"Processing {file_path.name}")
            
            try:
                # Extract metadata
                metadata = extract_metadata_from_file(file_path)
                logger.info(f"  Metadata: policy_id={metadata['policy_id']}, region={metadata['region']}")
                
                # Extract document body
                body = extract_document_body(file_path)
                
                # Basic chunking
                basic_chunks = self.basic_chunker.chunk(body, metadata)
                inserted_basic = self.vector_db.insert_chunks(
                    self.basic_collection,
                    basic_chunks,
                    skip_duplicates=True
                )
                total_basic += inserted_basic
                logger.info(f"  Basic chunks: {len(basic_chunks)} (inserted: {inserted_basic})")
                
                # Structured chunking
                structured_chunks = self.structured_chunker.chunk(body, metadata)
                inserted_structured = self.vector_db.insert_chunks(
                    self.structured_collection,
                    structured_chunks,
                    skip_duplicates=True
                )
                total_structured += inserted_structured
                logger.info(f"  Structured chunks: {len(structured_chunks)} (inserted: {inserted_structured})")
            
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
        
        logger.info(f"Total chunks ingested - Basic: {total_basic}, Structured: {total_structured}")
        return total_basic, total_structured
    
    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        collection_type: str = "basic",
        region_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-K relevant chunks.
        
        Args:
            query: Query text
            top_k: Number of results to return
            collection_type: "basic" or "structured"
            region_filter: Optional region to filter by
            
        Returns:
            List of retrieved chunks with metadata and scores
        """
        collection = (
            self.basic_collection if collection_type == "basic"
            else self.structured_collection
        )
        
        where_filter = None
        if region_filter:
            where_filter = {"region": {"$eq": region_filter}}
        
        results = self.vector_db.search(
            collection,
            query,
            top_k=top_k,
            where_filter=where_filter
        )
        
        return results
    
    def retrieve_both(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        region_filter: str = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Retrieve from both chunking strategies.
        
        Returns:
            Tuple of (basic_results, structured_results)
        """
        basic_results = self.retrieve(query, top_k, "basic", region_filter)
        structured_results = self.retrieve(query, top_k, "structured", region_filter)
        return basic_results, structured_results
    
    def generate_answer(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
        collection_type: str = "structured"
    ) -> Dict[str, Any]:
        """
        Generate answer for a question.
        
        Args:
            question: Question to answer
            top_k: Number of chunks to retrieve
            collection_type: "basic" or "structured"
            
        Returns:
            Dictionary with answer and citations
        """
        # Retrieve
        retrieved = self.retrieve(question, top_k, collection_type)
        
        if not retrieved:
            return {
                "question": question,
                "answer": "I don't know. The provided HR policy documents do not contain this information.",
                "citations": [],
                "retrieved_chunks_count": 0,
                "success": False,
            }
        
        # Generate
        result = self.answer_generator.generate_answer(question, retrieved)
        
        return result
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about collections."""
        return {
            "basic_collection_size": self.vector_db.get_collection_size(self.basic_collection),
            "structured_collection_size": self.vector_db.get_collection_size(self.structured_collection),
        }


if __name__ == "__main__":
    # Initialize RAG
    rag = HRPolicyRAG()
    
    # Ingest documents
    basic_count, structured_count = rag.ingest_documents()
    
    # Print stats
    stats = rag.get_collection_stats()
    print(f"\nCollection stats: {stats}")
    
    # Test query
    test_query = "What is the carry-over cap for a probationary employee in Kerala?"
    print(f"\nTest query: {test_query}")
    
    basic_results, structured_results = rag.retrieve_both(test_query, top_k=5)
    
    print(f"\nBasic chunker results:")
    for i, result in enumerate(basic_results, 1):
        print(f"  {i}. {result['metadata']['chunk_id']} (score: {result['score']:.3f})")
    
    print(f"\nStructured chunker results:")
    for i, result in enumerate(structured_results, 1):
        print(f"  {i}. {result['metadata']['chunk_id']} (score: {result['score']:.3f})")
