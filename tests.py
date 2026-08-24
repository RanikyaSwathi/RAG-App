"""
Test suite for HR Policy RAG.
"""

import pytest
from pathlib import Path
import tempfile
import yaml
import json

from metadata_extractor import extract_metadata_from_file, extract_document_body
from chunkers import BasicChunker, StructureAwareChunker
from embeddings import EmbeddingGenerator, VectorDatabase
from config import EMBEDDING_MODEL


class TestMetadataExtraction:
    """Tests for metadata extraction."""
    
    def test_extract_metadata_from_file(self):
        """Test extracting metadata from a file."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
policy_id: HR-202
region: Bangalore
effective_date: 2025-01-01
source_type: synthetic_training_addendum
---

# Test Content

Some content here.
""")
            temp_file = Path(f.name)
        
        try:
            metadata = extract_metadata_from_file(temp_file)
            
            assert metadata["policy_id"] == "HR-202"
            assert metadata["region"] == "Bangalore"
            assert metadata["effective_date"] == "2025-01-01"
            assert metadata["source_file"] == temp_file.name
        finally:
            temp_file.unlink()
    
    def test_extract_document_body(self):
        """Test extracting document body."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
policy_id: HR-202
region: Bangalore
effective_date: 2025-01-01
---

# Header

Content here.
""")
            temp_file = Path(f.name)
        
        try:
            body = extract_document_body(temp_file)
            
            assert "# Header" in body
            assert "Content here" in body
            assert "---" not in body
            assert "policy_id" not in body
        finally:
            temp_file.unlink()


class TestBasicChunker:
    """Tests for basic chunker."""
    
    def test_basic_chunking(self):
        """Test basic fixed-size chunking."""
        chunker = BasicChunker(chunk_size=100, chunk_overlap=20)
        
        text = "This is a test document. " * 20  # Create text longer than chunk_size
        metadata = {
            "source_file": "test.md",
            "policy_id": "HR-202",
            "region": "Bangalore",
            "effective_date": "2025-01-01",
            "section": "4.2",
        }
        
        chunks = chunker.chunk(text, metadata)
        
        assert len(chunks) > 1
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
        assert all(chunk["metadata"]["source_file"] == "test.md" for chunk in chunks)
        assert all(chunk["metadata"]["chunk_type"] == "basic" for chunk in chunks)
    
    def test_chunk_metadata_complete(self):
        """Test that metadata is complete in chunks."""
        chunker = BasicChunker(chunk_size=100, chunk_overlap=20)
        
        text = "Test content. " * 30
        metadata = {
            "source_file": "test.md",
            "policy_id": "HR-202",
            "region": "Bangalore",
            "effective_date": "2025-01-01",
            "section": "4.2",
        }
        
        chunks = chunker.chunk(text, metadata)
        
        for chunk in chunks:
            chunk_meta = chunk["metadata"]
            assert chunk_meta["source_file"] == "test.md"
            assert chunk_meta["policy_id"] == "HR-202"
            assert chunk_meta["region"] == "Bangalore"
            assert chunk_meta["effective_date"] == "2025-01-01"
            assert "chunk_id" in chunk_meta


class TestStructureAwareChunker:
    """Tests for structure-aware chunker."""
    
    def test_structured_chunking(self):
        """Test structure-aware chunking."""
        chunker = StructureAwareChunker(max_chunk_size=1000)
        
        text = """## 4.1 Annual Leave Eligibility

Employees follow the company's annual leave process.

## 4.2 Carry-over Rule

| Employee status | Carry-over cap |
|---|---:|
| Probationary | 2 days |
| Confirmed | 9 days |

## 4.3 Regional Table

| Region | Casual/Sick | Privilege |
|---|---:|---:|
| Region | 15 | 3 |
"""
        
        metadata = {
            "source_file": "test.md",
            "policy_id": "HR-202",
            "region": "Bangalore",
            "effective_date": "2025-01-01",
            "section": "4.2",
        }
        
        chunks = chunker.chunk(text, metadata)
        
        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
        assert all("4." in chunk["metadata"].get("section", "") for chunk in chunks)


class TestEmbeddingGenerator:
    """Tests for embedding generation."""
    
    def test_embedding_generation(self):
        """Test that embeddings are generated."""
        generator = EmbeddingGenerator(EMBEDDING_MODEL)
        
        texts = [
            "What is the carry-over cap?",
            "How many days of leave?",
        ]
        
        embeddings = generator.embed(texts)
        
        assert len(embeddings) == len(texts)
        assert len(embeddings[0]) > 0
        assert isinstance(embeddings[0], list)
        assert isinstance(embeddings[0][0], float)
    
    def test_embedding_similarity(self):
        """Test that similar texts have similar embeddings."""
        generator = EmbeddingGenerator(EMBEDDING_MODEL)
        
        texts = [
            "What is the carry-over cap for probationary employees?",
            "What is the carry-over cap for confirmed employees?",
            "What is the weather today?",
        ]
        
        embeddings = generator.embed(texts)
        
        # Calculate similarities (simple dot product)
        def cosine_similarity(a, b):
            dot = sum(x*y for x, y in zip(a, b))
            norm_a = sum(x*x for x in a) ** 0.5
            norm_b = sum(x*x for x in b) ** 0.5
            return dot / (norm_a * norm_b)
        
        sim_01 = cosine_similarity(embeddings[0], embeddings[1])
        sim_02 = cosine_similarity(embeddings[0], embeddings[2])
        sim_12 = cosine_similarity(embeddings[1], embeddings[2])
        
        # First two should be more similar than the first and third
        assert sim_01 > sim_02
        assert sim_01 > sim_12


class TestVectorDatabase:
    """Tests for vector database."""
    
    def test_vector_db_operations(self):
        """Test basic vector DB operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = EmbeddingGenerator(EMBEDDING_MODEL)
            db = VectorDatabase(tmpdir, generator)
            
            # Create collection
            collection = db.create_collection("test_collection")
            assert collection is not None
            
            # Insert chunks
            chunks = [
                {
                    "text": "What is the carry-over cap for probationary employees?",
                    "metadata": {
                        "chunk_id": "HR-202-1",
                        "policy_id": "HR-202",
                        "region": "Bangalore",
                        "section": "4.2",
                        "source_file": "HR-202-Bangalore.md",
                    }
                },
                {
                    "text": "Probationary employees have a carry-over cap of 2 days.",
                    "metadata": {
                        "chunk_id": "HR-202-2",
                        "policy_id": "HR-202",
                        "region": "Bangalore",
                        "section": "4.2",
                        "source_file": "HR-202-Bangalore.md",
                    }
                }
            ]
            
            inserted = db.insert_chunks(collection, chunks)
            assert inserted >= 0
            
            # Search
            results = db.search(collection, "carry-over cap", top_k=5)
            assert len(results) > 0
            assert "chunk_id" in results[0]
            assert "text" in results[0]
            assert "score" in results[0]
            assert "metadata" in results[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
