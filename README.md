# HR Policy RAG Application

A Retrieval-Augmented Generation (RAG) application for HR policy question answering using two distinct chunking strategies.

## Overview

This application ingests 6 regional HR policy addenda and provides intelligent question answering with:

- **Two chunking strategies**: Basic fixed-size and structure-aware
- **Vector embeddings**: Using sentence-transformers
- **Vector database**: ChromaDB for efficient retrieval
- **LLM-based generation**: OpenAI GPT models
- **Metadata filtering**: Region-based filtering support
- **Strict refusal**: Refuses to answer questions outside policy scope

## Documents

The application processes 6 HR policy addenda:

1. HR-202-Bangalore.md
2. HR-203-Chennai.md
3. HR-204-Hyderabad.md
4. HR-205-Pune.md
5. HR-206-Mumbai.md
6. HR-207-Kerala.md

Each document contains policy metadata and regional variations for leave policies.

## Architecture

### Modules

- **config.py**: Configuration and constants
- **metadata_extractor.py**: Extract metadata from YAML frontmatter
- **chunkers.py**: Two chunking strategies (basic and structure-aware)
- **embeddings.py**: Embedding generation and vector DB operations
- **generator.py**: LLM-based answer generation with citations
- **main.py**: Main RAG application orchestrator
- **evaluation_questions.py**: 8 evaluation questions with known answers
- **evaluation.py**: Comprehensive evaluation suite
- **tests.py**: Unit tests for all components

### Chunking Strategies

#### Basic Chunker
- Fixed chunk size (default 500 characters)
- Configurable overlap (default 100 characters)
- Simple sliding window approach

#### Structure-Aware Chunker
- Respects section headers
- Keeps eligibility tables together
- Splits large sections intelligently
- Maintains policy context with chunk IDs

### Vector Database

Uses ChromaDB with two separate collections:

- `hr_policy_basic`: Chunks from basic chunker
- `hr_policy_structured`: Chunks from structure-aware chunker

### Metadata

Every chunk contains complete metadata:

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

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Set your OpenAI API key:

```
OPENAI_API_KEY=your-key-here
```

## Usage

### Ingest Documents

```python
from main import HRPolicyRAG

rag = HRPolicyRAG()
basic_count, structured_count = rag.ingest_documents()
```

### Retrieve Chunks

```python
# Retrieve from both strategies
basic_results, structured_results = rag.retrieve_both(
    query="What is the carry-over cap?",
    top_k=5
)

# Retrieve with region filter
results = rag.retrieve(
    query="What is the carry-over cap?",
    top_k=5,
    collection_type="structured",
    region_filter="Kerala"
)
```

### Generate Answers

```python
result = rag.generate_answer(
    question="What is the carry-over cap for a probationary employee?",
    top_k=5,
    collection_type="structured"
)

print(result["answer"])
print(result["citations"])
```

## Evaluation

### Run Full Evaluation Suite

```bash
python evaluation.py
```

This runs:

1. **Retrieval evaluation** on 8 known-answer questions
2. **Metadata filtering** demonstration
3. **Answerable questions** with LLM generation (3+ examples)
4. **Unanswerable questions** with refusal behavior (3+ examples)

### Run Tests

```bash
pytest tests.py -v
```

## Evaluation Results

### 8 Evaluation Questions

All questions have known answers in the policy documents:

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

### Chunking Strategy Comparison

Results are reported as Hit@5 (whether the correct policy/section appears in top 5 results):

- **Basic chunker**: X/8
- **Structure-aware chunker**: Y/8

### Metadata Filtering

Example: Query with and without region filter for Kerala:

**Unfiltered**: Results from all 6 policies
**Filtered** (region=Kerala): Results prioritizing HR-207

## Project Structure

```
RAG-App/
├── config.py                    # Configuration
├── metadata_extractor.py        # Metadata extraction
├── chunkers.py                  # Chunking strategies
├── embeddings.py                # Embeddings and vector DB
├── generator.py                 # LLM answer generation
├── main.py                      # Main RAG application
├── evaluation_questions.py      # Evaluation questions
├── evaluation.py                # Evaluation suite
├── tests.py                     # Unit tests
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
├── hr_policy_addenda/           # Input policy documents
│   ├── HR-202-Bangalore.md
│   ├── HR-203-Chennai.md
│   ├── HR-204-Hyderabad.md
│   ├── HR-205-Pune.md
│   ├── HR-206-Mumbai.md
│   └── HR-207-Kerala.md
├── vector_db/                   # ChromaDB storage
│   └── chroma_db/
└── evaluation/                  # Evaluation results
    └── results.md
```

## Features

### ✅ Complete Implementation

- [x] Ingest 6 policy documents
- [x] Extract metadata from YAML frontmatter
- [x] Implement basic chunker
- [x] Implement structure-aware chunker
- [x] Generate embeddings with sentence-transformers
- [x] Store in ChromaDB with two separate collections
- [x] Retrieve top-K chunks
- [x] Support metadata filtering by region
- [x] Generate LLM-based answers
- [x] Provide citations with chunk IDs
- [x] Refuse unsupported questions
- [x] Evaluate with 8 questions
- [x] Compare chunking strategies
- [x] Generate results.md
- [x] Comprehensive test suite

### Quality Assurance

- Clean, modular Python code
- Type hints throughout
- Comprehensive logging
- Error handling
- Unit tests for all components
- No hardcoded values (all configurable)
- Environment variables for secrets
- Idempotent ingestion (no duplicates)

## Assumptions

- OpenAI API key is available and valid
- Internet connection for downloading embedding models
- ChromaDB supports SQLite backend (included)
- Policy documents are in Markdown format with YAML frontmatter

## Known Limitations

- LLM quality depends on OpenAI API availability and model performance
- Metadata filtering is on exact field matches
- No multi-field filtering (AND/OR logic)
- Requires internet for downloading embedding models

## Future Enhancements

- Support for different embedding models
- Multiple LLM providers (Anthropic, Hugging Face, etc.)
- Advanced filtering with nested queries
- Fine-tuning on HR policy domain
- Caching for frequently asked questions
- User feedback loop for answer quality
- A/B testing framework

## License

Educational use for Week 3 RAG practical exercise.

## Contact

For questions or issues, please refer to the assignment instructions.
