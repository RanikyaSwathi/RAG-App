#!/usr/bin/env python
"""
Quick test script to verify RAG components work.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Testing imports...")
    
    from config import DATA_DIR, EMBEDDING_MODEL
    logger.info(f"✓ Config loaded. DATA_DIR={DATA_DIR}")
    
    from metadata_extractor import extract_metadata_from_file
    logger.info("✓ Metadata extractor loaded")
    
    from chunkers import BasicChunker, StructureAwareChunker
    logger.info("✓ Chunkers loaded")
    
    from embeddings import EmbeddingGenerator
    logger.info("✓ Embeddings module loaded")
    
    logger.info("\nAll imports successful!")
    
    # Test metadata extraction
    logger.info("\nTesting metadata extraction...")
    test_file = DATA_DIR / "HR-207-Kerala.md"
    if test_file.exists():
        metadata = extract_metadata_from_file(test_file)
        logger.info(f"✓ Metadata extracted from {test_file.name}")
        logger.info(f"  Policy ID: {metadata['policy_id']}")
        logger.info(f"  Region: {metadata['region']}")
        logger.info(f"  Section: {metadata.get('section', 'N/A')}")
    else:
        logger.error(f"Test file not found: {test_file}")
        sys.exit(1)
    
    # Test chunking
    logger.info("\nTesting chunking...")
    from metadata_extractor import extract_document_body
    body = extract_document_body(test_file)
    
    basic_chunker = BasicChunker(chunk_size=500, chunk_overlap=100)
    basic_chunks = basic_chunker.chunk(body, metadata)
    logger.info(f"✓ Basic chunker: {len(basic_chunks)} chunks created")
    
    structured_chunker = StructureAwareChunker()
    structured_chunks = structured_chunker.chunk(body, metadata)
    logger.info(f"✓ Structured chunker: {len(structured_chunks)} chunks created")
    
    logger.info("\n✅ All tests passed!")
    
except Exception as e:
    logger.error(f"❌ Error: {e}", exc_info=True)
    sys.exit(1)
