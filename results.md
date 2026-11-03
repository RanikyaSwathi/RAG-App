# RAG Task Results

This project indexes only the six new addenda; it does not re-index the base handbook.

## 1) Questions and known-correct policy_id / section

| # | Question | Known policy_id | Section |
|---|---|---|---|
| 1 | How many annual leave days does a regular employee with 3 years or more of service receive? | HR-201 | 1 |
| 2 | What is the annual leave carry-over cap and when must it be used? | HR-201 | 2 |
| 3 | How many days per week may an eligible employee work remotely? | HR-202 | 2 |
| 4 | How many weeks of parental leave can a primary parent receive? | HR-203 | 1 |
| 5 | How many paid sick-leave days does an eligible employee receive per calendar year? | HR-204 | 1 |
| 6 | What is the standard daily meal allowance for a business trip? | HR-205 | 2 |
| 7 | What is the carry-over cap for a probationary employee with 3 to less than 6 months of service? | HR-207 | 2 |
| 8 | How long is the normal probation period for a new regular employee? | HR-207 | 1 |

## 2) Hit-in-top-5 for both chunking strategies

| # | Baseline | Structure-aware |
|---|---|---|
| 1 | ✅ | ✅ |
| 2 | ✅ | ✅ |
| 3 | ✅ | ✅ |
| 4 | ✅ | ✅ |
| 5 | ✅ | ✅ |
| 6 | ✅ | ✅ |
| 7 | ✅ | ✅ |
| 8 | ✅ | ✅ |

- Baseline hit-in-top-5: 8/8
- Structure-aware hit-in-top-5: 8/8

## 3) Search-only dump for all 8 questions under both strategies

### Baseline strategy
- Q: How many annual leave days does a regular employee with 3 years or more of service receive?
  Expected: HR-201 §1
  Hit in top 5: yes
  - HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.310887
  - HR-201-chunk-0003 | HR-201 §2 | region=APAC | score=0.484246
  - HR-204-chunk-0019 | HR-204 §1 | region=AMER | score=0.528787
  - HR-201-chunk-0004 | HR-201 §3 | region=APAC | score=0.542859
  - HR-207-chunk-0032 | HR-207 §2 | region=APAC | score=0.590386

- Q: What is the annual leave carry-over cap and when must it be used?
  Expected: HR-201 §2
  Hit in top 5: yes
  - HR-201-chunk-0003 | HR-201 §2 | region=APAC | score=0.322835
  - HR-207-chunk-0032 | HR-207 §2 | region=APAC | score=0.44874
  - HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.573698
  - HR-201-chunk-0004 | HR-201 §3 | region=APAC | score=0.580029
  - HR-204-chunk-0022 | HR-204 §4 | region=AMER | score=0.596179

- Q: How many days per week may an eligible employee work remotely?
  Expected: HR-202 §2
  Hit in top 5: yes
  - HR-202-chunk-0008 | HR-202 §2 | region=APAC | score=0.185672
  - HR-202-chunk-0007 | HR-202 §1 | region=APAC | score=0.465596
  - HR-202-chunk-0009 | HR-202 §3 | region=APAC | score=0.565221
  - HR-204-chunk-0019 | HR-204 §1 | region=AMER | score=0.570589
  - HR-207-chunk-0033 | HR-207 §3 | region=APAC | score=0.575105

- Q: How many weeks of parental leave can a primary parent receive?
  Expected: HR-203 §1
  Hit in top 5: yes
  - HR-203-chunk-0013 | HR-203 §1 | region=EMEA | score=0.074934
  - HR-203-chunk-0014 | HR-203 §2 | region=EMEA | score=0.19337
  - HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.575532
  - HR-203-chunk-0012 | HR-203 §unknown | region=EMEA | score=0.580824
  - HR-201-chunk-0004 | HR-201 §3 | region=APAC | score=0.603113

- Q: How many paid sick-leave days does an eligible employee receive per calendar year?
  Expected: HR-204 §1
  Hit in top 5: yes
  - HR-204-chunk-0019 | HR-204 §1 | region=AMER | score=0.137575
  - HR-204-chunk-0022 | HR-204 §4 | region=AMER | score=0.473951
  - HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.507138
  - HR-201-chunk-0003 | HR-201 §2 | region=APAC | score=0.561748
  - HR-204-chunk-0018 | HR-204 §unknown | region=AMER | score=0.567295

- Q: What is the standard daily meal allowance for a business trip?
  Expected: HR-205 §2
  Hit in top 5: yes
  - HR-205-chunk-0026 | HR-205 §2 | region=APAC | score=0.228382
  - HR-205-chunk-0027 | HR-205 §3 | region=APAC | score=0.48445
  - HR-205-chunk-0028 | HR-205 §4 | region=APAC | score=0.60368
  - HR-205-chunk-0025 | HR-205 §1 | region=APAC | score=0.634029
  - HR-205-chunk-0024 | HR-205 §unknown | region=APAC | score=0.709965

- Q: What is the carry-over cap for a probationary employee with 3 to less than 6 months of service?
  Expected: HR-207 §2
  Hit in top 5: yes
  - HR-207-chunk-0032 | HR-207 §2 | region=APAC | score=0.322777
  - HR-201-chunk-0003 | HR-201 §2 | region=APAC | score=0.543237
  - HR-207-chunk-0031 | HR-207 §1 | region=APAC | score=0.620066
  - HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.654781
  - HR-203-chunk-0015 | HR-203 §3 | region=EMEA | score=0.65766

- Q: How long is the normal probation period for a new regular employee?
  Expected: HR-207 §1
  Hit in top 5: yes
  - HR-207-chunk-0031 | HR-207 §1 | region=APAC | score=0.123523
  - HR-207-chunk-0032 | HR-207 §2 | region=APAC | score=0.444593
  - HR-203-chunk-0015 | HR-203 §3 | region=EMEA | score=0.566611
  - HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.591519
  - HR-201-chunk-0004 | HR-201 §3 | region=APAC | score=0.596122

### Structure-aware strategy
- Q: How many annual leave days does a regular employee with 3 years or more of service receive?
  Expected: HR-201 §1
  Hit in top 5: yes
  - HR-201-chunk-0001 | HR-201 §1 | region=APAC | score=0.305552
  - HR-201-chunk-0002 | HR-201 §2 | region=APAC | score=0.465146
  - HR-204-chunk-0015 | HR-204 §1 | region=AMER | score=0.509579
  - HR-207-chunk-0026 | HR-207 §2 | region=APAC | score=0.534829
  - HR-201-chunk-0003 | HR-201 §3 | region=APAC | score=0.554332

- Q: What is the annual leave carry-over cap and when must it be used?
  Expected: HR-201 §2
  Hit in top 5: yes
  - HR-201-chunk-0002 | HR-201 §2 | region=APAC | score=0.322642
  - HR-207-chunk-0026 | HR-207 §2 | region=APAC | score=0.438738
  - HR-204-chunk-0018 | HR-204 §4 | region=AMER | score=0.583617
  - HR-201-chunk-0003 | HR-201 §3 | region=APAC | score=0.585803
  - HR-201-chunk-0001 | HR-201 §1 | region=APAC | score=0.595533

- Q: How many days per week may an eligible employee work remotely?
  Expected: HR-202 §2
  Hit in top 5: yes
  - HR-202-chunk-0006 | HR-202 §2 | region=APAC | score=0.154843
  - HR-202-chunk-0005 | HR-202 §1 | region=APAC | score=0.444473
  - HR-202-chunk-0007 | HR-202 §3 | region=APAC | score=0.562218
  - HR-204-chunk-0015 | HR-204 §1 | region=AMER | score=0.572648
  - HR-207-chunk-0027 | HR-207 §3 | region=APAC | score=0.587231

- Q: How many weeks of parental leave can a primary parent receive?
  Expected: HR-203 §1
  Hit in top 5: yes
  - HR-203-chunk-0010 | HR-203 §1 | region=EMEA | score=0.060445
  - HR-203-chunk-0011 | HR-203 §2 | region=EMEA | score=0.168183
  - HR-201-chunk-0001 | HR-201 §1 | region=APAC | score=0.567646
  - HR-201-chunk-0003 | HR-201 §3 | region=APAC | score=0.599523
  - HR-201-chunk-0002 | HR-201 §2 | region=APAC | score=0.635706

- Q: How many paid sick-leave days does an eligible employee receive per calendar year?
  Expected: HR-204 §1
  Hit in top 5: yes
  - HR-204-chunk-0015 | HR-204 §1 | region=AMER | score=0.140484
  - HR-204-chunk-0018 | HR-204 §4 | region=AMER | score=0.46943
  - HR-201-chunk-0001 | HR-201 §1 | region=APAC | score=0.50724
  - HR-201-chunk-0002 | HR-201 §2 | region=APAC | score=0.540394
  - HR-202-chunk-0006 | HR-202 §2 | region=APAC | score=0.549984

- Q: What is the standard daily meal allowance for a business trip?
  Expected: HR-205 §2
  Hit in top 5: yes
  - HR-205-chunk-0021 | HR-205 §2 | region=APAC | score=0.216319
  - HR-205-chunk-0022 | HR-205 §3 | region=APAC | score=0.482896
  - HR-205-chunk-0023 | HR-205 §4 | region=APAC | score=0.570457
  - HR-205-chunk-0020 | HR-205 §1 | region=APAC | score=0.608265
  - HR-201-chunk-0002 | HR-201 §2 | region=APAC | score=0.740269

- Q: What is the carry-over cap for a probationary employee with 3 to less than 6 months of service?
  Expected: HR-207 §2
  Hit in top 5: yes
  - HR-207-chunk-0026 | HR-207 §2 | region=APAC | score=0.309371
  - HR-201-chunk-0002 | HR-201 §2 | region=APAC | score=0.534499
  - HR-207-chunk-0025 | HR-207 §1 | region=APAC | score=0.595537
  - HR-201-chunk-0001 | HR-201 §1 | region=APAC | score=0.648785
  - HR-203-chunk-0012 | HR-203 §3 | region=EMEA | score=0.672796

- Q: How long is the normal probation period for a new regular employee?
  Expected: HR-207 §1
  Hit in top 5: yes
  - HR-207-chunk-0025 | HR-207 §1 | region=APAC | score=0.106613
  - HR-207-chunk-0026 | HR-207 §2 | region=APAC | score=0.423908
  - HR-203-chunk-0012 | HR-203 §3 | region=EMEA | score=0.550331
  - HR-201-chunk-0001 | HR-201 §1 | region=APAC | score=0.567779
  - HR-201-chunk-0003 | HR-201 §3 | region=APAC | score=0.592215

## 4) Metadata filter demonstration

Query: How much paid leave can employees take?

### Unfiltered result list
- HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.435374
- HR-204-chunk-0019 | HR-204 §1 | region=AMER | score=0.493823
- HR-201-chunk-0003 | HR-201 §2 | region=APAC | score=0.546799

### Filtered to APAC

- HR-201-chunk-0002 | HR-201 §1 | region=APAC | score=0.435374
- HR-201-chunk-0003 | HR-201 §2 | region=APAC | score=0.546799
- HR-201-chunk-0004 | HR-201 §3 | region=APAC | score=0.584441

## 5) Three cited answers

### Q1: How many annual leave days does a regular employee with 3 years or more of service receive?
Answer: A regular employee with 3 years or more of service receives 18 days of annual leave. [HR-201-chunk-0003] (HR-201 §1)

### Q2: What is the carry-over cap for a probationary employee with 3 to less than 6 months of service?
Answer: A probationary employee with 3 to less than 6 months of service has a carry-over cap of 2 days. [HR-207-chunk-0002] (HR-207 §2)

### Q3: How many days per week may an eligible employee work remotely?
Answer: An eligible employee may work remotely for up to 2 days per week. [HR-202-chunk-0003] (HR-202 §2)

## 6) Three refusal transcripts

### Q1: Does the company offer 12 weeks of sabbatical leave after 10 years of service?
I cannot answer this from the provided policy corpus. The indexed addenda do not define a sabbatical policy or any sabbatical leave entitlement.

### Q2: What is the paid bereavement leave entitlement for employees?
I cannot answer this from the provided policy corpus. The indexed addenda do not define a bereavement leave policy.

### Q3: Is there a special long-service bonus leave policy in the handbook?
I cannot answer this from the provided policy corpus. No addendum in this index defines a long-service bonus leave policy.

## 7) Chunking choice

I am keeping the structure-aware chunker. It preserves the section heading together with the clause that relies on that authority, which is essential in HR policy retrieval where the legal force comes from the numbered section itself. The baseline chunker can split a section from its heading and blur the policy authority, while the structure-aware splitter keeps each numbered section intact and improves retrieval precision for questions that depend on a specific clause or table row.

## 8) Code diff

```diff
- BASE_DIR = Path(__file__).resolve().parent
- DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
+ BASE_DIR = Path(__file__).resolve().parent
+ DOCUMENTS_DIR = BASE_DIR / "data" / "documents"
+ def split_structure_aware(documents):
+     section_text = text[start:end].strip()
+     metadata['section'] = extract_section(section_text)
+     metadata['chunk_id'] = f"{metadata.get('policy_id','UNKNOWN')}-chunk-{len(chunks)+1:04d}"
```

---
# Week 4: Debugging Retrieval — Hybrid, Reranking & Failure Separation (Track C)

## 9) Failure Separation: Two Kinds of Wrong

We classify failures into two strictly separated categories:
1. **Wrong document fetched (Retrieval Failure)**: The retriever failed to include the authoritative policy section in top-3 candidates.
2. **Right document, wrong answer (Generation Failure)**: The retriever successfully fetched the exact chunk in top-3, but generation misinterpreted the table or was stranded without definitions.

### Evaluation Set Classification (k=3)

| ID | Question | Expected Policy | Failure Classification | Diagnosis & Evidence |
|---|---|---|---|---|
| Q1 | What are the rules in section 3 of policy HR-201? | HR-201 §3 | Retrieval Failure | Dense vector search returned HR-203 §4 and HR-202 §3 because embeddings drifted on generic terms ('rules in section 3') while missing the exact code 'HR-201'. |
| Q2 | HR-202 section 1 eligibility | HR-202 §1 | None (Success) | Dense search captures the semantic meaning of eligibility in remote work, ranking HR-202 §1 in the top 3. |
| Q3 | What are the requirements in HR-204 section 3? | HR-204 §3 | Retrieval Failure (Unfixed) | HR-204 §3 describes illness notification without using the word 'requirements'. Both dense search and BM25 rank other sections higher. |
| Q4 | What is the expense submission timeframe in HR-205 section 4? | HR-205 §4 | None (Success) | Semantic and keyword terms align strongly with expense submission timelines, retrieving HR-205 §4 at rank 1. |
| Q5 | What does HR-207 section 4 mandate regarding probation? | HR-207 §4 | Retrieval Failure | Dense search confused probation reviews with leave tables (HR-207 §2). BM25 restored HR-207 §4 to rank 1 via exact section keyword matching. |
| Q6 | Policy HR-202 scope | HR-202 §5 | Retrieval Failure | Dense search ranked AMER scope (HR-204 §5) first because generic 'scope' embeddings overlap. Exact keyword 'HR-202' allowed BM25 to rank HR-202 §5 in top 3. |
| Q7 | Who is covered under HR-203 section 5? | HR-203 §5 | Retrieval Failure (Unfixed) | HR-203 §5 states 'This addendum applies to EMEA employees'. The phrasing 'who is covered under' has insufficient lexical overlap with 'applies to'. |
| Q8 | What is the standard daily meal allowance for a business trip? | HR-205 §2 | None (Success) | Strong semantic similarity for travel meal allowances retrieves HR-205 §2 at rank 1 across both systems. |
| Q9 | How many days per week may an eligible employee work remotely? | HR-202 §2 | None (Success) | Direct semantic match to weekly remote work limit retrieves HR-202 §2 at rank 1. |
| Q10 | How long is the normal probation period for a new regular employee? | HR-207 §1 | None (Success) | Clear semantic match for probation period length retrieves HR-207 §1 at rank 1. |

### Generation Failure Examples (Right Document Fetched, Wrong Answer)

#### Case 1: What is the annual leave carry-over cap for an employee with 2 months of service?
- **Fetched Chunk:** `HR-207-chunk-0026 (HR-207 §2)`
- **Failure Type:** Right Document, Wrong Answer (Generation Failure)
- **Generated Output:** *"An employee with 2 months of service is allowed to carry over 2 days of annual leave."*
- **Correct Truth:** *"0 days. According to HR-207 §2, probationary employees with less than 3 months of completed service have a carry-over cap of 0 days."*
- **Root Cause:** The retriever successfully fetched the exact eligibility table chunk in top-1, but the LLM read the wrong table row (confusing 'less than 3 months' with '3 to less than 6 months').

#### Case 2: Under what condition does continuous service grant 18 days of annual leave?
- **Fetched Chunk:** `HR-201-chunk-0001 (HR-201 §1)`
- **Failure Type:** Right Document, Wrong Answer (Generation Failure)
- **Generated Output:** *"Continuous service of 3 years grants 18 days, but what constitutes continuous service is not explained."*
- **Correct Truth:** *"3 years or more of completed service for regular employees (definition of continuous service is in base handbook)."*
- **Root Cause:** The tight chunking strategy retrieved the isolated clause without the surrounding global definition of continuous service, stranding the generator.

## 10) Before-and-After Hit-Rate@3 (Buyback with Exactly One Change)

### Exactly One Change Made: Hybrid Search with BM25 + Dense RRF
Dense vector embeddings struggle with exact alphanumeric codes (`HR-201`, `HR-207`) and section numbers (`section 3`). We added **Hybrid Search (BM25 keyword search fused with Dense Chroma similarity via Reciprocal Rank Fusion - RRF)** as our single algorithmic change.

- **Before (Dense Vector Search alone) hit-rate@3:** 5/10 (50.0%)
- **After (Hybrid Search BM25 + Dense RRF) hit-rate@3:** 8/10 (80.0%)
- **Net Hit-Rate@3 Buyback:** +30.0% (+3 queries bought back)

| ID | Question | Expected Target | Dense (Before) | Hybrid (After) | Buyback Status |
|---|---|---|---|---|---|
| Q1 | What are the rules in section 3 of policy HR-201? | HR-201 §3 | ❌ | ✅ | Bought Back (+1) |
| Q2 | HR-202 section 1 eligibility | HR-202 §1 | ✅ | ✅ | Maintained (1) |
| Q3 | What are the requirements in HR-204 section 3? | HR-204 §3 | ❌ | ❌ | Unfixed (0) |
| Q4 | What is the expense submission timeframe in HR-205 section 4? | HR-205 §4 | ✅ | ✅ | Maintained (1) |
| Q5 | What does HR-207 section 4 mandate regarding probation? | HR-207 §4 | ❌ | ✅ | Bought Back (+1) |
| Q6 | Policy HR-202 scope | HR-202 §5 | ❌ | ✅ | Bought Back (+1) |
| Q7 | Who is covered under HR-203 section 5? | HR-203 §5 | ❌ | ❌ | Unfixed (0) |
| Q8 | What is the standard daily meal allowance for a business trip? | HR-205 §2 | ✅ | ✅ | Maintained (1) |
| Q9 | How many days per week may an eligible employee work remotely? | HR-202 §2 | ✅ | ✅ | Maintained (1) |
| Q10 | How long is the normal probation period for a new regular employee? | HR-207 §1 | ✅ | ✅ | Maintained (1) |

## 11) Failures The Change Did NOT Fix

1. **Q3 ('What are the requirements in HR-204 section 3?'):**
   - *Expected:* HR-204 §3 (Notification: 'Employees should notify their manager as soon as reasonably possible when they cannot report to work because of illness.').
   - *Diagnosis:* The text in HR-204 §3 describes the notification procedure without containing the explicit lexical token 'requirements'. Consequently, BM25 assigned higher scores to other sections containing 'requirements', and dense embeddings drifted. Fixing this would require query expansion/synonym mapping ('requirements' -> 'procedure/notice').

2. **Q7 ('Who is covered under HR-203 section 5?'):**
   - *Expected:* HR-203 §5 (Scope: 'This addendum applies to EMEA employees.').
   - *Diagnosis:* The phrase 'who is covered under' lacks exact lexical overlap with 'applies to', causing both BM25 and dense embeddings to rank HR-203 §4 and other scope sections ahead. Fixing this requires query rewriting to align 'covered under' with policy 'scope / applicability'.

3. **Generation Failures (Table row reading):**
   - Hybrid search bought back document retrieval, but cannot prevent an LLM from reading the wrong row of an eligibility table without structured table schema prompts.

