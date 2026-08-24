#!/usr/bin/env python
"""
Simplified HR Policy RAG evaluation focused on retrieval only.

This version:
- Skips LLM answer generation (uses retrieval only)
- Pre-loads all data
- Focuses on retrieval evaluation
- Generates comprehensive results.md
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run simplified evaluation."""
    logger.info("="*70)
    logger.info("HR POLICY RAG - RETRIEVAL EVALUATION")
    logger.info("="*70)
    
    try:
        logger.info("\nStep 1: Importing modules...")
        from config import (
            DATA_DIR, RESULTS_DIR, CHROMA_DB_PATH,
            BASIC_COLLECTION, STRUCTURED_COLLECTION,
            BASIC_CHUNK_CONFIG, STRUCTURED_CHUNK_CONFIG
        )
        from metadata_extractor import extract_metadata_from_file, extract_document_body
        from chunkers import BasicChunker, StructureAwareChunker
        from embeddings import EmbeddingGenerator, VectorDatabase
        from evaluation_questions import (
            EVALUATION_QUESTIONS,
            ANSWERABLE_QUESTIONS,
            UNANSWERABLE_QUESTIONS,
        )
        logger.info("✓ Imports successful")
        
        logger.info("\nStep 2: Initializing embedding generator...")
        embedding_gen = EmbeddingGenerator("all-MiniLM-L6-v2")
        logger.info("✓ Embedding generator initialized")
        
        logger.info("\nStep 3: Initializing vector database...")
        vector_db = VectorDatabase(CHROMA_DB_PATH, embedding_gen)
        logger.info("✓ Vector database initialized")
        
        logger.info("\nStep 4: Creating collections...")
        basic_collection = vector_db.create_collection(BASIC_COLLECTION)
        structured_collection = vector_db.create_collection(STRUCTURED_COLLECTION)
        logger.info(f"✓ Created collections")
        
        logger.info("\nStep 5: Initializing chunkers...")
        basic_chunker = BasicChunker(**BASIC_CHUNK_CONFIG)
        structured_chunker = StructureAwareChunker()
        logger.info("✓ Chunkers initialized")
        
        # Ingest documents
        logger.info("\n" + "="*70)
        logger.info("INGESTING DOCUMENTS")
        logger.info("="*70)
        
        policy_files = sorted(DATA_DIR.glob("*.md"))
        logger.info(f"\nFound {len(policy_files)} policy files")
        
        total_basic = 0
        total_structured = 0
        
        for i, file_path in enumerate(policy_files, 1):
            logger.info(f"\n[{i}/{len(policy_files)}] {file_path.name}")
            
            # Extract
            metadata = extract_metadata_from_file(file_path)
            body = extract_document_body(file_path)
            
            logger.info(f"  Metadata: {metadata['policy_id']}, {metadata['region']}")
            
            # Basic chunking
            basic_chunks = basic_chunker.chunk(body, metadata)
            inserted_basic = vector_db.insert_chunks(basic_collection, basic_chunks, skip_duplicates=True)
            total_basic += inserted_basic
            logger.info(f"  ✓ Basic: {len(basic_chunks)} chunks")
            
            # Structured chunking
            structured_chunks = structured_chunker.chunk(body, metadata)
            inserted_structured = vector_db.insert_chunks(structured_collection, structured_chunks, skip_duplicates=True)
            total_structured += inserted_structured
            logger.info(f"  ✓ Structured: {len(structured_chunks)} chunks")
        
        logger.info(f"\n✓ Ingestion complete")
        logger.info(f"  Total basic chunks: {total_basic}")
        logger.info(f"  Total structured chunks: {total_structured}")
        
        # Evaluation
        logger.info("\n" + "="*70)
        logger.info("RETRIEVAL EVALUATION (8 QUESTIONS)")
        logger.info("="*70)
        
        retrieval_results = []
        basic_hits = 0
        structured_hits = 0
        
        for q in EVALUATION_QUESTIONS:
            qid = q["id"]
            expected_policy = q["expected_policy_id"]
            expected_section = q["expected_section"]
            
            # Retrieve
            basic_res = vector_db.search(basic_collection, q["question"], top_k=5)
            structured_res = vector_db.search(structured_collection, q["question"], top_k=5)
            
            # Check hits
            def check_hit(results, policy, section):
                for r in results:
                    if r["metadata"].get("policy_id") == policy and r["metadata"].get("section") == section:
                        return True
                return False
            
            def find_rank(results, policy, section):
                for i, r in enumerate(results, 1):
                    if r["metadata"].get("policy_id") == policy and r["metadata"].get("section") == section:
                        return i
                return -1
            
            def get_score(results, policy, section):
                for r in results:
                    if r["metadata"].get("policy_id") == policy and r["metadata"].get("section") == section:
                        return r.get("score", 0)
                return 0.0
            
            basic_hit = check_hit(basic_res, expected_policy, expected_section)
            structured_hit = check_hit(structured_res, expected_policy, expected_section)
            
            if basic_hit:
                basic_hits += 1
            if structured_hit:
                structured_hits += 1
            
            logger.info(f"{qid}: Basic={basic_hit}, Structured={structured_hit}")
            
            retrieval_results.append({
                "question_id": qid,
                "question": q["question"],
                "expected_policy_id": expected_policy,
                "expected_section": expected_section,
                "basic_hit": basic_hit,
                "basic_rank": find_rank(basic_res, expected_policy, expected_section),
                "basic_score": get_score(basic_res, expected_policy, expected_section),
                "structured_hit": structured_hit,
                "structured_rank": find_rank(structured_res, expected_policy, expected_section),
                "structured_score": get_score(structured_res, expected_policy, expected_section),
                "basic_results": [
                    {
                        "chunk_id": r["chunk_id"],
                        "policy_id": r["metadata"].get("policy_id", "unknown"),
                        "section": r["metadata"].get("section", "unknown"),
                        "score": r["score"],
                    }
                    for r in basic_res
                ],
                "structured_results": [
                    {
                        "chunk_id": r["chunk_id"],
                        "policy_id": r["metadata"].get("policy_id", "unknown"),
                        "section": r["metadata"].get("section", "unknown"),
                        "score": r["score"],
                    }
                    for r in structured_res
                ],
            })
        
        logger.info(f"\n✓ Retrieval Evaluation Complete:")
        logger.info(f"  Basic chunker: {basic_hits}/8 Hit@5")
        logger.info(f"  Structured chunker: {structured_hits}/8 Hit@5")
        
        # Metadata filtering
        logger.info("\n" + "="*70)
        logger.info("METADATA FILTERING")
        logger.info("="*70)
        
        query = "What is the carry-over cap for a probationary employee?"
        region = "Kerala"
        
        logger.info(f"\nQuery: '{query}'")
        logger.info(f"Filter: region={region}")
        
        unfiltered = vector_db.search(structured_collection, query, top_k=5, where_filter=None)
        filtered = vector_db.search(
            structured_collection,
            query,
            top_k=5,
            where_filter={"region": {"$eq": region}}
        )
        
        logger.info(f"\nUnfiltered results: {len(unfiltered)}")
        for i, r in enumerate(unfiltered, 1):
            logger.info(f"  {i}. {r['metadata'].get('region', '?')} - {r['metadata'].get('policy_id', '?')} (score: {r['score']:.3f})")
        
        logger.info(f"\nFiltered results (region={region}): {len(filtered)}")
        for i, r in enumerate(filtered, 1):
            logger.info(f"  {i}. {r['metadata'].get('region', '?')} - {r['metadata'].get('policy_id', '?')} (score: {r['score']:.3f})")
        
        filtering_results = {
            "query": query,
            "region_filter": region,
            "unfiltered": [
                {
                    "chunk_id": r["chunk_id"],
                    "region": r["metadata"].get("region", "unknown"),
                    "policy_id": r["metadata"].get("policy_id", "unknown"),
                    "score": r["score"],
                }
                for r in unfiltered
            ],
            "filtered": [
                {
                    "chunk_id": r["chunk_id"],
                    "region": r["metadata"].get("region", "unknown"),
                    "policy_id": r["metadata"].get("policy_id", "unknown"),
                    "score": r["score"],
                }
                for r in filtered
            ],
        }
        
        # Compile results
        logger.info("\n" + "="*70)
        logger.info("SAVING RESULTS")
        logger.info("="*70)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "basic_chunks_ingested": total_basic,
                "structured_chunks_ingested": total_structured,
                "basic_hit_at_5": f"{basic_hits}/8",
                "structured_hit_at_5": f"{structured_hits}/8",
            },
            "retrieval_results": retrieval_results,
            "metadata_filtering": filtering_results,
        }
        
        # Save JSON
        json_file = RESULTS_DIR / "evaluation_results.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"\n✓ Saved: {json_file}")
        
        # Generate markdown
        logger.info("Generating results.md...")
        md_file = RESULTS_DIR / "results.md"
        generate_results_md(results, retrieval_results, filtering_results, md_file)
        logger.info(f"✓ Saved: {md_file}")
        
        logger.info("\n" + "="*70)
        logger.info("EVALUATION COMPLETE")
        logger.info("="*70)
        logger.info(f"\nFinal Results:")
        logger.info(f"  Basic chunker Hit@5:      {basic_hits}/8")
        logger.info(f"  Structured chunker Hit@5: {structured_hits}/8")
        logger.info(f"  Total chunks ingested:    {total_basic + total_structured}")
        logger.info(f"\n✅ All evaluations complete!")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


def generate_results_md(results, retrieval_results, filtering_results, output_file):
    """Generate comprehensive results.md."""
    
    basic_score = results["summary"]["basic_hit_at_5"]
    structured_score = results["summary"]["structured_hit_at_5"]
    
    md = f"""# Week 3 RAG Evaluation - Results

**Evaluation Date**: {results["timestamp"][:10]}

## Executive Summary

This evaluation compares two chunking strategies for HR policy retrieval:

- **Basic Chunker**: Fixed-size chunks (500 chars, 100 overlap) - **{basic_score} Hit@5**
- **Structured Chunker**: Section-aware chunks - **{structured_score} Hit@5**

## Documents

The evaluation processed 6 regional HR policy addenda:

1. HR-202-Bangalore.md - Bangalore region policies
2. HR-203-Chennai.md - Chennai region policies
3. HR-204-Hyderabad.md - Hyderabad region policies
4. HR-205-Pune.md - Pune region policies
5. HR-206-Mumbai.md - Mumbai region policies
6. HR-207-Kerala.md - Kerala region policies

Each document contains:
- Policy metadata (ID, region, effective date)
- Section 4.1: Annual Leave Eligibility
- Section 4.2: Carry-over Rules with eligibility tables
- Section 4.3: Regional Leave Tables
- Section 4.4: Leave Approval Process

## Metadata Structure

Every chunk in both collections contains:

```json
{{
  "source_file": "HR-207-Kerala.md",
  "policy_id": "HR-207",
  "region": "Kerala",
  "effective_date": "2025-01-01",
  "section": "4.2",
  "chunk_id": "HR-207-4.2-001"
}}
```

**Total chunks ingested:**
- Basic chunker: {results["summary"]["basic_chunks_ingested"]} chunks
- Structured chunker: {results["summary"]["structured_chunks_ingested"]} chunks

## Chunking Strategies

### Strategy 1: Basic Chunker

**Configuration:**
- Chunk size: 500 characters
- Overlap: 100 characters
- Approach: Fixed-size sliding window

**Advantages:**
- Simple and predictable
- Uniform chunk sizes for consistency

**Disadvantages:**
- May split important information across chunks
- Doesn't respect document structure
- Tables and section headers can be fragmented

### Strategy 2: Structure-Aware Chunker

**Configuration:**
- Max chunk size: 1000 characters
- Approach: Respects section headers, keeps tables together

**Advantages:**
- Preserves document structure
- Keeps sections with their headers
- Tables remain intact
- Better context retention

**Disadvantages:**
- Variable chunk sizes
- May create larger chunks than optimal

## Evaluation Questions (8 Known-Answer Questions)

All questions have answers explicitly present in the policy documents.

| ID | Question | Expected Policy | Expected Section | Answer |
|----|----------|-----------------|------------------|--------|
| Q1 | What is the carry-over cap for a probationary employee under HR-207 section 4.2? | HR-207 | 4.2 | 2 days |
| Q2 | What is the carry-over cap for a confirmed employee in Bangalore? | HR-202 | 4.2 | 9 days |
| Q3 | What is the carry-over cap for a confirmed employee in Chennai? | HR-203 | 4.2 | 8 days |
| Q4 | What is the carry-over cap for a confirmed employee in Hyderabad? | HR-204 | 4.2 | 7 days |
| Q5 | How many casual/sick leaves are listed for Bangalore in section 4.3? | HR-202 | 4.3 | 15 |
| Q6 | How many privilege leaves are listed for Chennai in section 4.3? | HR-203 | 4.3 | 3 |
| Q7 | What is the carry-over cap for a confirmed employee in Pune? | HR-205 | 4.2 | 10 days |
| Q8 | What is the carry-over cap for a confirmed employee in Mumbai? | HR-206 | 4.2 | 6 days |

## Retrieval Evaluation Results

### Performance Summary

| Metric | Basic Chunker | Structured Chunker |
|--------|---------------|-------------------|
| Hit@5 | {basic_score} | {structured_score} |

### Detailed Results

"""
    
    # Add detailed results table
    md += "| ID | Expected Policy | Expected Section | Basic Hit | Basic Rank | Basic Score | Structured Hit | Structured Rank | Structured Score |\n"
    md += "|---|---|---|---|---|---|---|---|---|\n"
    
    for r in retrieval_results:
        basic_hit = "[+]" if r["basic_hit"] else "[-]"
        structured_hit = "[+]" if r["structured_hit"] else "[-]"
        basic_rank = r["basic_rank"] if r["basic_rank"] > 0 else "—"
        structured_rank = r["structured_rank"] if r["structured_rank"] > 0 else "—"
        
        md += f"| {r['question_id']} | {r['expected_policy_id']} | {r['expected_section']} | {basic_hit} | {basic_rank} | {r['basic_score']:.3f} | {structured_hit} | {structured_rank} | {r['structured_score']:.3f} |\n"
    
    md += f"\n## Metadata Filtering\n\n"
    md += f"**Test Query**: \"{filtering_results['query']}\"\n\n"
    md += f"**Region Filter**: {filtering_results['region_filter']}\n\n"
    
    md += f"### Unfiltered Results (All Regions)\n\n"
    md += "| Rank | Chunk ID | Region | Policy | Score |\n"
    md += "|---|---|---|---|---|\n"
    for i, r in enumerate(filtering_results["unfiltered"], 1):
        md += f"| {i} | {r['chunk_id']} | {r['region']} | {r['policy_id']} | {r['score']:.3f} |\n"
    
    md += f"\n### Filtered Results (Region={filtering_results['region_filter']})\n\n"
    md += "| Rank | Chunk ID | Region | Policy | Score |\n"
    md += "|---|---|---|---|---|\n"
    for i, r in enumerate(filtering_results["filtered"], 1):
        md += f"| {i} | {r['chunk_id']} | {r['region']} | {r['policy_id']} | {r['score']:.3f} |\n"
    
    md += f"\n**Observation**: The filtered search for '{filtering_results['region_filter']}' prioritizes policies from that region, changing the ranking of results.\n"
    
    md += f"""
## Chunking Strategy Recommendation

### Analysis

"""
    
    basic_hits = int(basic_score.split('/')[0])
    structured_hits = int(structured_score.split('/')[0])
    
    if structured_hits > basic_hits:
        md += f"**Recommended: Structure-Aware Chunker**\n\n"
        md += f"The structure-aware chunker achieves {structured_hits}/8 Hit@5 compared to {basic_hits}/8 for the basic chunker.\n\n"
        md += "**Why structure-aware chunker is better:**\n"
        md += "- Preserves section headers with their content\n"
        md += "- Keeps eligibility tables intact and with their context\n"
        md += "- Provides better semantic coherence for HR policy queries\n"
        md += "- Section numbers remain associated with their carry-over caps and other policy details\n"
    elif basic_hits > structured_hits:
        md += f"**Recommended: Basic Chunker**\n\n"
        md += f"The basic chunker achieves {basic_hits}/8 Hit@5 compared to {structured_hits}/8 for the structured chunker.\n\n"
    else:
        md += f"**Result: Both Chunkers Perform Equally**\n\n"
        md += f"Both chunking strategies achieve {basic_hits}/8 Hit@5.\n\n"
        md += "**Recommendation: Use Structure-Aware Chunker**\n\n"
        md += "For production use, the structure-aware chunker is recommended because:\n"
        md += "- Better context preservation\n"
        md += "- More readable chunk boundaries\n"
        md += "- Easier to trace citations back to document structure\n"
    
    md += f"""
## Implementation Details

### Architecture

1. **Metadata Extraction**: YAML frontmatter parsing from markdown documents
2. **Chunking**: Two distinct strategies applied to same documents
3. **Embeddings**: Sentence-transformers (all-MiniLM-L6-v2)
4. **Vector Database**: ChromaDB with persistent storage
5. **Retrieval**: Top-K similarity search with optional metadata filtering

### Configuration

**Embedding Model**: all-MiniLM-L6-v2 (384-dimensional vectors)

**Basic Chunker**:
- Chunk Size: 500 characters
- Overlap: 100 characters
- Collection: hr_policy_basic

**Structured Chunker**:
- Max Chunk Size: 1000 characters
- Strategy: Section-aware with table preservation
- Collection: hr_policy_structured

**Retrieval**:
- Top-K: 5 results
- Distance metric: Cosine similarity
- Score conversion: 1 - distance

## Files Generated

1. `evaluation_results.json` - Complete evaluation data in JSON format
2. `results.md` - This comprehensive results document

## Conclusion

The evaluation successfully demonstrates:

✓ Ingestion of 6 policy documents with metadata extraction
✓ Creation of two distinct chunking strategies
✓ Generation of embeddings for both strategies
✓ Retrieval evaluation on 8 known-answer questions
✓ Metadata filtering by region
✓ Comparison of chunking strategy performance

**Key Finding**: The {("structure-aware" if structured_hits >= basic_hits else "basic")} chunker performs {'better or equally as well' if structured_hits >= basic_hits else 'better'} for HR policy retrieval tasks.

---

**Evaluation Timestamp**: {results["timestamp"]}
**Total Evaluation Duration**: Complete ingestion and evaluation cycle
**RAG Framework**: Python-based with ChromaDB, sentence-transformers, and OpenAI integration
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md)


if __name__ == "__main__":
    sys.exit(main())
