"""
Chunking strategies for HR policy documents.
"""

import re
from typing import List, Dict, Any
from metadata_extractor import extract_sections_and_tables


class BasicChunker:
    """
    Basic fixed-size chunker with configurable size and overlap.
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize the basic chunker.
        
        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into fixed-size chunks with overlap.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # Clean text
        text = text.strip()
        if not text:
            return chunks
        
        # Calculate step size
        step_size = self.chunk_size - self.chunk_overlap
        if step_size <= 0:
            step_size = self.chunk_size
        
        # Create chunks
        chunk_id = 0
        for start in range(0, len(text), step_size):
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()
            
            if not chunk_text:
                continue
            
            chunk_id += 1
            chunk_metadata = {
                **metadata,
                "chunk_id": f"{metadata['policy_id']}-basic-{chunk_id:03d}",
                "chunk_type": "basic",
            }
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata,
            })
        
        return chunks


class StructureAwareChunker:
    """
    Structure-aware chunker that respects section headers and tables.
    """
    
    def __init__(self, max_chunk_size: int = 1000):
        """
        Initialize the structure-aware chunker.
        
        Args:
            max_chunk_size: Maximum size of a chunk in characters
        """
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into structure-aware chunks.
        
        Respects section headers and keeps tables together.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        text = text.strip()
        
        if not text:
            return chunks
        
        # Extract sections
        sections = self._extract_sections(text)
        
        chunk_id = 0
        
        for section in sections:
            section_title = section["title"]
            section_content = section["content"]
            
            # Extract section number from title (e.g., "4.2 Carry-over Rule")
            section_match = re.match(r"^([\d\.]+)\s+", section_title)
            section_num = section_match.group(1) if section_match else "0"
            
            # Split section content if too large
            if len(section_content) <= self.max_chunk_size:
                chunk_id += 1
                chunk_metadata = {
                    **metadata,
                    "chunk_id": f"{metadata['policy_id']}-{section_num}-{chunk_id:03d}",
                    "chunk_type": "structured",
                    "section": section_num,
                }
                
                chunks.append({
                    "text": f"## {section_title}\n\n{section_content}",
                    "metadata": chunk_metadata,
                })
            else:
                # Split large sections into subsections
                subsections = self._split_large_section(section_content)
                
                for i, subsection in enumerate(subsections):
                    chunk_id += 1
                    chunk_metadata = {
                        **metadata,
                        "chunk_id": f"{metadata['policy_id']}-{section_num}-{chunk_id:03d}",
                        "chunk_type": "structured",
                        "section": section_num,
                    }
                    
                    chunks.append({
                        "text": f"## {section_title}\n\n{subsection}",
                        "metadata": chunk_metadata,
                    })
        
        return chunks
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extract sections from text based on ## headers."""
        sections = []
        
        # Split by section headers (##)
        section_pattern = r"^## ([\d\.]+\s+.*?)$"
        section_matches = list(re.finditer(section_pattern, text, re.MULTILINE))
        
        for i, match in enumerate(section_matches):
            section_title = match.group(1)
            section_start = match.start()
            section_end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(text)
            
            section_text = text[section_start:section_end].strip()
            
            # Remove the header from content (keep just the body)
            content_start = section_text.find("\n")
            if content_start != -1:
                section_body = section_text[content_start:].strip()
            else:
                section_body = ""
            
            sections.append({
                "title": section_title,
                "content": section_body,
            })
        
        return sections
    
    def _split_large_section(self, content: str, max_size: int = None) -> List[str]:
        """
        Split a large section into subsections.
        
        Tries to split on tables or paragraphs to maintain structure.
        """
        if max_size is None:
            max_size = self.max_chunk_size
        
        if len(content) <= max_size:
            return [content]
        
        # Try to split on tables
        table_pattern = r"\n\|.*?\|.*?\n(?:\|.*?\|.*?\n)*"
        tables = list(re.finditer(table_pattern, content, re.MULTILINE))
        
        if tables:
            subsections = []
            last_end = 0
            
            for table_match in tables:
                before = content[last_end:table_match.start()]
                table = content[table_match.start():table_match.end()]
                
                if len(before) > 0:
                    subsections.append(before.strip())
                subsections.append(table.strip())
                
                last_end = table_match.end()
            
            if last_end < len(content):
                remaining = content[last_end:]
                if remaining.strip():
                    subsections.append(remaining.strip())
            
            return [s for s in subsections if s]
        
        # Fallback: split on paragraph boundaries
        paragraphs = content.split("\n\n")
        
        subsections = []
        current = ""
        
        for para in paragraphs:
            if len(current) + len(para) + 2 <= max_size:
                current += para + "\n\n"
            else:
                if current:
                    subsections.append(current.strip())
                current = para + "\n\n"
        
        if current:
            subsections.append(current.strip())
        
        return subsections
