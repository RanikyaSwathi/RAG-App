from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi

BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma"

# Week 4 Evaluation Questions with Ground Truth and Pre-Improvement Classification
WEEK4_EVALUATION_SET = [
    {
        "id": "Q1",
        "question": "What are the rules in section 3 of policy HR-201?",
        "expected_policy_id": "HR-201",
        "expected_section": "3",
        "dense_status": "FAIL",
        "hybrid_status": "PASS",
        "failure_type": "Retrieval Failure",
        "evidence": "Dense vector search returned HR-203 §4 and HR-202 §3 because embeddings drifted on generic terms ('rules in section 3') while missing the exact code 'HR-201'.",
        "ground_truth_answer": "Annual leave requests must normally be submitted at least 5 working days before the planned date, subject to manager approval.",
    },
    {
        "id": "Q2",
        "question": "HR-202 section 1 eligibility",
        "expected_policy_id": "HR-202",
        "expected_section": "1",
        "dense_status": "PASS",
        "hybrid_status": "PASS",
        "failure_type": "None (Success)",
        "evidence": "Dense search captures the semantic meaning of eligibility in remote work, ranking HR-202 §1 in the top 3.",
        "ground_truth_answer": "Employees may request remote work after completing probation and meeting role requirements.",
    },
    {
        "id": "Q3",
        "question": "What are the requirements in HR-204 section 3?",
        "expected_policy_id": "HR-204",
        "expected_section": "3",
        "dense_status": "FAIL",
        "hybrid_status": "FAIL",
        "failure_type": "Retrieval Failure (Unfixed)",
        "evidence": "HR-204 §3 describes illness notification without using the word 'requirements'. Both dense search and BM25 rank other sections higher.",
        "ground_truth_answer": "Employees must notify their manager as soon as reasonably possible when unable to report to work due to illness.",
    },
    {
        "id": "Q4",
        "question": "What is the expense submission timeframe in HR-205 section 4?",
        "expected_policy_id": "HR-205",
        "expected_section": "4",
        "dense_status": "PASS",
        "hybrid_status": "PASS",
        "failure_type": "None (Success)",
        "evidence": "Semantic and keyword terms align strongly with expense submission timelines, retrieving HR-205 §4 at rank 1.",
        "ground_truth_answer": "Travel expenses must normally be submitted within 15 calendar days after returning from the business trip.",
    },
    {
        "id": "Q5",
        "question": "What does HR-207 section 4 mandate regarding probation?",
        "expected_policy_id": "HR-207",
        "expected_section": "4",
        "dense_status": "FAIL",
        "hybrid_status": "PASS",
        "failure_type": "Retrieval Failure",
        "evidence": "Dense search confused probation reviews with leave tables (HR-207 §2). BM25 restored HR-207 §4 to rank 1 via exact section keyword matching.",
        "ground_truth_answer": "Probation completion requires satisfactory performance and manager confirmation.",
    },
    {
        "id": "Q6",
        "question": "Policy HR-202 scope",
        "expected_policy_id": "HR-202",
        "expected_section": "5",
        "dense_status": "FAIL",
        "hybrid_status": "PASS",
        "failure_type": "Retrieval Failure",
        "evidence": "Dense search ranked AMER scope (HR-204 §5) first because generic 'scope' embeddings overlap. Exact keyword 'HR-202' allowed BM25 to rank HR-202 §5 in top 3.",
        "ground_truth_answer": "The remote work addendum applies to APAC employees.",
    },
    {
        "id": "Q7",
        "question": "Who is covered under HR-203 section 5?",
        "expected_policy_id": "HR-203",
        "expected_section": "5",
        "dense_status": "FAIL",
        "hybrid_status": "FAIL",
        "failure_type": "Retrieval Failure (Unfixed)",
        "evidence": "HR-203 §5 states 'This addendum applies to EMEA employees'. The phrasing 'who is covered under' has insufficient lexical overlap with 'applies to'.",
        "ground_truth_answer": "HR-203 applies to EMEA employees covered by the parental leave program.",
    },
    {
        "id": "Q8",
        "question": "What is the standard daily meal allowance for a business trip?",
        "expected_policy_id": "HR-205",
        "expected_section": "2",
        "dense_status": "PASS",
        "hybrid_status": "PASS",
        "failure_type": "None (Success)",
        "evidence": "Strong semantic similarity for travel meal allowances retrieves HR-205 §2 at rank 1 across both systems.",
        "ground_truth_answer": "USD 45 per eligible travel day.",
    },
    {
        "id": "Q9",
        "question": "How many days per week may an eligible employee work remotely?",
        "expected_policy_id": "HR-202",
        "expected_section": "2",
        "dense_status": "PASS",
        "hybrid_status": "PASS",
        "failure_type": "None (Success)",
        "evidence": "Direct semantic match to weekly remote work limit retrieves HR-202 §2 at rank 1.",
        "ground_truth_answer": "Up to 2 days per week, unless an exception is approved.",
    },
    {
        "id": "Q10",
        "question": "How long is the normal probation period for a new regular employee?",
        "expected_policy_id": "HR-207",
        "expected_section": "1",
        "dense_status": "PASS",
        "hybrid_status": "PASS",
        "failure_type": "None (Success)",
        "evidence": "Clear semantic match for probation period length retrieves HR-207 §1 at rank 1.",
        "ground_truth_answer": "Normally 6 months.",
    },
]

# Separate Generation Failure Cases (Right Document Fetched, Wrong Answer)
GENERATION_FAILURE_CASES = [
    {
        "question": "What is the annual leave carry-over cap for an employee with 2 months of service?",
        "fetched_chunk": "HR-207-chunk-0026 (HR-207 §2)",
        "chunk_content": "| Employee status | Completed service | Carry-over cap |\n| Probationary employee | Less than 3 months | 0 days |\n| Probationary employee | 3 to less than 6 months | 2 days |",
        "failure_type": "Right Document, Wrong Answer (Generation Failure)",
        "generated_answer": "An employee with 2 months of service is allowed to carry over 2 days of annual leave.",
        "correct_answer": "0 days. According to HR-207 §2, probationary employees with less than 3 months of completed service have a carry-over cap of 0 days.",
        "root_cause": "The retriever successfully fetched the exact eligibility table chunk in top-1, but the LLM read the wrong table row (confusing 'less than 3 months' with '3 to less than 6 months').",
    },
    {
        "question": "Under what condition does continuous service grant 18 days of annual leave?",
        "fetched_chunk": "HR-201-chunk-0001 (HR-201 §1)",
        "chunk_content": "| Regular employee | 3 years or more | 18 days |",
        "failure_type": "Right Document, Wrong Answer (Generation Failure)",
        "generated_answer": "Continuous service of 3 years grants 18 days, but what constitutes continuous service is not explained.",
        "correct_answer": "3 years or more of completed service for regular employees (definition of continuous service is in base handbook).",
        "root_cause": "The tight chunking strategy retrieved the isolated clause without the surrounding global definition of continuous service, stranding the generator.",
    },
]


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase alphanumeric tokens."""
    return re.findall(r"\w+", text.lower())


class HybridSearchEngine:
    def __init__(self, vectorstore: Chroma, rrf_k: int = 60):
        self.vectorstore = vectorstore
        self.rrf_k = rrf_k
        self._build_bm25_index()

    def _build_bm25_index(self) -> None:
        raw_data = self.vectorstore.get(include=["documents", "metadatas"])
        self.documents_text: list[str] = raw_data["documents"]
        self.documents_meta: list[dict[str, Any]] = raw_data["metadatas"]

        self.corpus = [
            tokenize(
                f"{meta.get('policy_id', '')} Section {meta.get('section', '')} "
                f"{meta.get('region', '')} {text}"
            )
            for text, meta in zip(self.documents_text, self.documents_meta)
        ]
        self.bm25 = BM25Okapi(self.corpus)

    def search_dense(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        """Perform dense vector search alone."""
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def search_hybrid(
        self, query: str, k: int = 3, candidate_k: int = 10
    ) -> list[tuple[Document, float]]:
        """Perform Hybrid Search combining BM25 keyword search and Dense Vector Search via RRF."""
        # 1. Dense retrieval
        dense_hits = self.vectorstore.similarity_search_with_score(query, k=candidate_k)

        # 2. BM25 keyword retrieval
        query_tokens = tokenize(query)
        bm25_scores = self.bm25.get_scores(query_tokens)
        top_bm25_indices = sorted(
            range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True
        )[:candidate_k]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: dict[str, float] = {}
        doc_map: dict[str, Document] = {}

        for rank, (doc, _) in enumerate(dense_hits, start=1):
            cid = doc.metadata.get("chunk_id", str(rank))
            doc_map[cid] = doc
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        for rank, idx in enumerate(top_bm25_indices, start=1):
            if bm25_scores[idx] <= 0:
                continue
            meta = self.documents_meta[idx]
            cid = meta.get("chunk_id", str(idx))
            if cid not in doc_map:
                doc_map[cid] = Document(
                    page_content=self.documents_text[idx], metadata=meta
                )
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort by combined RRF score descending
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:k]
        return [(doc_map[cid], round(rrf_scores[cid], 6)) for cid in sorted_cids]


def evaluate_week4_retrieval(hybrid_engine: HybridSearchEngine, k: int = 3) -> dict[str, Any]:
    dense_results = []
    hybrid_results = []
    dense_passes = 0
    hybrid_passes = 0

    for item in WEEK4_EVALUATION_SET:
        q = item["question"]
        exp_pid = item["expected_policy_id"]
        exp_sec = item["expected_section"]

        # Dense evaluation
        dense_hits = hybrid_engine.search_dense(q, k=k)
        dense_hit = any(
            d.metadata.get("policy_id") == exp_pid and d.metadata.get("section") == exp_sec
            for d, _ in dense_hits
        )
        if dense_hit:
            dense_passes += 1
        dense_results.append({
            "id": item["id"],
            "question": q,
            "expected_policy_id": exp_pid,
            "expected_section": exp_sec,
            "hit": dense_hit,
            "top_results": [
                {
                    "chunk_id": doc.metadata.get("chunk_id"),
                    "policy_id": doc.metadata.get("policy_id"),
                    "section": doc.metadata.get("section"),
                    "region": doc.metadata.get("region"),
                    "score": round(float(score), 4),
                }
                for doc, score in dense_hits
            ],
        })

        # Hybrid evaluation
        hybrid_hits = hybrid_engine.search_hybrid(q, k=k)
        hybrid_hit = any(
            d.metadata.get("policy_id") == exp_pid and d.metadata.get("section") == exp_sec
            for d, _ in hybrid_hits
        )
        if hybrid_hit:
            hybrid_passes += 1
        hybrid_results.append({
            "id": item["id"],
            "question": q,
            "expected_policy_id": exp_pid,
            "expected_section": exp_sec,
            "hit": hybrid_hit,
            "top_results": [
                {
                    "chunk_id": doc.metadata.get("chunk_id"),
                    "policy_id": doc.metadata.get("policy_id"),
                    "section": doc.metadata.get("section"),
                    "region": doc.metadata.get("region"),
                    "score": round(float(score), 4),
                }
                for doc, score in hybrid_hits
            ],
        })

    total = len(WEEK4_EVALUATION_SET)
    return {
        "k": k,
        "total": total,
        "dense_passes": dense_passes,
        "hybrid_passes": hybrid_passes,
        "dense_hit_rate": dense_passes / total,
        "hybrid_hit_rate": hybrid_passes / total,
        "dense_results": dense_results,
        "hybrid_results": hybrid_results,
        "eval_set": WEEK4_EVALUATION_SET,
        "generation_failures": GENERATION_FAILURE_CASES,
    }


def main() -> None:
    print("Loading vectorstore for Week 4 Hybrid Evaluation...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    store = Chroma(
        collection_name="rag_addenda_structure",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR / "rag_addenda_structure"),
    )
    engine = HybridSearchEngine(store)
    report = evaluate_week4_retrieval(engine, k=3)

    print("\n" + "=" * 65)
    print("WEEK 4 BENCHMARK: DENSE VS HYBRID (BM25 + DENSE RRF) AT k=3")
    print("=" * 65)
    import sys
    if sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    for d, h, item in zip(report["dense_results"], report["hybrid_results"], report["eval_set"]):
        d_icon = "[PASS]" if d["hit"] else "[FAIL]"
        h_icon = "[PASS]" if h["hit"] else "[FAIL]"
        print(f"[{item['id']}] Dense: {d_icon:<6} | Hybrid: {h_icon:<6} | {item['question'][:45]}")

    print("\n" + "-" * 65)
    print(f"Dense Hit-Rate@3:  {report['dense_passes']}/{report['total']} ({report['dense_hit_rate']*100:.1f}%)")
    print(f"Hybrid Hit-Rate@3: {report['hybrid_passes']}/{report['total']} ({report['hybrid_hit_rate']*100:.1f}%)")
    print(f"Improvement:       +{report['hybrid_hit_rate']*100 - report['dense_hit_rate']*100:.1f}%")
    print("=" * 65)


if __name__ == "__main__":
    main()
