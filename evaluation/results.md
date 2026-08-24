# Week 3 RAG Evaluation - Results

**Evaluation Date**: 2026-08-24

## Executive Summary

This evaluation compares two chunking strategies for HR policy retrieval:

- **Basic Chunker**: Fixed-size chunks (500 chars, 100 overlap) - **0/8 Hit@5**
- **Structured Chunker**: Section-aware chunks - **7/8 Hit@5**

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
{
  "source_file": "HR-207-Kerala.md",
  "policy_id": "HR-207",
  "region": "Kerala",
  "effective_date": "2025-01-01",
  "section": "4.2",
  "chunk_id": "HR-207-4.2-001"
}
```

**Total chunks ingested:**
- Basic chunker: 18 chunks
- Structured chunker: 24 chunks

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
| Hit@5 | 0/8 | 7/8 |

### Detailed Results

| ID | Expected Policy | Expected Section | Basic Hit | Basic Rank | Basic Score | Structured Hit | Structured Rank | Structured Score |
|---|---|---|---|---|---|---|---|---|
| Q1 | HR-207 | 4.2 | [-] | — | 0.000 | [+] | 1 | 0.728 |
| Q2 | HR-202 | 4.2 | [-] | — | 0.000 | [+] | 2 | 0.512 |
| Q3 | HR-203 | 4.2 | [-] | — | 0.000 | [-] | — | 0.000 |
| Q4 | HR-204 | 4.2 | [-] | — | 0.000 | [+] | 5 | 0.529 |
| Q5 | HR-202 | 4.3 | [-] | — | 0.000 | [+] | 1 | 0.601 |
| Q6 | HR-203 | 4.3 | [-] | — | 0.000 | [+] | 1 | 0.673 |
| Q7 | HR-205 | 4.2 | [-] | — | 0.000 | [+] | 3 | 0.537 |
| Q8 | HR-206 | 4.2 | [-] | — | 0.000 | [+] | 4 | 0.545 |

## Metadata Filtering

**Test Query**: "What is the carry-over cap for a probationary employee?"

**Region Filter**: Kerala

### Unfiltered Results (All Regions)

| Rank | Chunk ID | Region | Policy | Score |
|---|---|---|---|---|
| 1 | HR-207-4.2-002 | Kerala | HR-207 | 0.751 |
| 2 | HR-203-4.2-002 | Chennai | HR-203 | 0.645 |
| 3 | HR-205-4.2-002 | Pune | HR-205 | 0.644 |
| 4 | HR-204-4.2-002 | Hyderabad | HR-204 | 0.644 |
| 5 | HR-206-4.2-002 | Mumbai | HR-206 | 0.643 |

### Filtered Results (Region=Kerala)

| Rank | Chunk ID | Region | Policy | Score |
|---|---|---|---|---|
| 1 | HR-207-4.2-002 | Kerala | HR-207 | 0.751 |
| 2 | HR-207-4.3-003 | Kerala | HR-207 | 0.254 |
| 3 | HR-207-4.1-001 | Kerala | HR-207 | 0.248 |
| 4 | HR-207-4.4-004 | Kerala | HR-207 | 0.241 |

**Observation**: The filtered search for 'Kerala' prioritizes policies from that region, changing the ranking of results.

## Chunking Strategy Recommendation

### Analysis

**Recommended: Structure-Aware Chunker**

The structure-aware chunker achieves 7/8 Hit@5 compared to 0/8 for the basic chunker.

**Why structure-aware chunker is better:**
- Preserves section headers with their content
- Keeps eligibility tables intact and with their context
- Provides better semantic coherence for HR policy queries
- Section numbers remain associated with their carry-over caps and other policy details

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

**Key Finding**: The structure-aware chunker performs better or equally as well for HR policy retrieval tasks.

---

**Evaluation Timestamp**: 2026-08-24T13:53:27.228146
**Total Evaluation Duration**: Complete ingestion and evaluation cycle
**RAG Framework**: Python-based with ChromaDB, sentence-transformers, and OpenAI integration
