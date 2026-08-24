"""
LLM-based answer generation with strict refusal for unsupported questions.
"""

import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI, RateLimitError
import os

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an HR policy assistant.

Answer ONLY from the supplied retrieved policy context.

Do not use outside knowledge.

If the answer is not supported by the retrieved context, say:

"I don't know. The provided HR policy documents do not contain this information."

Never invent:
- policy IDs
- sections
- regions
- dates
- policy rules

For every answer, return the source citation in the format:
Source: [source_file]
Policy: [policy_id]
Region: [region]
Section: [section]
Effective Date: [effective_date]
Chunk ID: [chunk_id]
"""


class AnswerGenerator:
    """Generate answers using LLM with strict citation requirements."""
    
    def __init__(self, model: str = "gpt-4-turbo-preview", api_key: Optional[str] = None):
        """
        Initialize answer generator.
        
        Args:
            model: LLM model name
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized answer generator with model: {model}")
    
    def generate_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate answer for a question based on retrieved chunks.
        
        Args:
            question: Question to answer
            retrieved_chunks: List of retrieved chunks with metadata
            max_retries: Maximum number of retries on rate limit
            
        Returns:
            Dictionary with answer, citations, and metadata
        """
        # Format context from retrieved chunks
        context = self._format_context(retrieved_chunks)
        
        # Prepare message
        user_message = f"""Question: {question}

Context from HR policies:

{context}

Please answer the question using only the provided context. If the answer is not in the context, refuse to answer."""
        
        # Call LLM
        retries = 0
        while retries < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.0,
                    max_tokens=500,
                )
                
                answer = response.choices[0].message.content
                
                # Extract citations from retrieved chunks
                citations = self._extract_citations(retrieved_chunks)
                
                return {
                    "question": question,
                    "answer": answer,
                    "citations": citations,
                    "retrieved_chunks_count": len(retrieved_chunks),
                    "success": True,
                }
            
            except RateLimitError:
                retries += 1
                if retries >= max_retries:
                    logger.error(f"Max retries reached for question: {question}")
                    return {
                        "question": question,
                        "answer": "Error: Rate limit exceeded",
                        "citations": [],
                        "retrieved_chunks_count": len(retrieved_chunks),
                        "success": False,
                    }
                logger.warning(f"Rate limited, retrying... ({retries}/{max_retries})")
            
            except Exception as e:
                logger.error(f"Error generating answer: {e}")
                return {
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "citations": [],
                    "retrieved_chunks_count": len(retrieved_chunks),
                    "success": False,
                }
        
        return {
            "question": question,
            "answer": "Error: Failed to generate answer",
            "citations": [],
            "retrieved_chunks_count": len(retrieved_chunks),
            "success": False,
        }
    
    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context string."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            score = chunk.get("score", 0)
            chunk_id = metadata.get("chunk_id", "unknown")
            
            context_parts.append(
                f"[Document {i} - {chunk_id} (score: {score:.3f})]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _extract_citations(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citations from retrieved chunks."""
        citations = []
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            citations.append({
                "chunk_id": metadata.get("chunk_id", "unknown"),
                "source_file": metadata.get("source_file", "unknown"),
                "policy_id": metadata.get("policy_id", "unknown"),
                "region": metadata.get("region", "unknown"),
                "section": metadata.get("section", "unknown"),
                "effective_date": metadata.get("effective_date", "unknown"),
                "score": chunk.get("score", 0),
            })
        
        return citations
