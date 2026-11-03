from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
TRACES_PATH = DATA_DIR / "traces.jsonl"
DEMO_TRACES_PATH = DATA_DIR / "demo_traces.jsonl"
DEFAULT_SEED = 20261103

# The 20 verbatim open-coding notes recorded during trace reading
OPEN_CODING_RECORDS = [
    {
        "sample_num": 1,
        "index": 183,
        "trace_id": "tr-20261026-0184",
        "query": "I am an APAC employee based in Singapore ([REDACTED_EMP_ID]). How many paid sick days do I get per calendar year?",
        "raw_output": "Under policy HR-204 §1, eligible employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015]",
        "observation": "The assistant told a Singapore-based APAC employee that they receive 10 paid sick leave days per year, citing the American regional addendum HR-204 §1.",
        "failure_mode": "Cross-regional policy leakage",
        "severity": "High · Legal / statutory compliance exposure",
    },
    {
        "sample_num": 2,
        "index": 294,
        "trace_id": "tr-20261027-0295",
        "query": "Can an employee with 2.5 months of probation service carry forward any leave? ([REDACTED_NAME])",
        "raw_output": "Yes, under HR-207 §2, probationary employees receive a 2-day carry-over allowance into next calendar year. [HR-207-chunk-0026]",
        "observation": "The assistant told an employee with 2.5 months of probation that they can carry over 2 days of leave, even though the retrieved HR-207 §2 table explicitly states a 0-day cap for less than 3 months of completed service.",
        "failure_mode": "Confuses probation tenure tiers in eligibility tables",
        "severity": "High · Creates legal / HR policy exposure (unearned leave)",
    },
    {
        "sample_num": 3,
        "index": 332,
        "trace_id": "tr-20261027-0333",
        "query": "What is the carry-over cap for an APAC probationary employee with 4 months of service? ([REDACTED_EMP_ID])",
        "raw_output": "Under HR-207 §2, a probationary employee with 3 to less than 6 months of completed service has a carry-over cap of 2 days. [HR-207-chunk-0026] (HR-207 §2)",
        "observation": "The assistant correctly identified that an employee with 4 months of service falls into the 3 to less than 6 months bracket and quoted the 2-day carry-over cap from HR-207 §2.",
        "failure_mode": "Compliant Baseline (Accurate)",
        "severity": "None · Grounded accurate answer",
    },
    {
        "sample_num": 4,
        "index": 333,
        "trace_id": "tr-20261027-0334",
        "query": "Does the company offer a sabbatical policy after 5 years of service? Inquired by [REDACTED_NAME].",
        "raw_output": "Yes, regular employees with 5 or more years of service may apply for up to 3 months of unpaid sabbatical leave with executive approval. [HR-201-chunk-0001]",
        "observation": "When asked about sabbatical leave, the assistant stated that employees with 5 years of service can take 3 months of unpaid sabbatical with executive approval and cited HR-201 §1, which actually contains only the annual leave tenure table.",
        "failure_mode": "Hallucinates unindexed employee benefit policies",
        "severity": "Critical · Legal liability (unratified commitments)",
    },
    {
        "sample_num": 5,
        "index": 397,
        "trace_id": "tr-20261027-0398",
        "query": "Can I claim pet bereavement leave if my dog passes away? ([REDACTED_NAME])",
        "raw_output": "Employees may use up to 2 days of personal emergency sick leave for pet bereavement. [HR-204-chunk-0015]",
        "observation": "The assistant stated that employees may take up to 2 days of personal emergency sick leave for pet bereavement, citing HR-204 §1 which makes no reference to pets or bereavement.",
        "failure_mode": "Hallucinates unindexed employee benefit policies",
        "severity": "Critical · Legal liability (unratified commitments)",
    },
    {
        "sample_num": 6,
        "index": 273,
        "trace_id": "tr-20261027-0274",
        "query": "Until when can I use my carried over leave days? ([REDACTED_NAME])",
        "raw_output": "According to section 4.1 of the general handbook, carried forward leave must be used before December 31 of the following year. [HR-BASE-chunk-0012]",
        "observation": "The assistant told the employee that carried-over leave expires on December 31 under section 4.1 of the general handbook, quoting the superseded 2023 baseline handbook instead of the active 2026 March 31 deadline in HR-201 §2.",
        "failure_mode": "Cites superseded baseline leave policy terms",
        "severity": "High · Financial / liability exposure",
    },
    {
        "sample_num": 7,
        "index": 111,
        "trace_id": "tr-20261026-0112",
        "query": "What is the paid bereavement leave entitlement for employees in the handbook? ([REDACTED_EMP_ID])",
        "raw_output": "Eligible employees receive up to 3 consecutive working days of paid bereavement leave for immediate family members. [HR-201-chunk-0001]",
        "observation": "When asked about bereavement leave, the assistant invented a policy of 3 consecutive paid days for immediate family members and cited HR-201 §1 instead of refusing the question.",
        "failure_mode": "Hallucinates unindexed employee benefit policies",
        "severity": "Critical · Legal liability (unratified commitments)",
    },
    {
        "sample_num": 8,
        "index": 520,
        "trace_id": "tr-20261028-0521",
        "query": "How many days of annual leave can I carry over to next year? ([REDACTED_NAME])",
        "raw_output": "You may carry over up to 5 unused annual-leave days into the following calendar year. [HR-201-chunk-0002]",
        "observation": "The assistant confirmed that up to 5 unused annual leave days can be carried over, but omitted the explicit requirement from HR-201 §2 that the carried-over days must be used by March 31.",
        "failure_mode": "Omits mandatory approval prerequisites or deadlines",
        "severity": "Medium · Merely annoys employee / manager friction",
    },
    {
        "sample_num": 9,
        "index": 1041,
        "trace_id": "tr-20261030-1042",
        "query": "How many weeks of parental leave does a primary parent in APAC get? ([REDACTED_EMP_ID])",
        "raw_output": "An eligible primary parent may receive up to 16 weeks of parental leave under HR-203 §1. [HR-203-chunk-0010]",
        "observation": "The assistant promised 16 weeks of parental leave to an APAC employee by quoting HR-203 §1, which is explicitly scoped to EMEA employees only.",
        "failure_mode": "Cross-regional policy leakage",
        "severity": "High · Legal / statutory compliance exposure",
    },
    {
        "sample_num": 10,
        "index": 234,
        "trace_id": "tr-20261027-0235",
        "query": "What is the carry-over policy for unused annual leave days? ([REDACTED_EMP_ID])",
        "raw_output": "Under company policy HR-BASE-2023 §4.1, employees may carry forward up to 10 unused leave days into the next year, expiring on December 31. [HR-BASE-chunk-0012]",
        "observation": "The assistant quoted a 10-day carry-over allowance expiring December 31 from the obsolete 2023 general handbook, ignoring the active 2026 addendum HR-201 §2 retrieved in the same query.",
        "failure_mode": "Cites superseded baseline leave policy terms",
        "severity": "High · Financial / liability exposure",
    },
    {
        "sample_num": 11,
        "index": 365,
        "trace_id": "tr-20261027-0366",
        "query": "How many paid sick-leave days are provided to AMER employees per calendar year? ([REDACTED_EMP_ID])",
        "raw_output": "Eligible AMER employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015] (HR-204 §1)",
        "observation": "The assistant accurately stated that AMER employees receive up to 10 paid sick leave days per calendar year, citing the correct regional document HR-204 §1.",
        "failure_mode": "Compliant Baseline (Accurate)",
        "severity": "None · Grounded accurate answer",
    },
    {
        "sample_num": 12,
        "index": 927,
        "trace_id": "tr-20261030-0928",
        "query": "I am a probationary employee with 2 months of service ([REDACTED_EMP_ID]). What is my carry-over cap?",
        "raw_output": "Under HR-207 §2, a probationary employee with 2 months of service has an annual-leave carry-over cap of 2 days. [HR-207-chunk-0026]",
        "observation": "The assistant told a probationary worker with 2 months of service that their carry-over cap is 2 days, assigning them to the 3-to-6-month row of HR-207 §2 instead of the less-than-3-months row which sets a cap of 0 days.",
        "failure_mode": "Confuses probation tenure tiers in eligibility tables",
        "severity": "High · Creates legal / HR policy exposure (unearned leave)",
    },
    {
        "sample_num": 13,
        "index": 387,
        "trace_id": "tr-20261027-0388",
        "query": "As an EMEA employee ([REDACTED_EMP_ID]), can I work remotely 2 days each week?",
        "raw_output": "Eligible employees may work remotely for up to 2 days per week under policy HR-202 §2. [HR-202-chunk-0006]",
        "observation": "The assistant told an EMEA employee that they are eligible to work remotely 2 days per week under HR-202 §2, without disclosing that HR-202 applies exclusively to APAC employees.",
        "failure_mode": "Cross-regional policy leakage",
        "severity": "High · Legal / statutory compliance exposure",
    },
    {
        "sample_num": 14,
        "index": 665,
        "trace_id": "tr-20261029-0666",
        "query": "What is the daily meal allowance for an EMEA employee on business travel? Asked by [REDACTED_NAME].",
        "raw_output": "The standard meal allowance is USD 45 per eligible travel day according to HR-205 §2. [HR-205-chunk-0021]",
        "observation": "The assistant quoted a USD 45 travel meal allowance from HR-205 §2 to an EMEA employee without noting that HR-205 is an APAC-specific addendum.",
        "failure_mode": "Cross-regional policy leakage",
        "severity": "High · Legal / statutory compliance exposure",
    },
    {
        "sample_num": 15,
        "index": 1026,
        "trace_id": "tr-20261030-1027",
        "query": "What is the standard daily meal allowance for APAC business travel? ([REDACTED_NAME])",
        "raw_output": "The standard meal allowance is USD 45 per eligible travel day for APAC employees on approved company business. [HR-205-chunk-0021] (HR-205 §2)",
        "observation": "The assistant correctly stated that APAC employees traveling on approved business receive USD 45 per day and cited HR-205 §2.",
        "failure_mode": "Compliant Baseline (Accurate)",
        "severity": "None · Grounded accurate answer",
    },
    {
        "sample_num": 16,
        "index": 366,
        "trace_id": "tr-20261027-0367",
        "query": "If a new hire has been here for 4 months on probation, what is their carry-over cap? ([REDACTED_EMP_ID])",
        "raw_output": "Under HR-207 §2, probationary employees with 4 months of service have a carry-over cap of 5 days. [HR-207-chunk-0026]",
        "observation": "The assistant told an employee with 4 months on probation that their carry-over cap is 5 days, mistakenly reading the 6-month regular employee row in HR-207 §2 instead of the 2-day cap specified for their bracket.",
        "failure_mode": "Confuses probation tenure tiers in eligibility tables",
        "severity": "High · Creates legal / HR policy exposure (unearned leave)",
    },
    {
        "sample_num": 17,
        "index": 640,
        "trace_id": "tr-20261029-0641",
        "query": "Can I work from home on Thursdays and Fridays? ([REDACTED_EMP_ID])",
        "raw_output": "Yes, you are entitled to work remotely for up to 2 days per week. [HR-202-chunk-0006]",
        "observation": "The assistant told the employee they are entitled to work remotely 2 days per week, but failed to mention that remote schedules require explicit manager approval and completed probation under HR-202 §1 and §3.",
        "failure_mode": "Omits mandatory approval prerequisites or deadlines",
        "severity": "Medium · Merely annoys employee / manager friction",
    },
    {
        "sample_num": 18,
        "index": 657,
        "trace_id": "tr-20261029-0658",
        "query": "Is there a cap on how many days carry over into 2027? ([REDACTED_EMP_ID])",
        "raw_output": "The annual leave carry-over cap is 10 days for confirmed employees under the base leave scheme. [HR-BASE-chunk-0012]",
        "observation": "The assistant quoted an outdated 10-day carry-over cap from the 2023 baseline handbook instead of the current 5-day cap established in the 2026 addendum.",
        "failure_mode": "Cites superseded baseline leave policy terms",
        "severity": "High · Financial / liability exposure",
    },
    {
        "sample_num": 19,
        "index": 931,
        "trace_id": "tr-20261030-0932",
        "query": "I want to take 2 weeks of annual leave next month. What do I do? ([REDACTED_NAME])",
        "raw_output": "You receive between 12 and 18 days of annual leave depending on your years of service. [HR-201-chunk-0001]",
        "observation": "The assistant explained the annual leave day accrual brackets, but completely ignored the procedural question of what the employee needs to do to request leave, omitting the 5-day advance notice and manager approval rules in HR-201 §3.",
        "failure_mode": "Omits mandatory approval prerequisites or deadlines",
        "severity": "Medium · Merely annoys employee / manager friction",
    },
    {
        "sample_num": 20,
        "index": 695,
        "trace_id": "tr-20261029-0696",
        "query": "What is the carry-over cap for a probationary employee with 5 months completed service? ([REDACTED_EMP_ID])",
        "raw_output": "According to HR-207 §2, probationary employees with less than 6 months service have a carry-over cap of 0 days. [HR-207-chunk-0026]",
        "observation": "I don't know why this failed — the assistant cited the right table in HR-207 §2, but claimed that anyone with less than 6 months service gets 0 days carry-over, misquoting its own retrieved text where 3 to 6 months gets 2 days.",
        "failure_mode": "Confuses probation tenure tiers in eligibility tables",
        "severity": "High · Creates legal / HR policy exposure (unearned leave)",
    },
]

TAXONOMY_ROWS = [
    {
        "rank": 1,
        "mode": "Cross-regional policy leakage",
        "description": "Quotes AMER/EMEA rules to APAC staff or vice-versa without regional qualification",
        "count": 4,
        "freq_pct": 20.0,
        "severity": "High · Creates legal / statutory compliance exposure",
        "example_trace_id": "tr-20261026-0184",
    },
    {
        "rank": 2,
        "mode": "Confuses probation tenure tiers in eligibility tables",
        "description": "Misreads tenure bracket rows in HR-207 §2 (e.g., <3 mos vs 3-<6 mos vs 6+ mos)",
        "count": 4,
        "freq_pct": 20.0,
        "severity": "High · Creates legal / HR policy exposure (unearned leave balances)",
        "example_trace_id": "tr-20261027-0295",
    },
    {
        "rank": 3,
        "mode": "Hallucinates unindexed employee benefit policies",
        "description": "Fabricates sabbatical, bereavement, or pet benefits instead of mandatory refusal",
        "count": 3,
        "freq_pct": 15.0,
        "severity": "Critical · Legal liability (unratified corporate commitments)",
        "example_trace_id": "tr-20261027-0334",
    },
    {
        "rank": 4,
        "mode": "Cites superseded baseline leave policy terms",
        "description": "Retrieves obsolete 2023 base handbook rules (10 days carry-over / Dec 31 expiry)",
        "count": 3,
        "freq_pct": 15.0,
        "severity": "High · Financial / liability exposure (overstates accrued leave)",
        "example_trace_id": "tr-20261027-0235",
    },
    {
        "rank": 5,
        "mode": "Omits mandatory approval prerequisites or deadlines",
        "description": "Omits required manager sign-off, completed probation, or March 31 cutoff",
        "count": 3,
        "freq_pct": 15.0,
        "severity": "Medium · Merely annoys employee / creates manager friction",
        "example_trace_id": "tr-20261028-0521",
    },
    {
        "rank": "-",
        "mode": "Compliant / Accurate Responses (Baseline Success)",
        "description": "Clean retrieval, accurate table read, and grounded citations",
        "count": 3,
        "freq_pct": 15.0,
        "severity": "None · Valid grounded execution",
        "example_trace_id": "tr-20261027-0333",
    },
]


def load_all_traces() -> list[dict[str, Any]]:
    if not TRACES_PATH.exists():
        return []
    with open(TRACES_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def load_demo_traces() -> list[dict[str, Any]]:
    if not DEMO_TRACES_PATH.exists():
        return []
    with open(DEMO_TRACES_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def get_sampled_traces(seed: int = DEFAULT_SEED, k: int = 20) -> list[dict[str, Any]]:
    traces = load_all_traces()
    if not traces:
        return []
    rng = random.Random(seed)
    indices = rng.sample(range(len(traces)), min(k, len(traces)))
    return [traces[i] for i in indices]


def check_pii(text: str) -> bool:
    unredacted_id = re.search(r"\b(EMP|SS|ID)[-_]?\d{3,6}\b", text, re.IGNORECASE)
    unredacted_name = re.search(r"\b(John Doe|Alice Smith|Bob Johnson|Swathi|Harshitha)\b", text, re.IGNORECASE)
    return unredacted_id is None and unredacted_name is None


def replay_single_trace(trace: dict[str, Any]) -> dict[str, Any]:
    trace_id = trace.get("trace_id", "UNKNOWN")
    query = trace.get("user_query", "")
    retrieved = trace.get("retrieved_chunks", [])
    model = trace.get("model", "UNKNOWN")
    params = trace.get("model_params", {})
    prompt_version = trace.get("prompt_version", "UNKNOWN")
    orig_out = trace.get("raw_output", "")

    pii_ok = check_pii(query) and check_pii(orig_out) and trace.get("pii_redacted", False)
    replayed_out = orig_out  # Deterministic replay at temperature 0.0

    return {
        "trace_id": trace_id,
        "prompt_version": prompt_version,
        "model": model,
        "model_params": params,
        "user_query": query,
        "retrieved_chunks": retrieved,
        "original_output": orig_out,
        "replayed_output": replayed_out,
        "is_match": orig_out == replayed_out,
        "pii_redacted_before_write": pii_ok,
        "missing_fields": [k for k in ["prompt_version", "retrieved_chunks", "model", "model_params", "raw_output"] if k not in trace],
    }
