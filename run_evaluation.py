#!/usr/bin/env python
"""
Complete evaluation script for HR Policy RAG.

Runs all evaluation tasks and generates results.md
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run complete evaluation."""
    logger.info("="*70)
    logger.info("HR POLICY RAG - COMPLETE EVALUATION")
    logger.info("="*70)
    
    try:
        # Import after logging is set up
        from config import DATA_DIR, RESULTS_DIR
        from metadata_extractor import extract_metadata_from_file, extract_document_body
        from chunkers import BasicChunker, StructureAwareChunker
        from embeddings import EmbeddingGenerator, VectorDatabase
        from evaluation_questions import (
            EVALUATION_QUESTIONS,
            ANSWERABLE_QUESTIONS,
            UNANSWERABLE_QUESTIONS,
        )
        
        logger.info(f"\n✓ All imports successful")
        logger.info(f"  Data directory: {DATA_DIR}")
        logger.info(f"  Results directory: {RESULTS_DIR}")
        
        # Initialize components
        logger.info("\n" + "="*70)
        logger.info("INITIALIZING RAG COMPONENTS")
        logger.info("="*70)
        
        logger.info("\n[1/4] Initializing embedding generator...")
        embedding_gen = EmbeddingGenerator("all-MiniLM-L6-v2")
        logger.info("  ✓ Embedding generator ready")
        
        logger.info("\n[2/4] Initializing vector database...")
        from config import CHROMA_DB_PATH
        vector_db = VectorDatabase(CHROMA_DB_PATH, embedding_gen)
        logger.info("  ✓ Vector database ready")
        
        logger.info("\n[3/4] Creating collections...")
        from config import BASIC_COLLECTION, STRUCTURED_COLLECTION
        basic_collection = vector_db.create_collection(BASIC_COLLECTION)
        structured_collection = vector_db.create_collection(STRUCTURED_COLLECTION)
        logger.info(f"  ✓ Basic collection: {BASIC_COLLECTION}")
        logger.info(f"  ✓ Structured collection: {STRUCTURED_COLLECTION}")
        
        logger.info("\n[4/4] Initializing chunkers...")
        from config import BASIC_CHUNK_CONFIG, STRUCTURED_CHUNK_CONFIG
        basic_chunker = BasicChunker(**BASIC_CHUNK_CONFIG)
        structured_chunker = StructureAwareChunker()
        logger.info("  ✓ Basic chunker ready")
        logger.info("  ✓ Structured chunker ready")
        
        # Ingest documents
        logger.info("\n" + "="*70)
        logger.info("INGESTING DOCUMENTS")
        logger.info("="*70)
        
        policy_files = sorted(DATA_DIR.glob("*.md"))
        total_basic = 0
        total_structured = 0
        
        for i, file_path in enumerate(policy_files, 1):
            logger.info(f"\n[{i}/{len(policy_files)}] Processing {file_path.name}...")
            
            # Extract metadata
            metadata = extract_metadata_from_file(file_path)
            logger.info(f"  Policy: {metadata['policy_id']}, Region: {metadata['region']}")
            
            # Extract body
            body = extract_document_body(file_path)
            
            # Basic chunking
            basic_chunks = basic_chunker.chunk(body, metadata)
            inserted_basic = vector_db.insert_chunks(
                basic_collection, basic_chunks, skip_duplicates=True
            )
            total_basic += inserted_basic
            logger.info(f"  ✓ Basic: {len(basic_chunks)} chunks ({inserted_basic} inserted)")
            
            # Structured chunking
            structured_chunks = structured_chunker.chunk(body, metadata)
            inserted_structured = vector_db.insert_chunks(
                structured_collection, structured_chunks, skip_duplicates=True
            )
            total_structured += inserted_structured
            logger.info(f"  ✓ Structured: {len(structured_chunks)} chunks ({inserted_structured} inserted)")
        
        logger.info(f"\n✓ Ingestion complete:")
        logger.info(f"  Total basic chunks: {total_basic}")
        logger.info(f"  Total structured chunks: {total_structured}")
        
        # Evaluation
        logger.info("\n" + "="*70)
        logger.info("RUNNING EVALUATIONS")
        logger.info("="*70)
        
        # 1. Retrieval evaluation
        logger.info("\n[EVALUATION] Retrieval on 8 questions...")
        
        retrieval_results = []
        basic_hits = 0
        structured_hits = 0
        
        for q in EVALUATION_QUESTIONS:
            qid = q["id"]
            question = q["question"]
            expected_policy = q["expected_policy_id"]
            expected_section = q["expected_section"]
            
            # Retrieve
            basic_res = vector_db.search(basic_collection, question, top_k=5)
            structured_res = vector_db.search(structured_collection, question, top_k=5)
            
            # Check hits
            def check_hit(results, policy, section):
                for r in results:
                    m = r["metadata"]
                    if m.get("policy_id") == policy and m.get("section") == section:
                        return True
                return False
            
            def find_rank(results, policy, section):
                for i, r in enumerate(results, 1):
                    m = r["metadata"]
                    if m.get("policy_id") == policy and m.get("section") == section:
                        return i
                return -1
            
            def get_score(results, policy, section):
                for r in results:
                    m = r["metadata"]
                    if m.get("policy_id") == policy and m.get("section") == section:
                        return r.get("score", 0)
                return 0.0
            
            basic_hit = check_hit(basic_res, expected_policy, expected_section)
            structured_hit = check_hit(structured_res, expected_policy, expected_section)
            
            if basic_hit:
                basic_hits += 1
            if structured_hit:
                structured_hits += 1
            
            basic_rank = find_rank(basic_res, expected_policy, expected_section)
            structured_rank = find_rank(structured_res, expected_policy, expected_section)
            basic_score = get_score(basic_res, expected_policy, expected_section)
            structured_score = get_score(structured_res, expected_policy, expected_section)
            
            logger.info(f"  {qid}: B={basic_hit} ({basic_rank}), S={structured_hit} ({structured_rank})")
            
            retrieval_results.append({
                "question_id": qid,
                "question": question,
                "expected_policy_id": expected_policy,
                "expected_section": expected_section,
                "basic_hit": basic_hit,
                "basic_rank": basic_rank,
                "basic_score": basic_score,
                "structured_hit": structured_hit,
                "structured_rank": structured_rank,
                "structured_score": structured_score,
            })
        
        logger.info(f"\n✓ Retrieval Evaluation Results:")
        logger.info(f"  Basic chunker:      {basic_hits}/8")
        logger.info(f"  Structured chunker: {structured_hits}/8")
        
        # 2. Metadata filtering
        logger.info("\n[EVALUATION] Metadata filtering...")
        
        query = "What is the carry-over cap for a probationary employee?"
        region = "Kerala"
        
        unfiltered = vector_db.search(structured_collection, query, top_k=5, where_filter=None)
        filtered = vector_db.search(
            structured_collection,
            query,
            top_k=5,
            where_filter={"region": {"$eq": region}}
        )
        
        logger.info(f"  Query: '{query}'")
        logger.info(f"  Filter region: {region}")
        logger.info(f"  ✓ Unfiltered: {len(unfiltered)} results")
        logger.info(f"  ✓ Filtered: {len(filtered)} results")
        
        filtering_results = {
            "query": query,
            "region_filter": region,
            "unfiltered_count": len(unfiltered),
            "filtered_count": len(filtered),
            "unfiltered_results": [
                {
                    "chunk_id": r["chunk_id"],
                    "region": r["metadata"].get("region", "unknown"),
                    "policy_id": r["metadata"].get("policy_id", "unknown"),
                    "score": r["score"],
                }
                for r in unfiltered
            ],
            "filtered_results": [
                {
                    "chunk_id": r["chunk_id"],
                    "region": r["metadata"].get("region", "unknown"),
                    "policy_id": r["metadata"].get("policy_id", "unknown"),
                    "score": r["score"],
                }
                for r in filtered
            ],
        }
        
        # 3. Generate answers (try with LLM if available)
        logger.info("\n[EVALUATION] Answerable questions...")
        
        answerable_results = []
        try:
            from generator import AnswerGenerator
            answer_gen = AnswerGenerator()
            
            for q in ANSWERABLE_QUESTIONS[:3]:
                qid = q["id"]
                question = q["question"]
                
                retrieved = vector_db.search(structured_collection, question, top_k=5)
                result = answer_gen.generate_answer(question, retrieved)
                
                logger.info(f"  {qid}: Generated answer")
                answerable_results.append({
                    "question_id": qid,
                    "question": question,
                    "answer": result.get("answer", "Error"),
                    "citations": result.get("citations", []),
                })
        except Exception as e:
            logger.warning(f"  Could not generate answers with LLM: {e}")
            logger.info("  Storing retrieval results instead")
            
            for q in ANSWERABLE_QUESTIONS[:3]:
                qid = q["id"]
                question = q["question"]
                
                retrieved = vector_db.search(structured_collection, question, top_k=5)
                
                answerable_results.append({
                    "question_id": qid,
                    "question": question,
                    "answer": "[Retrieval-only - LLM not available]",
                    "retrieved_chunks": [
                        {
                            "chunk_id": r["chunk_id"],
                            "policy_id": r["metadata"].get("policy_id", "unknown"),
                            "section": r["metadata"].get("section", "unknown"),
                            "score": r["score"],
                        }
                        for r in retrieved
                    ],
                })
        
        # 4. Unanswerable questions
        logger.info("\n[EVALUATION] Unanswerable questions...")
        
        unanswerable_results = []
        try:
            from generator import AnswerGenerator
            answer_gen = AnswerGenerator()
            
            for q in UNANSWERABLE_QUESTIONS[:3]:
                qid = q["id"]
                question = q["question"]
                reason = q.get("reason", "Unknown reason")
                
                retrieved = vector_db.search(structured_collection, question, top_k=5)
                result = answer_gen.generate_answer(question, retrieved)
                
                is_refused = "don't know" in result.get("answer", "").lower()
                logger.info(f"  {qid}: Refused={is_refused}")
                
                unanswerable_results.append({
                    "question_id": qid,
                    "question": question,
                    "expected_reason": reason,
                    "refused": is_refused,
                    "answer": result.get("answer", "Error"),
                })
        except Exception as e:
            logger.warning(f"  Could not test unanswerable with LLM: {e}")
            logger.info("  Storing expected refusals instead")
            
            for q in UNANSWERABLE_QUESTIONS[:3]:
                qid = q["id"]
                question = q["question"]
                reason = q.get("reason", "Unknown reason")
                
                unanswerable_results.append({
                    "question_id": qid,
                    "question": question,
                    "expected_reason": reason,
                    "answer": "[LLM not available for testing]",
                })
        
        # Compile results
        logger.info("\n" + "="*70)
        logger.info("COMPILING RESULTS")
        logger.info("="*70)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "basic_chunks_ingested": total_basic,
                "structured_chunks_ingested": total_structured,
            },
            "retrieval_evaluation": {
                "basic_score": f"{basic_hits}/8",
                "structured_score": f"{structured_hits}/8",
                "results": retrieval_results,
            },
            "metadata_filtering": filtering_results,
            "answerable_questions": answerable_results,
            "unanswerable_questions": unanswerable_results,
        }
        
        # Save JSON results
        json_output = RESULTS_DIR / "evaluation_results.json"
        with open(json_output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"\n✓ Results saved to {json_output}")
        
        # Generate results.md
        logger.info("\nGenerating results.md...")
        generate_results_md(results, RESULTS_DIR / "results.md")
        logger.info(f"✓ Results markdown saved")
        
        logger.info("\n" + "="*70)
        logger.info("EVALUATION COMPLETE")
        logger.info("="*70)
        logger.info(f"\nSummary:")
        logger.info(f"  Basic chunker Hit@5:      {results['retrieval_evaluation']['basic_score']}")
        logger.info(f"  Structured chunker Hit@5: {results['retrieval_evaluation']['structured_score']}")
        logger.info(f"  Total chunks ingested:    {total_basic + total_structured}")
        logger.info(f"\n✅ All evaluations complete!")
        
        return 0
    
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}", exc_info=True)
        return 1


def generate_results_md(results, output_file):
    """Generate results.md file."""
    
    md_content = """# Week 3 RAG Evaluation Results

## Documents

The evaluation ingested 6 regional HR policy addenda:

1. HR-202-Bangalore.md
2. HR-203-Chennai.md
3. HR-204-Hyderabad.md
4. HR-205-Pune.md
5. HR-206-Mumbai.md
6. HR-207-Kerala.md

Each document contains regional variations for leave policies with:
- Policy metadata (ID, region, effective date)
- Section 4.1: Annual Leave Eligibility
- Section 4.2: Carry-over Rules (with eligibility tables)
- Section 4.3: Regional Leave Tables
- Section 4.4: Leave Approval Process

## Metadata

Every chunk contains complete metadata:

- **source_file**: Name of the source policy document
- **policy_id**: HR policy identifier (e.g., HR-207)
- **region**: Geographic region (e.g., Kerala)
- **effective_date**: Policy effective date (2025-01-01)
- **section**: Section number (e.g., 4.2)
- **chunk_id**: Unique chunk identifier for citation

## Chunking Strategies

### Basic Chunker
- **Strategy**: Fixed-size chunks with sliding window
- **Configuration**: chunk_size=500, chunk_overlap=100
- **Approach**: Splits text into uniform chunks regardless of content structure
- **Advantage**: Simple and predictable
- **Disadvantage**: May split tables, sections, or important information across chunks

### Structure-Aware Chunker
- **Strategy**: Respects document structure (sections, tables)
- **Configuration**: max_chunk_size=1000
- **Approach**: Splits on section headers, keeps tables together
- **Advantage**: Preserves context and policy structure
- **Disadvantage**: May create variable-size chunks

## 8 Evaluation Questions

| ID | Question | Expected Policy | Expected Section |
|----|----------|-----------------|------------------|
| Q1 | What is the carry-over cap for a probationary employee under HR-207 section 4.2? | HR-207 | 4.2 |
| Q2 | What is the carry-over cap for a confirmed employee in Bangalore? | HR-202 | 4.2 |
| Q3 | What is the carry-over cap for a confirmed employee in Chennai? | HR-203 | 4.2 |
| Q4 | What is the carry-over cap for a confirmed employee in Hyderabad? | HR-204 | 4.2 |
| Q5 | How many casual/sick leaves are listed for Bangalore in section 4.3? | HR-202 | 4.3 |
| Q6 | How many privilege leaves are listed for Chennai in section 4.3? | HR-203 | 4.3 |
| Q7 | What is the carry-over cap for a confirmed employee in Pune? | HR-205 | 4.2 |
| Q8 | What is the carry-over cap for a confirmed employee in Mumbai? | HR-206 | 4.2 |

## Retrieval Results

### Hit@5 Performance

"""
    
    # Add retrieval table
    retrieval_results = results.get("retrieval_evaluation", {}).get("results", [])
    
    md_content += "| ID | Question | Expected Policy | Basic Rank | Basic Hit@5 | Structured Rank | Structured Hit@5 |\n"
    md_content += "|---|---|---|---|---|---|---|\n"
    
    for r in retrieval_results:
        basic_hit = "✓" if r.get("basic_hit") else "✗"
        structured_hit = "✓" if r.get("structured_hit") else "✗"
        basic_rank = r.get("basic_rank", -1)
        structured_rank = r.get("structured_rank", -1)
        
        basic_rank_str = str(basic_rank) if basic_rank > 0 else "—"
        structured_rank_str = str(structured_rank) if structured_rank > 0 else "—"
        
        md_content += f"| {r['question_id']} | {r['question'][:50]}... | {r['expected_policy_id']} | {basic_rank_str} | {basic_hit} | {structured_rank_str} | {structured_hit} |\n"
    
    # Add summary scores
    md_content += f"\n### Summary\n\n"
    md_content += f"**Basic Chunker**: {results['retrieval_evaluation']['basic_score']}\n\n"
    md_content += f"**Structured Chunker**: {results['retrieval_evaluation']['structured_score']}\n\n"
    
    # Add metadata filtering section
    md_content += "## Metadata Filtering\n\n"
    filtering = results.get("metadata_filtering", {})
    md_content += f"**Query**: {filtering.get('query', 'N/A')}\n\n"
    md_content += f"**Region Filter**: {filtering.get('region_filter', 'N/A')}\n\n"
    
    md_content += "### Unfiltered Results\n\n"
    for i, r in enumerate(filtering.get("unfiltered_results", []), 1):
        md_content += f"{i}. {r.get('chunk_id', 'N/A')} - Region: {r.get('region', 'N/A')}, Score: {r.get('score', 0):.3f}\n"
    
    md_content += "\n### Filtered Results (Region=Kerala)\n\n"
    for i, r in enumerate(filtering.get("filtered_results", []), 1):
        md_content += f"{i}. {r.get('chunk_id', 'N/A')} - Region: {r.get('region', 'N/A')}, Score: {r.get('score', 0):.3f}\n"
    
    # Add answerable questions section
    md_content += "\n## Answerable Questions\n\n"
    for q in results.get("answerable_questions", []):
        md_content += f"### {q.get('question_id', 'N/A')}\n\n"
        md_content += f"**Question**: {q.get('question', 'N/A')}\n\n"
        md_content += f"**Answer**: {q.get('answer', 'N/A')}\n\n"
        if q.get('citations'):
            md_content += f"**Citations**:\n\n"
            for c in q['citations'][:3]:
                md_content += f"- Chunk: {c.get('chunk_id', 'N/A')}\n"
                md_content += f"  Policy: {c.get('policy_id', 'N/A')}, Section: {c.get('section', 'N/A')}\n"
            md_content += "\n"
    
    # Add unanswerable questions section
    md_content += "## Unanswerable Questions\n\n"
    for q in results.get("unanswerable_questions", []):
        md_content += f"### {q.get('question_id', 'N/A')}\n\n"
        md_content += f"**Question**: {q.get('question', 'N/A')}\n\n"
        md_content += f"**Expected Reason**: {q.get('expected_reason', 'N/A')}\n\n"
        md_content += f"**Response**: {q.get('answer', 'N/A')}\n\n"
        if q.get('refused'):
            md_content += "**Status**: ✓ Refused\n\n"
        else:
            md_content += "**Status**: ✗ Not refused (may have hallucinated)\n\n"
    
    # Add summary
    md_content += "## Chunking Strategy Recommendation\n\n"
    basic_score = int(results['retrieval_evaluation']['basic_score'].split('/')[0])
    structured_score = int(results['retrieval_evaluation']['structured_score'].split('/')[0])
    
    if structured_score > basic_score:
        md_content += f"**Recommended**: Structure-Aware Chunker ({structured_score}/8 vs {basic_score}/8)\n\n"
        md_content += "The structure-aware chunker performs better because it respects policy section boundaries "
        md_content += "and keeps eligibility tables together with their section context. This ensures that queries "
        md_content += "about specific policy sections retrieve the correct chunks with all relevant information."
    elif basic_score > structured_score:
        md_content += f"**Recommended**: Basic Chunker ({basic_score}/8 vs {structured_score}/8)\n\n"
        md_content += "The basic chunker performs better in this evaluation. Despite its simpler approach, "
        md_content += "it may be more effective for this particular policy set."
    else:
        md_content += f"**Result**: Both chunkers perform equally ({basic_score}/8)\n\n"
        md_content += "Both chunking strategies achieve the same retrieval performance on this evaluation set. "
        md_content += "The structure-aware approach is recommended for production use as it better preserves context."
    
    md_content += "\n\n## Implementation Notes\n\n"
    md_content += f"- **Total documents ingested**: 6 policy addenda\n"
    md_content += f"- **Total chunks created** (basic): {results['summary'].get('basic_chunks_ingested', 0)}\n"
    md_content += f"- **Total chunks created** (structured): {results['summary'].get('structured_chunks_ingested', 0)}\n"
    md_content += f"- **Embedding model**: all-MiniLM-L6-v2\n"
    md_content += f"- **Vector database**: ChromaDB\n"
    md_content += f"- **Top-K retrieval**: 5\n"
    
    # Write to file
    with open(output_file, "w") as f:
        f.write(md_content)


if __name__ == "__main__":
    sys.exit(main())
