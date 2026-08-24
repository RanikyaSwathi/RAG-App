"""
Metadata extraction from HR policy documents.
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


def extract_metadata_from_file(file_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from YAML frontmatter in markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Dictionary containing metadata
        
    Raises:
        ValueError: If metadata cannot be extracted
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract YAML frontmatter
    if not content.startswith("---"):
        raise ValueError(f"File {file_path.name} does not start with YAML frontmatter")
    
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        raise ValueError(f"Cannot parse YAML frontmatter in {file_path.name}")
    
    frontmatter_text = match.group(1)
    metadata = yaml.safe_load(frontmatter_text)
    
    if not metadata:
        raise ValueError(f"Empty metadata in {file_path.name}")
    
    # Add source_file to metadata
    metadata["source_file"] = file_path.name
    
    # Convert date objects to strings (ChromaDB requires string/int/float/bool)
    for key, value in metadata.items():
        if hasattr(value, 'isoformat'):  # datetime/date object
            metadata[key] = value.isoformat()
    
    # Validate required fields
    required_fields = ["policy_id", "region", "effective_date"]
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required field '{field}' in {file_path.name}")
    
    return metadata


def extract_document_body(file_path: Path) -> str:
    """
    Extract the document body (everything after YAML frontmatter).
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Document body as string
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove YAML frontmatter
    match = re.match(r"^---\n.*?\n---\n", content, re.DOTALL)
    if match:
        return content[match.end():]
    
    return content


def extract_sections_and_tables(content: str) -> list[Dict[str, Any]]:
    """
    Extract sections and tables from document content.
    
    Args:
        content: Document body content
        
    Returns:
        List of sections with their content
    """
    sections = []
    
    # Split by section headers (##)
    section_pattern = r"^## ([\d\.]+\s+.*?)$"
    section_matches = list(re.finditer(section_pattern, content, re.MULTILINE))
    
    for i, match in enumerate(section_matches):
        section_title = match.group(1)
        section_start = match.start()
        section_end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(content)
        
        section_content = content[section_start:section_end].strip()
        
        sections.append({
            "title": section_title,
            "content": section_content,
            "start": section_start,
            "end": section_end,
        })
    
    return sections
