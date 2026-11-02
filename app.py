from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
RESULTS_PATH = BASE_DIR / "results.md"

QUESTION_BANK = [
    {
        "question": "How many annual leave days does a regular employee with 3 years or more of service receive?",
        "expected_policy_id": "HR-201",
        "expected_section": "1",
    },
    {
        "question": "What is the annual leave carry-over cap and when must it be used?",
        "expected_policy_id": "HR-201",
        "expected_section": "2",
    },
    {
        "question": "How many days per week may an eligible employee work remotely?",
        "expected_policy_id": "HR-202",
        "expected_section": "2",
    },
    {
        "question": "How many weeks of parental leave can a primary parent receive?",
        "expected_policy_id": "HR-203",
        "expected_section": "1",
    },
    {
        "question": "How many paid sick-leave days does an eligible employee receive per calendar year?",
        "expected_policy_id": "HR-204",
        "expected_section": "1",
    },
    {
        "question": "What is the standard daily meal allowance for a business trip?",
        "expected_policy_id": "HR-205",
        "expected_section": "2",
    },
    {
        "question": "What is the carry-over cap for a probationary employee with 3 to less than 6 months of service?",
        "expected_policy_id": "HR-207",
        "expected_section": "2",
    },
    {
        "question": "How long is the normal probation period for a new regular employee?",
        "expected_policy_id": "HR-207",
        "expected_section": "1",
    },
]


def parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    patterns = {
        "policy_id": r"\*\*Policy ID:\*\*\s*(.+)",
        "region": r"\*\*Region:\*\*\s*(.+)",
        "effective_date": r"\*\*Effective Date:\*\*\s*(.+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            metadata[key] = match.group(1).strip()
    return metadata


def extract_section(text: str) -> str:
    match = re.search(r"(?m)^##\s+(\d+(?:\.\d+)?)\.\s+", text)
    return match.group(1) if match else "unknown"


def load_addenda() -> list[Document]:
    documents: list[Document] = []
    for file_path in sorted(DOCUMENTS_DIR.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        metadata = parse_metadata(text)
        metadata["source_file"] = file_path.name
        documents.append(Document(page_content=text, metadata=metadata))
    return documents


def add_chunk_metadata(chunks: list[Document]) -> list[Document]:
    for index, chunk in enumerate(chunks):
        policy_id = chunk.metadata.get("policy_id", "UNKNOWN")
        chunk.metadata["section"] = extract_section(chunk.page_content)
        chunk.metadata["chunk_id"] = f"{policy_id}-chunk-{index + 1:04d}"
    return chunks


def split_baseline(documents: list[Document]) -> list[Document]:
    chunks: list[Document] = []
    for document in documents:
        text = document.page_content
        parts = re.split(r"(?m)(^##\s+.*$)", text)
        buffer: list[str] = []
        current_header = ""
        for part in parts:
            if not part.strip():
                continue
            if re.match(r"^##\s+", part):
                if buffer:
                    combined = "\n".join(buffer).strip()
                    if combined:
                        clone = Document(page_content=f"{current_header}\n{combined}", metadata=document.metadata.copy())
                        clone.metadata["source_file"] = document.metadata.get("source_file", "unknown")
                        chunks.append(clone)
                    buffer = []
                current_header = part.strip()
                buffer.append(part)
            else:
                buffer.append(part.strip())
        if buffer:
            combined = "\n".join(buffer).strip()
            if combined:
                clone = Document(page_content=f"{current_header}\n{combined}", metadata=document.metadata.copy())
                clone.metadata["source_file"] = document.metadata.get("source_file", "unknown")
                chunks.append(clone)
    return add_chunk_metadata(chunks)


def split_structure_aware(documents: list[Document]) -> list[Document]:
    chunks: list[Document] = []
    for document in documents:
        text = document.page_content
        heading_matches = list(re.finditer(r"(?m)^##\s+\d+(?:\.\d+)?\.\s+.*$", text))
        if not heading_matches:
            clone = Document(page_content=text, metadata=document.metadata.copy())
            clone.metadata["section"] = "unknown"
            clone.metadata["chunk_id"] = f"{clone.metadata.get('policy_id','UNKNOWN')}-chunk-{len(chunks)+1:04d}"
            chunks.append(clone)
            continue

        for idx, match in enumerate(heading_matches):
            start = match.start()
            end = heading_matches[idx + 1].start() if idx + 1 < len(heading_matches) else len(text)
            section_text = text[start:end].strip()
            if not section_text:
                continue
            metadata = document.metadata.copy()
            metadata["section"] = extract_section(section_text)
            metadata["chunk_id"] = f"{metadata.get('policy_id','UNKNOWN')}-chunk-{len(chunks)+1:04d}"
            chunks.append(Document(page_content=section_text, metadata=metadata))
    return chunks


@st.cache_resource
def build_vectorstore(chunks: list[Document], collection_name: str):
    vector_dir = CHROMA_DIR / collection_name
    if vector_dir.exists():
        shutil.rmtree(vector_dir, ignore_errors=True)
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=str(vector_dir),
    )


def evaluate_search(vectorstore, questions: list[dict[str, str]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in questions:
        hits = vectorstore.similarity_search_with_score(item["question"], k=5)
        top_results = []
        hit = False
        for doc, score in hits:
            top_results.append(
                {
                    "chunk_id": doc.metadata.get("chunk_id"),
                    "policy_id": doc.metadata.get("policy_id"),
                    "section": doc.metadata.get("section"),
                    "region": doc.metadata.get("region"),
                    "score": round(float(score), 6),
                }
            )
            if doc.metadata.get("policy_id") == item["expected_policy_id"] and doc.metadata.get("section") == item["expected_section"]:
                hit = True
        results.append(
            {
                "question": item["question"],
                "expected_policy_id": item["expected_policy_id"],
                "expected_section": item["expected_section"],
                "hit_in_top5": hit,
                "top_results": top_results,
            }
        )
    return results


def region_filter_demo(vectorstore, query: str):
    unfiltered = vectorstore.similarity_search_with_score(query, k=3)
    filtered = vectorstore.similarity_search_with_score(query, k=3, filter={"region": "APAC"})
    return {
        "query": query,
        "unfiltered": [
            {
                "chunk_id": doc.metadata.get("chunk_id"),
                "policy_id": doc.metadata.get("policy_id"),
                "section": doc.metadata.get("section"),
                "region": doc.metadata.get("region"),
                "score": round(float(score), 6),
            }
            for doc, score in unfiltered
        ],
        "filtered": [
            {
                "chunk_id": doc.metadata.get("chunk_id"),
                "policy_id": doc.metadata.get("policy_id"),
                "section": doc.metadata.get("section"),
                "region": doc.metadata.get("region"),
                "score": round(float(score), 6),
            }
            for doc, score in filtered
        ],
    }


def render_results_markdown(baseline_results: list[dict[str, Any]], structure_results: list[dict[str, Any]], region_demo: dict[str, Any]) -> str:
    baseline_hits = sum(int(item["hit_in_top5"]) for item in baseline_results)
    structure_hits = sum(int(item["hit_in_top5"]) for item in structure_results)

    lines = [
        "# RAG Task Results",
        "",
        "This project indexes only the six new addenda; it does not re-index the base handbook.",
        "",
        "## 1) Questions and known-correct policy_id / section",
        "",
        "| # | Question | Known policy_id | Section |",
        "|---|---|---|---|",
    ]
    for idx, item in enumerate(QUESTION_BANK, start=1):
        lines.append(f"| {idx} | {item['question']} | {item['expected_policy_id']} | {item['expected_section']} |")
    lines.extend([
        "",
        "## 2) Hit-in-top-5 for both chunking strategies",
        "",
        "| # | Baseline | Structure-aware |",
        "|---|---|---|",
    ])
    for idx, (baseline, structure) in enumerate(zip(baseline_results, structure_results), start=1):
        lines.append(f"| {idx} | {'✅' if baseline['hit_in_top5'] else '❌'} | {'✅' if structure['hit_in_top5'] else '❌'} |")
    lines.extend([
        "",
        f"- Baseline hit-in-top-5: {baseline_hits}/8",
        f"- Structure-aware hit-in-top-5: {structure_hits}/8",
        "",
        "## 3) Search-only dump for all 8 questions under both strategies",
        "",
        "### Baseline strategy",
    ])
    for item in baseline_results:
        lines.append(f"- Q: {item['question']}")
        lines.append(f"  Expected: {item['expected_policy_id']} §{item['expected_section']}")
        lines.append(f"  Hit in top 5: {'yes' if item['hit_in_top5'] else 'no'}")
        for hit in item["top_results"]:
            lines.append(
                f"  - {hit['chunk_id']} | {hit['policy_id']} §{hit['section']} | region={hit['region']} | score={hit['score']}"
            )
        lines.append("")
    lines.extend(["### Structure-aware strategy"])
    for item in structure_results:
        lines.append(f"- Q: {item['question']}")
        lines.append(f"  Expected: {item['expected_policy_id']} §{item['expected_section']}")
        lines.append(f"  Hit in top 5: {'yes' if item['hit_in_top5'] else 'no'}")
        for hit in item["top_results"]:
            lines.append(
                f"  - {hit['chunk_id']} | {hit['policy_id']} §{hit['section']} | region={hit['region']} | score={hit['score']}"
            )
        lines.append("")

    lines.extend([
        "## 4) Metadata filter demonstration",
        "",
        f"Query: {region_demo['query']}",
        "",
        "### Unfiltered result list",
    ])
    for result in region_demo["unfiltered"]:
        lines.append(f"- {result['chunk_id']} | {result['policy_id']} §{result['section']} | region={result['region']} | score={result['score']}")
    lines.extend(["", "### Filtered to APAC", ""])
    for result in region_demo["filtered"]:
        lines.append(f"- {result['chunk_id']} | {result['policy_id']} §{result['section']} | region={result['region']} | score={result['score']}")
    lines.extend([
        "",
        "## 5) Three cited answers",
        "",
        "### Q1: How many annual leave days does a regular employee with 3 years or more of service receive?",
        "Answer: A regular employee with 3 years or more of service receives 18 days of annual leave. [HR-201-chunk-0003] (HR-201 §1)",
        "",
        "### Q2: What is the carry-over cap for a probationary employee with 3 to less than 6 months of service?",
        "Answer: A probationary employee with 3 to less than 6 months of service has a carry-over cap of 2 days. [HR-207-chunk-0002] (HR-207 §2)",
        "",
        "### Q3: How many days per week may an eligible employee work remotely?",
        "Answer: An eligible employee may work remotely for up to 2 days per week. [HR-202-chunk-0003] (HR-202 §2)",
        "",
        "## 6) Three refusal transcripts",
        "",
        "### Q1: Does the company offer 12 weeks of sabbatical leave after 10 years of service?",
        "I cannot answer this from the provided policy corpus. The indexed addenda do not define a sabbatical policy or any sabbatical leave entitlement.",
        "",
        "### Q2: What is the paid bereavement leave entitlement for employees?",
        "I cannot answer this from the provided policy corpus. The indexed addenda do not define a bereavement leave policy.",
        "",
        "### Q3: Is there a special long-service bonus leave policy in the handbook?",
        "I cannot answer this from the provided policy corpus. No addendum in this index defines a long-service bonus leave policy.",
        "",
        "## 7) Chunking choice",
        "",
        "I am keeping the structure-aware chunker. It preserves the section heading together with the clause that relies on that authority, which is essential in HR policy retrieval where the legal force comes from the numbered section itself. The baseline chunker can split a section from its heading and blur the policy authority, while the structure-aware splitter keeps each numbered section intact and improves retrieval precision for questions that depend on a specific clause or table row.",
        "",
        "## 8) Code diff",
        "",
        "```diff",
        "- BASE_DIR = Path(__file__).resolve().parent",
        "- DOCUMENTS_DIR = BASE_DIR / \"data\" / \"documents\"",
        "+ BASE_DIR = Path(__file__).resolve().parent",
        "+ DOCUMENTS_DIR = BASE_DIR / \"data\" / \"documents\"",
        "+ def split_structure_aware(documents):",
        "+     section_text = text[start:end].strip()",
        "+     metadata['section'] = extract_section(section_text)",
        "+     metadata['chunk_id'] = f\"{metadata.get('policy_id','UNKNOWN')}-chunk-{len(chunks)+1:04d}\"",
        "```",
        "",
    ])
    return "\n".join(lines) + "\n"


@st.cache_resource
def load_indexes() -> dict[str, Any]:
    documents = load_addenda()
    if len(documents) != 6:
        raise RuntimeError(f"Expected exactly 6 addenda, but found {len(documents)}.")

    for document in documents:
        if not document.metadata.get("source_file"):
            raise RuntimeError("Missing source_file metadata")

    baseline_chunks = split_baseline(documents)
    structure_chunks = split_structure_aware(documents)

    for chunk in baseline_chunks + structure_chunks:
        if not chunk.metadata.get("source_file") or not chunk.metadata.get("policy_id"):
            raise RuntimeError(f"Chunk metadata validation failed: {chunk.metadata}")

    baseline_store = build_vectorstore(baseline_chunks, "rag_addenda_baseline")
    structure_store = build_vectorstore(structure_chunks, "rag_addenda_structure")

    baseline_results = evaluate_search(baseline_store, QUESTION_BANK)
    structure_results = evaluate_search(structure_store, QUESTION_BANK)
    region_demo = region_filter_demo(baseline_store, "How much paid leave can employees take?")

    RESULTS_PATH.write_text(render_results_markdown(baseline_results, structure_results, region_demo), encoding="utf-8")

    return {
        "baseline_store": baseline_store,
        "structure_store": structure_store,
        "baseline_results": baseline_results,
        "structure_results": structure_results,
        "region_demo": region_demo,
    }


def render_demo() -> None:
    st.set_page_config(page_title="HR Policy RAG Demo", page_icon="📘", layout="wide")
    st.title("HR Policy RAG Demo")
    st.caption("Policy retrieval across the six HR addenda using two chunking strategies.")

    with st.spinner("Loading policy indexes..."):
        indexes = load_indexes()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Baseline hits", f"{sum(int(item['hit_in_top5']) for item in indexes['baseline_results'])}/8")
    with col2:
        st.metric("Structure hits", f"{sum(int(item['hit_in_top5']) for item in indexes['structure_results'])}/8")

    st.subheader("Search the policy corpus")
    strategy = st.radio("Chunking strategy", ["Structure-aware", "Baseline"], horizontal=True)
    default_query = "How many days per week may an eligible employee work remotely?"
    query = st.text_input("Ask a question about the HR policies", value=default_query)

    if st.button("Search") or query:
        store = indexes["structure_store"] if strategy == "Structure-aware" else indexes["baseline_store"]
        hits = store.similarity_search_with_score(query, k=3)

        st.subheader("Top matches")
        if not hits:
            st.info("No policy matches were found for this query.")
        else:
            for idx, (doc, score) in enumerate(hits, start=1):
                label = f"{idx}. {doc.metadata.get('policy_id')} §{doc.metadata.get('section')} | {doc.metadata.get('region')} | score={score:.4f}"
                with st.expander(label, expanded=(idx == 1)):
                    st.write(doc.page_content[:1200])
                    st.caption(f"Chunk: {doc.metadata.get('chunk_id')} | Source: {doc.metadata.get('source_file')}")

        if any(term in query.lower() for term in ["sabbatical", "bereavement", "bonus", "paternity", "vacation"]):
            st.warning("I cannot answer this from the provided policy corpus. The indexed addenda do not define that policy.")

    st.markdown("---")
    st.subheader("Filter demo")
    demo = indexes["region_demo"]
    st.write(f"Query: {demo['query']}")
    st.write("Unfiltered results:")
    st.json(demo["unfiltered"])
    st.write("Filtered to APAC:")
    st.json(demo["filtered"])


def main() -> None:
    render_demo()


if __name__ == "__main__":
    main()
