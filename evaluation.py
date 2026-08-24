"""
Evaluation script for HR policy RAG.

Runs all evaluation questions against both chunking strategies and generates results.
"""

import logging
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path

from config import RESULTS_DIR
from main import HRPolicyRAG
from evaluation_questions import (
    EVALUATION_QUESTIONS,
    ANSWERABLE_QUESTIONS,
    UNANSWERABLE_QUESTIONS,
)

logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluation suite for RAG system."""
    
    def __init__(self, rag: HRPolicyRAG):
        """Initialize evaluator."""
        self.rag = rag
        self.evaluation_results = []
        self.answerable_results = []
        self.unanswerable_results = []
    
    def evaluate_retrieval(self) -> Dict[str, Any]:
        """
        Evaluate retrieval performance on 8 questions.
        
        Returns:
            Dictionary with evaluation results
        """
        logger.info("\n=== RETRIEVAL EVALUATION ===")
        logger.info("Evaluating 8 questions against both chunking strategies...\n")
        
        basic_hits = 0
        structured_hits = 0
        
        # Results table
        results_table = []
        
        for q in EVALUATION_QUESTIONS:
            question_id = q["id"]
            question = q["question"]
            expected_policy = q["expected_policy_id"]
            expected_section = q["expected_section"]
            expected_region = q["expected_region"]
            
            logger.info(f"[{question_id}] {question}")
            logger.info(f"  Expected: Policy={expected_policy}, Section={expected_section}, Region={expected_region}")
            
            # Retrieve from both strategies
            basic_results, structured_results = self.rag.retrieve_both(question, top_k=5)
            
            # Check if expected policy/section is in top 5
            basic_hit = self._check_hit(basic_results, expected_policy, expected_section)
            structured_hit = self._check_hit(structured_results, expected_policy, expected_section)
            
            basic_rank = self._find_rank(basic_results, expected_policy, expected_section)
            structured_rank = self._find_rank(structured_results, expected_policy, expected_section)
            
            if basic_hit:
                basic_hits += 1
            if structured_hit:
                structured_hits += 1
            
            basic_score = self._get_score(basic_results, expected_policy, expected_section)
            structured_score = self._get_score(structured_results, expected_policy, expected_section)
            
            logger.info(f"  Basic:      Rank={basic_rank}, Hit@5={basic_hit}, Score={basic_score:.3f}")
            logger.info(f"  Structured: Rank={structured_rank}, Hit@5={structured_hit}, Score={structured_score:.3f}\n")
            
            results_table.append({
                "question_id": question_id,
                "question": question,
                "expected_policy_id": expected_policy,
                "expected_section": expected_section,
                "expected_region": expected_region,
                "basic_hit": basic_hit,
                "basic_rank": basic_rank,
                "basic_score": basic_score,
                "structured_hit": structured_hit,
                "structured_rank": structured_rank,
                "structured_score": structured_score,
                "basic_results": basic_results[:5],
                "structured_results": structured_results[:5],
            })
        
        # Summary
        basic_score = f"{basic_hits}/8"
        structured_score = f"{structured_hits}/8"
        
        logger.info("\n=== SUMMARY ===")
        logger.info(f"Basic chunker:      {basic_score}")
        logger.info(f"Structured chunker: {structured_score}\n")
        
        return {
            "basic_score": basic_score,
            "structured_score": structured_score,
            "basic_hits": basic_hits,
            "structured_hits": structured_hits,
            "results_table": results_table,
        }
    
    def evaluate_metadata_filtering(self) -> Dict[str, Any]:
        """
        Evaluate metadata filtering with one region filter example.
        
        Returns:
            Dictionary with filtering results
        """
        logger.info("\n=== METADATA FILTERING EVALUATION ===")
        
        # Example query
        query = "What is the carry-over cap for a probationary employee?"
        region = "Kerala"
        
        logger.info(f"Query: {query}")
        logger.info(f"Filter region: {region}\n")
        
        # Unfiltered
        unfiltered = self.rag.retrieve(query, top_k=5, collection_type="structured")
        logger.info("Unfiltered results (all regions):")
        for i, result in enumerate(unfiltered, 1):
            metadata = result["metadata"]
            logger.info(
                f"  {i}. {result['chunk_id']} "
                f"(region: {metadata.get('region', 'unknown')}, score: {result['score']:.3f})"
            )
        
        # Filtered
        filtered = self.rag.retrieve(
            query,
            top_k=5,
            collection_type="structured",
            region_filter=region
        )
        logger.info(f"\nFiltered results (region={region}):")
        for i, result in enumerate(filtered, 1):
            metadata = result["metadata"]
            logger.info(
                f"  {i}. {result['chunk_id']} "
                f"(region: {metadata.get('region', 'unknown')}, score: {result['score']:.3f})"
            )
        
        # Check if filtering changed top result
        top_changed = (
            unfiltered[0]["metadata"].get("region") != region
            and filtered[0]["metadata"].get("region") == region
        )
        
        logger.info(f"\nTop result changed by filter: {top_changed}\n")
        
        return {
            "query": query,
            "region_filter": region,
            "unfiltered_results": unfiltered,
            "filtered_results": filtered,
            "top_changed": top_changed,
        }
    
    def evaluate_answerable_questions(self) -> List[Dict[str, Any]]:
        """
        Evaluate answerable questions with LLM generation.
        
        Returns:
            List of generation results
        """
        logger.info("\n=== ANSWERABLE QUESTIONS ===")
        
        results = []
        
        for q in ANSWERABLE_QUESTIONS:
            question_id = q["id"]
            question = q["question"]
            
            logger.info(f"\n[{question_id}] {question}")
            
            # Generate answer
            result = self.rag.generate_answer(question, top_k=5, collection_type="structured")
            
            logger.info(f"Answer: {result['answer'][:200]}...")
            if result.get("citations"):
                logger.info(f"Citations: {len(result['citations'])} chunks")
            
            results.append({
                "question_id": question_id,
                "question": question,
                **result,
            })
        
        return results
    
    def evaluate_unanswerable_questions(self) -> List[Dict[str, Any]]:
        """
        Evaluate unanswerable questions (should be refused).
        
        Returns:
            List of refusal results
        """
        logger.info("\n=== UNANSWERABLE QUESTIONS ===")
        
        results = []
        
        for q in UNANSWERABLE_QUESTIONS:
            question_id = q["id"]
            question = q["question"]
            reason = q["reason"]
            
            logger.info(f"\n[{question_id}] {question}")
            logger.info(f"  Reason: {reason}")
            
            # Try to generate answer
            result = self.rag.generate_answer(question, top_k=5, collection_type="structured")
            
            # Check if refused
            is_refused = "don't know" in result.get("answer", "").lower()
            
            logger.info(f"  Refused: {is_refused}")
            logger.info(f"  Response: {result['answer'][:200]}...")
            
            results.append({
                "question_id": question_id,
                "question": question,
                "expected_refusal_reason": reason,
                "refused": is_refused,
                **result,
            })
        
        return results
    
    def _check_hit(
        self,
        results: List[Dict[str, Any]],
        expected_policy: str,
        expected_section: str
    ) -> bool:
        """Check if expected policy and section are in results."""
        for result in results:
            metadata = result["metadata"]
            if (metadata.get("policy_id") == expected_policy and
                metadata.get("section") == expected_section):
                return True
        return False
    
    def _find_rank(
        self,
        results: List[Dict[str, Any]],
        expected_policy: str,
        expected_section: str
    ) -> int:
        """Find rank of expected policy and section."""
        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            if (metadata.get("policy_id") == expected_policy and
                metadata.get("section") == expected_section):
                return i
        return -1
    
    def _get_score(
        self,
        results: List[Dict[str, Any]],
        expected_policy: str,
        expected_section: str
    ) -> float:
        """Get score of expected policy and section."""
        for result in results:
            metadata = result["metadata"]
            if (metadata.get("policy_id") == expected_policy and
                metadata.get("section") == expected_section):
                return result.get("score", 0)
        return 0.0


def run_evaluation() -> Dict[str, Any]:
    """Run full evaluation suite."""
    logger.info("Initializing RAG system...")
    rag = HRPolicyRAG()
    
    logger.info("Ingesting documents...")
    basic_count, structured_count = rag.ingest_documents()
    
    stats = rag.get_collection_stats()
    logger.info(f"Collection stats: {stats}\n")
    
    # Run evaluations
    evaluator = Evaluator(rag)
    
    retrieval_results = evaluator.evaluate_retrieval()
    filtering_results = evaluator.evaluate_metadata_filtering()
    answerable_results = evaluator.evaluate_answerable_questions()
    unanswerable_results = evaluator.evaluate_unanswerable_questions()
    
    # Compile results
    evaluation_output = {
        "summary": {
            "basic_chunks_ingested": basic_count,
            "structured_chunks_ingested": structured_count,
            "collection_stats": stats,
        },
        "retrieval_evaluation": retrieval_results,
        "metadata_filtering": filtering_results,
        "answerable_questions": answerable_results,
        "unanswerable_questions": unanswerable_results,
    }
    
    return evaluation_output


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    results = run_evaluation()
    
    # Save results
    output_file = RESULTS_DIR / "evaluation_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\nResults saved to {output_file}")
