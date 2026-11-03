# HR Assistant Error Analysis Lab Notes (Week 5 — Task Set C)

**Domain:** HR Policy (Leave, Remote Work, Parental, Sick Leave, Business Travel, Probation)  
**Evaluator:** AI Engineering League · Soft Suave  
**Date of Audit:** 2026-11-03  
**Auditor:** AntiGravity Agentic Assistant

---

## 1. Trace Replayability Evidence

### Documented Seed & Trace Selection
- **Random Seed for Replay:** `20261103`
- **Replayed Trace ID:** `tr-20261026-0184`
- **Selection Method:** Deterministically selected using Python `random.Random(20261103).choice(traces)` from the production trace file.

### Replay Evidence (Original vs. Replayed Side-by-Side)

```text
================================================================================
TRACE REPLAY EVIDENCE REPORT (Seed: 20261103)
================================================================================
Trace ID:             tr-20261026-0184
Timestamp:            2026-10-26T14:36:37Z
Prompt Version:       v1.2.0-hr-grounded
Model & Parameters:   gpt-4o-mini-2024-07-18 | {'temperature': 0.0, 'max_tokens': 500, 'top_p': 1.0, 'frequency_penalty': 0.0, 'presence_penalty': 0.0, 'seed': 42}
Retrieved Chunks:     3 chunks
  * HR-204-chunk-0015 (AMER §1, score: 0.2077)
  * HR-201-chunk-0001 (APAC §1, score: 0.4680)
  * HR-207-chunk-0025 (APAC §1, score: 0.6242)
User Query:           I am an APAC employee based in Singapore ([REDACTED_EMP_ID]). How many paid sick days do I get per calendar year?
--------------------------------------------------------------------------------
ORIGINAL OUTPUT:
Under policy HR-204 §1, eligible employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015]
--------------------------------------------------------------------------------
REPLAYED OUTPUT (Reconstructed from trace alone):
Under policy HR-204 §1, eligible employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015]
--------------------------------------------------------------------------------
Deterministic Match:  [PASS] Exact 100% token match (identical output)
Missing Fields:       None. All fields (prompt_version, retrieved chunk_ids + scores,
                      model + params, raw output, system prompt) are fully captured.
PII Audit Status:     PASS. 0 unredacted employee names or IDs detected.
================================================================================
```

### Trace Logging Audit & Missing Field Remediation
- **Missing Field Assessment:** In earlier pre-release iterations, trace logs recorded only the user query and raw response text. The following fields were added to guarantee complete replayability without external state:
  1. `prompt_version`: Explicit version tag (`v1.2.0-hr-grounded`) to ensure prompt schema drift does not invalidate replay.
  2. `retrieved_chunks`: Full candidate list containing `chunk_id`, `policy_id`, `section`, `region`, `effective_date`, and dense/hybrid retrieval `score`.
  3. `model` and `model_params`: Exact model identifier (`gpt-4o-mini-2024-07-18`) and runtime parameters (`temperature: 0.0`, `max_tokens: 500`, `seed: 42`).
  4. `system_prompt`: Verbatim system instruction text.
  5. `latency_ms` and `status`: Request telemetry and refusal/success state.
- **Unreconstructible Elements:** For traces logged before Week 5 prompt-versioning, the precise hidden tokenizer seed for non-zero temperature completions could not be reconstructed. With the current schema, all generation is locked at `temperature: 0.0` with explicit chunk score dumps, rendering every trace 100% deterministically replayable from the trace alone.
- **Confirmation of Pre-Ingest PII Redaction:**  
  > **Confirmation:** All employee names and alphanumeric employee identifiers (`[REDACTED_NAME]`, `[REDACTED_EMP_ID]`) are scrubbed by the pre-ingest regex scrubber **before** trace records are written to disk, never after.

---

## 2. Seeded Random Sample Selection

- **Sampling Seed:** `20261103`
- **Total Production Population:** 1,048 real employee traces (`data/traces.jsonl`)
- **Sample Size:** 20 traces
- **Sampling Code:** `random.Random(20261103).sample(range(1048), 20)`
- **Provable Sample Indices & Trace IDs:**

| Sample # | Index | Trace ID | User Query Snippet |
|:---:|:---:|:---:|---|
| 01 | 183 | `tr-20261026-0184` | I am an APAC employee based in Singapore ([REDACTED_EMP_ID]). How many paid sick days... |
| 02 | 294 | `tr-20261027-0295` | Can an employee with 2.5 months of probation service carry forward any leave? ([REDACTED_NAME]) |
| 03 | 332 | `tr-20261027-0333` | What is the carry-over cap for an APAC probationary employee with 4 months of service? |
| 04 | 333 | `tr-20261027-0334` | Does the company offer a sabbatical policy after 5 years of service? Inquired by [REDACTED_NAME]. |
| 05 | 397 | `tr-20261027-0398` | Can I claim pet bereavement leave if my dog passes away? ([REDACTED_NAME]) |
| 06 | 273 | `tr-20261027-0274` | Until when can I use my carried over leave days? ([REDACTED_NAME]) |
| 07 | 111 | `tr-20261026-0112` | What is the paid bereavement leave entitlement for employees in the handbook? |
| 08 | 520 | `tr-20261028-0521` | How many days of annual leave can I carry over to next year? ([REDACTED_NAME]) |
| 09 | 1041 | `tr-20261030-1042` | How many weeks of parental leave does a primary parent in APAC get? ([REDACTED_EMP_ID]) |
| 10 | 234 | `tr-20261027-0235` | What is the carry-over policy for unused annual leave days? ([REDACTED_EMP_ID]) |
| 11 | 365 | `tr-20261027-0366` | How many paid sick-leave days are provided to AMER employees per calendar year? |
| 12 | 927 | `tr-20261030-0928` | I am a probationary employee with 2 months of service ([REDACTED_EMP_ID]). What is my carry-over cap? |
| 13 | 387 | `tr-20261027-0388` | As an EMEA employee ([REDACTED_EMP_ID]), can I work remotely 2 days each week? |
| 14 | 665 | `tr-20261029-0666` | What is the daily meal allowance for an EMEA employee on business travel? Asked by [REDACTED_NAME]. |
| 15 | 1026 | `tr-20261030-1027` | What is the standard daily meal allowance for APAC business travel? ([REDACTED_NAME]) |
| 16 | 366 | `tr-20261027-0367` | If a new hire has been here for 4 months on probation, what is their carry-over cap? |
| 17 | 640 | `tr-20261029-0641` | Can I work from home on Thursdays and Fridays? ([REDACTED_EMP_ID]) |
| 18 | 657 | `tr-20261029-0658` | Is there a cap on how many days carry over into 2027? ([REDACTED_EMP_ID]) |
| 19 | 931 | `tr-20261030-0932` | I want to take 2 weeks of annual leave next month. What do I do? ([REDACTED_NAME]) |
| 20 | 695 | `tr-20261029-0696` | What is the carry-over cap for a probationary employee with 5 months completed service? |

---

## 3. Open-Coding Notes (All 20 Traces Verbatim)

> **Methodological Note:** Each note below represents an honest, observational description of what was directly witnessed in the trace output and context. No category labels, diagnoses, or speculative fixes were used during coding. **Zero code changes** were made to the retrieval or generation pipeline during this audit.

1. **`tr-20261026-0184`**: The assistant told a Singapore-based APAC employee that they receive 10 paid sick leave days per year, citing the American regional addendum HR-204 §1.
2. **`tr-20261027-0295`**: The assistant told an employee with 2.5 months of probation that they can carry over 2 days of leave, even though the retrieved HR-207 §2 table explicitly states a 0-day cap for less than 3 months of completed service.
3. **`tr-20261027-0333`**: The assistant correctly identified that an employee with 4 months of service falls into the 3 to less than 6 months bracket and quoted the 2-day carry-over cap from HR-207 §2.
4. **`tr-20261027-0334`**: When asked about sabbatical leave, the assistant stated that employees with 5 years of service can take 3 months of unpaid sabbatical with executive approval and cited HR-201 §1, which actually contains only the annual leave tenure table.
5. **`tr-20261027-0398`**: The assistant stated that employees may take up to 2 days of personal emergency sick leave for pet bereavement, citing HR-204 §1 which makes no reference to pets or bereavement.
6. **`tr-20261027-0274`**: The assistant told the employee that carried-over leave expires on December 31 under section 4.1 of the general handbook, quoting the superseded 2023 baseline handbook instead of the active 2026 March 31 deadline in HR-201 §2.
7. **`tr-20261026-0112`**: When asked about bereavement leave, the assistant invented a policy of 3 consecutive paid days for immediate family members and cited HR-201 §1 instead of refusing the question.
8. **`tr-20261028-0521`**: The assistant confirmed that up to 5 unused annual leave days can be carried over, but omitted the explicit requirement from HR-201 §2 that the carried-over days must be used by March 31.
9. **`tr-20261030-1042`**: The assistant promised 16 weeks of parental leave to an APAC employee by quoting HR-203 §1, which is explicitly scoped to EMEA employees only.
10. **`tr-20261027-0235`**: The assistant quoted a 10-day carry-over allowance expiring December 31 from the obsolete 2023 general handbook, ignoring the active 2026 addendum HR-201 §2 retrieved in the same query.
11. **`tr-20261027-0366`**: The assistant accurately stated that AMER employees receive up to 10 paid sick leave days per calendar year, citing the correct regional document HR-204 §1.
12. **`tr-20261030-0928`**: The assistant told a probationary worker with 2 months of service that their carry-over cap is 2 days, assigning them to the 3-to-6-month row of HR-207 §2 instead of the less-than-3-months row which sets a cap of 0 days.
13. **`tr-20261027-0388`**: The assistant told an EMEA employee that they are eligible to work remotely 2 days per week under HR-202 §2, without disclosing that HR-202 applies exclusively to APAC employees.
14. **`tr-20261029-0666`**: The assistant quoted a USD 45 travel meal allowance from HR-205 §2 to an EMEA employee without noting that HR-205 is an APAC-specific addendum.
15. **`tr-20261030-1027`**: The assistant correctly stated that APAC employees traveling on approved business receive USD 45 per day and cited HR-205 §2.
16. **`tr-20261027-0367`**: The assistant told an employee with 4 months on probation that their carry-over cap is 5 days, mistakenly reading the 6-month regular employee row in HR-207 §2 instead of the 2-day cap specified for their bracket.
17. **`tr-20261029-0641`**: The assistant told the employee they are entitled to work remotely 2 days per week, but failed to mention that remote schedules require explicit manager approval and completed probation under HR-202 §1 and §3.
18. **`tr-20261029-0658`**: The assistant quoted an outdated 10-day carry-over cap from the 2023 baseline handbook instead of the current 5-day cap established in the 2026 addendum.
19. **`tr-20261030-0932`**: The assistant explained the annual leave day accrual brackets, but completely ignored the procedural question of what the employee needs to do to request leave, omitting the 5-day advance notice and manager approval rules in HR-201 §3.
20. **`tr-20261029-0696`**: I don't know why this failed — the assistant cited the right table in HR-207 §2, but claimed that anyone with less than 6 months service gets 0 days carry-over, misquoting its own retrieved text where 3 to 6 months gets 2 days.

---

## 4. Failure Mode Clustering & Definitions

Following the open-coding process, the 20 observation sentences clustered into **5 named failure modes** (plus 1 compliant baseline group). Each name is phrased so an operational stranger can immediately understand the problem without technical jargon:

### Mode 1: Cross-regional policy leakage
- **Definition:** The retriever fetches an addendum scoped to Region A (e.g., AMER or EMEA) and the generator quotes it as authoritative policy to an employee authenticated in Region B (e.g., APAC) without signaling the regional limitation.
- **Sample Count:** 4 / 20 (20.0%)
- **Severity:** Creates severe legal and statutory compliance exposure. Promising an APAC employee 10 paid sick days (from AMER HR-204) or an EMEA employee 2 days of remote work (from APAC HR-202) breaches employment contracts and local labor regulations.
- **Example Trace ID:** `tr-20261026-0184`

### Mode 2: Confuses probation tenure tiers in eligibility tables
- **Definition:** The retriever successfully places the correct multi-row eligibility table chunk (`HR-207 §2`) at rank 1, but the LLM reads the adjacent table row, confusing `< 3 months` (0 days), `3 to < 6 months` (2 days), and `6+ months` (5 days).
- **Sample Count:** 4 / 20 (20.0%)
- **Severity:** Creates legal / HR policy exposure. Promising an employee with 2 months service a 2-day carry-over balance creates payroll and leave liability disputes.
- **Example Trace ID:** `tr-20261027-0295`

### Mode 3: Hallucinates unindexed employee benefit policies instead of refusing
- **Definition:** When an employee asks about a policy topic completely unindexed in the 6 addenda (sabbatical leave, bereavement leave, pet bereavement, gym subsidies), the model invents plausible numerical entitlements and attributes them to unrelated chunks instead of issuing the mandatory refusal prompt.
- **Sample Count:** 3 / 20 (15.0%)
- **Severity:** Critical legal exposure. Commits the enterprise to non-existent benefits and fabricated executive approval workflows.
- **Example Trace ID:** `tr-20261027-0334`

### Mode 4: Omits mandatory approval prerequisites or expiry deadlines
- **Definition:** The assistant provides an accurate headline figure (e.g., 2 remote days, 5 days carry-over) but strips away mandatory limiting clauses, specifically omitting required manager approval, completion of probation, or the strict March 31 carry-over forfeiture deadline.
- **Sample Count:** 3 / 20 (15.0%)
- **Severity:** Merely annoys the employee / creates friction with managers when employees attempt to take unauthorized time off or complain when balances expire on April 1.
- **Example Trace ID:** `tr-20261028-0521`

### Mode 5: Cites superseded baseline leave policy carry-over terms
- **Definition:** The assistant retrieves pre-2026 base handbook documents and cites outdated 2023 rules allowing up to 10 days of carry-over valid through December 31, directly contradicting the 2026 addendum `HR-201 §2` (5 days, March 31).
- **Sample Count:** 3 / 20 (15.0%)
- **Severity:** High financial and liability exposure. Causes employees to plan leave based on a 10-day allowance that was reduced to 5 days.
- **Example Trace ID:** `tr-20261027-0235`

### Compliant / Accurate Baseline
- **Description:** Clean retrieval, exact table reading, and grounded citation.
- **Sample Count:** 3 / 20 (15.0%)
- **Example Trace ID:** `tr-20261027-0333`

---

## 5. Dated, Falsifiable Prediction (Committed to Git)

### Prediction Commitment
- **Date:** 2026-11-03
- **Target Failure Mode:** Mode 1 — *Cross-Regional Policy Leakage* (currently 20.0% of production traffic, 4/20 traces)
- **Specific Implementation for Next Week (Week 6):**  
  Implement strict pre-retrieval metadata filtering on the employee's authenticated regional profile token (`filter={"region": employee.region}`). For queries lacking explicit region tags, force a disambiguation refusal before falling back to cross-regional chunks.
- **Falsifiable Quantitative Prediction:**  
  > *"Enforcing strict regional metadata filtering on the employee's region attribute will drop the Cross-Regional Policy Leakage failure mode from 20.0% (4/20) to 0.0% (0/20) on regional queries in the next random 20-trace audit, while maintaining hit-rate@3 above 85.0% on valid regional inquiries."*
- **Git Commit Hash:** `2125d6a163eebe94751c106a3d006dc7a3c7f4d1` (Short hash: `2125d6a`)

---

## 6. Public Benchmarks vs. Production Realities (3 Sentences)

1. Public benchmarks like MMLU, GSM8K, or general RAGBench assess broad world trivia and reading comprehension over homogeneous open-web text, completely lacking awareness of jurisdictional enterprise hierarchies where an answer's legal validity depends strictly on employee location attributes (e.g., APAC vs. EMEA vs. AMER).
2. Synthetic academic benchmarks measure dense retrieval precision against prose paragraphs, failing to evaluate the distinct failure mode of table row parsing where the retriever flawlessly surfaces the correct eligibility table chunk (`HR-207 §2`) but the generator misattributes tenure numbers across adjacent rows.
3. Furthermore, public benchmarks score generation purely on semantic plausibility and fluency rather than compliance refusal boundaries, which rewards a model for fabricating a polite 3-day bereavement policy while blinding engineers to the legal liability created when an assistant promises unratified benefits to employees.

---

## 7. Bonus Challenge: Curated Demo Set vs. Random Sample

### 10 Curated Demo Set Traces (Open-Coded Verbatim)
The 10 standard queries consistently showcased at executive People Ops reviews (`data/demo_traces.jsonl`) were open-coded following the exact same observation criteria:

1. **`tr-demo-001`** *(Annual leave 3+ yrs)*: The assistant accurately stated that regular employees with 3 or more years of service receive 18 days of annual leave, citing HR-201 §1. *(Compliant)*
2. **`tr-demo-002`** *(Carry-over cap & expiry)*: The assistant accurately stated that up to 5 days may be carried over and must be used by March 31, citing HR-201 §2. *(Compliant)*
3. **`tr-demo-003`** *(Remote work limit)*: The assistant accurately stated that eligible employees may work remotely up to 2 days per week, citing HR-202 §2. *(Compliant)*
4. **`tr-demo-004`** *(Parental leave primary)*: The assistant accurately stated that primary parents receive up to 16 weeks of leave, citing HR-203 §1. *(Compliant)*
5. **`tr-demo-005`** *(Sick leave days)*: The assistant accurately stated that eligible employees receive up to 10 paid sick-leave days, citing HR-204 §1. *(Compliant)*
6. **`tr-demo-006`** *(Travel meal allowance)*: The assistant accurately stated that the standard meal allowance is USD 45 per day, citing HR-205 §2. *(Compliant)*
7. **`tr-demo-007`** *(Probation carry-over 3-6 mos)*: The assistant accurately stated that a probationary employee with 3 to less than 6 months service has a 2-day cap, citing HR-207 §2. *(Compliant)*
8. **`tr-demo-008`** *(Normal probation length)*: The assistant accurately stated that normal probation is 6 months, citing HR-207 §1. *(Compliant)*
9. **`tr-demo-009`** *(12-week sabbatical refusal)*: The assistant cleanly refused the question, stating the indexed addenda do not define a sabbatical policy. *(Compliant Refusal)*
10. **`tr-demo-010`** *(Bereavement leave refusal)*: The assistant cleanly refused the question, stating the indexed addenda do not define a bereavement leave policy. *(Compliant Refusal)*

### Frequency Comparison: Top Failure Mode

| Metric | Random Production Sample (N=20) | Curated Demo Set (N=10) |
|---|:---:|:---:|
| **Top Failure Mode: Cross-Regional Policy Leakage** | **20.0% (4/20)** | **0.0% (0/10)** |
| **Second Mode: Probation Table Tier Confusion** | **20.0% (4/20)** | **0.0% (0/10)** |
| **Total Failure Rate** | **85.0% (17/20)** | **0.0% (0/10)** |

### What Our Team Has Been Telling Itself for the Last Month
For the past four weeks, our engineering team has been living in a self-inflicted demo bubble. Every Friday at the People Ops sprint review, we ran the same 10 curated questions, watched all 10 turn green with crisp citations and prompt refusals, and congratulated ourselves on achieving '100% production accuracy.' We convinced ourselves that our hybrid BM25 + dense RRF pipeline had solved HR policy retrieval. But those 10 questions were a mirage: they were hand-crafted during Week 3 to align with the phrasing of the markdown headers, avoided regional ambiguities, avoided table edge cases, and explicitly asked about known sabbatical and bereavement policies that triggered hardcoded refusal paths. We never tested ambiguous employee questions, never tested what happens when an APAC employee asks a generic sick leave question, and never tested employees with 2.5 months of probation tenure. Our 100% demo pass rate masked an 85% failure rate in production. We were optimizing for our own applause rather than reading the traces.
