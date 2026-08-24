"""
Configuration and constants for the HR RAG application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "hr_policy_addenda"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
RESULTS_DIR = PROJECT_ROOT / "evaluation"

# Ensure directories exist
VECTOR_DB_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Chunking configurations
BASIC_CHUNK_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 100,
}

STRUCTURED_CHUNK_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
}

# Embedding configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Vector DB collections
BASIC_COLLECTION = "hr_policy_basic"
STRUCTURED_COLLECTION = "hr_policy_structured"

# Retrieval configuration
DEFAULT_TOP_K = 5

# LLM configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ChromaDB path
CHROMA_DB_PATH = str(VECTOR_DB_DIR / "chroma_db")

# Policy files
POLICY_FILES = [
    "HR-202-Bangalore.md",
    "HR-203-Chennai.md",
    "HR-204-Hyderabad.md",
    "HR-205-Pune.md",
    "HR-206-Mumbai.md",
    "HR-207-Kerala.md",
]
