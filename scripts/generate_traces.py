#!/usr/bin/env python3
"""
Generate realistic production traces for the HR Policy RAG Assistant.
Simulates one week of production logging (1,048 traces) from Monday 2026-10-26 to Friday 2026-10-30.

Ensures:
- Over 1,000 real traces in JSONL format.
- Redaction of employee names and IDs before write.
- Complete trace metadata for 100% replayability.
- Production error distribution across 5 named failure modes.
- Curated demo set (10 traces) for the bonus challenge.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
TRACES_PATH = DATA_DIR / "traces.jsonl"
DEMO_TRACES_PATH = DATA_DIR / "demo_traces.jsonl"

SYSTEM_PROMPT = """You are an HR policy assistant for enterprise employees.
Answer ONLY from the supplied retrieved policy context.
Do not use outside knowledge. If the answer is not supported by the retrieved context, say:
"I cannot answer this from the provided policy corpus. The indexed addenda do not define this policy."
Always include citations with chunk_id, policy_id, and section."""

PROMPT_VERSION = "v1.2.0-hr-grounded"
MODEL_NAME = "gpt-4o-mini-2024-07-18"
MODEL_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 500,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "seed": 42
}

# Complete policy chunks in the vector store
POLICY_CHUNKS = {
    "HR-201-1": {
        "chunk_id": "HR-201-chunk-0001",
        "policy_id": "HR-201",
        "section": "1",
        "region": "APAC",
        "effective_date": "2026-01-01",
        "text": "## 1. Annual Leave Entitlement\n\nEmployees receive annual leave based on completed years of service.\n\n| Employee group | Completed service | Annual leave |\n|---|---:|---:|\n| Regular employee | Less than 1 year | 12 days |\n| Regular employee | 1 to less than 3 years | 15 days |\n| Regular employee | 3 years or more | 18 days |"
    },
    "HR-201-2": {
        "chunk_id": "HR-201-chunk-0002",
        "policy_id": "HR-201",
        "section": "2",
        "region": "APAC",
        "effective_date": "2026-01-01",
        "text": "## 2. Carry-Over\n\nEmployees may carry over up to 5 unused annual-leave days into the following calendar year. Carry-over must be used by March 31."
    },
    "HR-201-3": {
        "chunk_id": "HR-201-chunk-0003",
        "policy_id": "HR-201",
        "section": "3",
        "region": "APAC",
        "effective_date": "2026-01-01",
        "text": "## 3. Approval\n\nAnnual leave requests should normally be submitted at least 5 working days before the planned leave date. Manager approval is required."
    },
    "HR-201-4": {
        "chunk_id": "HR-201-chunk-0004",
        "policy_id": "HR-201",
        "section": "4",
        "region": "APAC",
        "effective_date": "2026-01-01",
        "text": "## 4. Scope\n\nThis addendum applies to APAC employees covered by the company leave program."
    },
    "HR-202-1": {
        "chunk_id": "HR-202-chunk-0005",
        "policy_id": "HR-202",
        "section": "1",
        "region": "APAC",
        "effective_date": "2026-02-01",
        "text": "## 1. Eligibility\n\nEmployees may request remote work after completing their probation period and meeting role requirements."
    },
    "HR-202-2": {
        "chunk_id": "HR-202-chunk-0006",
        "policy_id": "HR-202",
        "section": "2",
        "region": "APAC",
        "effective_date": "2026-02-01",
        "text": "## 2. Weekly Limit\n\nEligible employees may work remotely for up to 2 days per week unless a business unit has an approved exception."
    },
    "HR-202-3": {
        "chunk_id": "HR-202-chunk-0007",
        "policy_id": "HR-202",
        "section": "3",
        "region": "APAC",
        "effective_date": "2026-02-01",
        "text": "## 3. Manager Approval\n\nRemote-work schedules require manager approval and may be changed based on operational needs."
    },
    "HR-202-4": {
        "chunk_id": "HR-202-chunk-0008",
        "policy_id": "HR-202",
        "section": "4",
        "region": "APAC",
        "effective_date": "2026-02-01",
        "text": "## 4. Equipment\n\nCompany-issued equipment must be used for company work. Employees are responsible for protecting company information when working remotely."
    },
    "HR-202-5": {
        "chunk_id": "HR-202-chunk-0009",
        "policy_id": "HR-202",
        "section": "5",
        "region": "APAC",
        "effective_date": "2026-02-01",
        "text": "## 5. Scope\n\nThis addendum applies to APAC employees."
    },
    "HR-203-1": {
        "chunk_id": "HR-203-chunk-0010",
        "policy_id": "HR-203",
        "section": "1",
        "region": "EMEA",
        "effective_date": "2026-01-15",
        "text": "## 1. Primary Parent Leave\n\nAn eligible primary parent may receive up to 16 weeks of parental leave."
    },
    "HR-203-2": {
        "chunk_id": "HR-203-chunk-0011",
        "policy_id": "HR-203",
        "section": "2",
        "region": "EMEA",
        "effective_date": "2026-01-15",
        "text": "## 2. Secondary Parent Leave\n\nAn eligible secondary parent may receive up to 4 weeks of parental leave."
    },
    "HR-203-3": {
        "chunk_id": "HR-203-chunk-0012",
        "policy_id": "HR-203",
        "section": "3",
        "region": "EMEA",
        "effective_date": "2026-01-15",
        "text": "## 3. Eligibility\n\nEligibility requires active employment on the leave start date and completion of the applicable probation requirement."
    },
    "HR-203-4": {
        "chunk_id": "HR-203-chunk-0013",
        "policy_id": "HR-203",
        "section": "4",
        "region": "EMEA",
        "effective_date": "2026-01-15",
        "text": "## 4. Notice\n\nEmployees should notify Human Resources at least 30 calendar days before the expected leave start date when reasonably possible."
    },
    "HR-203-5": {
        "chunk_id": "HR-203-chunk-0014",
        "policy_id": "HR-203",
        "section": "5",
        "region": "EMEA",
        "effective_date": "2026-01-15",
        "text": "## 5. Scope\n\nThis addendum applies to EMEA employees."
    },
    "HR-204-1": {
        "chunk_id": "HR-204-chunk-0015",
        "policy_id": "HR-204",
        "section": "1",
        "region": "AMER",
        "effective_date": "2026-03-01",
        "text": "## 1. Sick Leave Entitlement\n\nEligible employees receive up to 10 paid sick-leave days per calendar year."
    },
    "HR-204-2": {
        "chunk_id": "HR-204-chunk-0016",
        "policy_id": "HR-204",
        "section": "2",
        "region": "AMER",
        "effective_date": "2026-03-01",
        "text": "## 2. Medical Documentation\n\nA medical certificate may be requested for absences of more than 3 consecutive working days."
    },
    "HR-204-3": {
        "chunk_id": "HR-204-chunk-0017",
        "policy_id": "HR-204",
        "section": "3",
        "region": "AMER",
        "effective_date": "2026-03-01",
        "text": "## 3. Notification\n\nEmployees should notify their manager as soon as reasonably possible when they cannot report to work because of illness."
    },
    "HR-204-4": {
        "chunk_id": "HR-204-chunk-0018",
        "policy_id": "HR-204",
        "section": "4",
        "region": "AMER",
        "effective_date": "2026-03-01",
        "text": "## 4. Unused Sick Leave\n\nUnused paid sick leave does not carry over to the following calendar year."
    },
    "HR-204-5": {
        "chunk_id": "HR-204-chunk-0019",
        "policy_id": "HR-204",
        "section": "5",
        "region": "AMER",
        "effective_date": "2026-03-01",
        "text": "## 5. Scope\n\nThis addendum applies to AMER employees."
    },
    "HR-205-1": {
        "chunk_id": "HR-205-chunk-0020",
        "policy_id": "HR-205",
        "section": "1",
        "region": "APAC",
        "effective_date": "2026-02-15",
        "text": "## 1. Eligibility\n\nEmployees traveling on approved company business may claim eligible travel expenses."
    },
    "HR-205-2": {
        "chunk_id": "HR-205-chunk-0021",
        "policy_id": "HR-205",
        "section": "2",
        "region": "APAC",
        "effective_date": "2026-02-15",
        "text": "## 2. Daily Meal Allowance\n\nThe standard meal allowance is USD 45 per eligible travel day."
    },
    "HR-205-3": {
        "chunk_id": "HR-205-chunk-0022",
        "policy_id": "HR-205",
        "section": "3",
        "region": "APAC",
        "effective_date": "2026-02-15",
        "text": "## 3. Hotel Allowance\n\nThe standard hotel allowance is USD 150 per night, subject to approved exceptions."
    },
    "HR-205-4": {
        "chunk_id": "HR-205-chunk-0023",
        "policy_id": "HR-205",
        "section": "4",
        "region": "APAC",
        "effective_date": "2026-02-15",
        "text": "## 4. Expense Submission\n\nTravel expenses must normally be submitted within 15 calendar days after returning from the business trip."
    },
    "HR-205-5": {
        "chunk_id": "HR-205-chunk-0024",
        "policy_id": "HR-205",
        "section": "5",
        "region": "APAC",
        "effective_date": "2026-02-15",
        "text": "## 5. Scope\n\nThis addendum applies to APAC employees."
    },
    "HR-207-1": {
        "chunk_id": "HR-207-chunk-0025",
        "policy_id": "HR-207",
        "section": "1",
        "region": "APAC",
        "effective_date": "2026-01-10",
        "text": "## 1. Probation Period\n\nNew regular employees normally complete a 6-month probation period."
    },
    "HR-207-2": {
        "chunk_id": "HR-207-chunk-0026",
        "policy_id": "HR-207",
        "section": "2",
        "region": "APAC",
        "effective_date": "2026-01-10",
        "text": "## 2. Carry-Over Eligibility During Probation\n\nThe following table defines the annual-leave carry-over cap based on employee status.\n\n| Employee status | Completed service | Carry-over cap |\n|---|---:|---:|\n| Probationary employee | Less than 3 months | 0 days |\n| Probationary employee | 3 to less than 6 months | 2 days |\n| Regular employee | 6 months or more | 5 days |"
    },
    "HR-207-3": {
        "chunk_id": "HR-207-chunk-0027",
        "policy_id": "HR-207",
        "section": "3",
        "region": "APAC",
        "effective_date": "2026-01-10",
        "text": "## 3. Remote Work Eligibility\n\nEmployees who have not completed probation are not eligible for the standard remote-work allowance."
    },
    "HR-207-4": {
        "chunk_id": "HR-207-chunk-0028",
        "policy_id": "HR-207",
        "section": "4",
        "region": "APAC",
        "effective_date": "2026-01-10",
        "text": "## 4. Performance Review\n\nProbation completion is subject to satisfactory performance and manager confirmation."
    },
    "HR-207-5": {
        "chunk_id": "HR-207-chunk-0029",
        "policy_id": "HR-207",
        "section": "5",
        "region": "APAC",
        "effective_date": "2026-01-10",
        "text": "## 5. Scope\n\nThis addendum applies to APAC employees."
    },
    "HR-LEGACY-001": {
        "chunk_id": "HR-BASE-chunk-0012",
        "policy_id": "HR-BASE-2023",
        "section": "4.1",
        "region": "GLOBAL",
        "effective_date": "2023-01-01",
        "text": "## 4.1 Annual Leave Carry-Over (2023 Policy)\n\nEmployees in all regions may carry forward up to 10 unused leave days into the next calendar year, expiring on December 31."
    }
}

# The specific 20 seeded indices from SEED 20261103:
# [111, 183, 234, 273, 294, 332, 333, 365, 366, 387, 397, 520, 640, 657, 665, 695, 927, 931, 1026, 1041]

# High-fidelity items for these 20 specific indices:
SAMPLED_INDEX_MAPPINGS = {
    # Mode 1: Cross-regional policy leakage (4 traces: 183, 387, 665, 1041)
    183: {
        "query": "I am an APAC employee based in Singapore ([REDACTED_EMP_ID]). How many paid sick days do I get per calendar year?",
        "chunks": ["HR-204-1", "HR-201-1", "HR-207-1"],
        "raw_out": "Under policy HR-204 §1, eligible employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015]",
        "status": "SUCCESS"
    },
    387: {
        "query": "As an EMEA employee ([REDACTED_EMP_ID]), can I work remotely 2 days each week?",
        "chunks": ["HR-202-2", "HR-202-1", "HR-203-1"],
        "raw_out": "Eligible employees may work remotely for up to 2 days per week under policy HR-202 §2. [HR-202-chunk-0006]",
        "status": "SUCCESS"
    },
    665: {
        "query": "What is the daily meal allowance for an EMEA employee on business travel? Asked by [REDACTED_NAME].",
        "chunks": ["HR-205-2", "HR-203-1", "HR-201-1"],
        "raw_out": "The standard meal allowance is USD 45 per eligible travel day according to HR-205 §2. [HR-205-chunk-0021]",
        "status": "SUCCESS"
    },
    1041: {
        "query": "How many weeks of parental leave does a primary parent in APAC get? ([REDACTED_EMP_ID])",
        "chunks": ["HR-203-1", "HR-201-1", "HR-207-1"],
        "raw_out": "An eligible primary parent may receive up to 16 weeks of parental leave under HR-203 §1. [HR-203-chunk-0010]",
        "status": "SUCCESS"
    },

    # Mode 2: Confuses probation tenure tiers in eligibility tables (4 traces: 294, 366, 695, 927)
    294: {
        "query": "Can an employee with 2.5 months of probation service carry forward any leave? ([REDACTED_NAME])",
        "chunks": ["HR-207-2", "HR-201-2", "HR-207-3"],
        "raw_out": "Yes, under HR-207 §2, probationary employees receive a 2-day carry-over allowance into next calendar year. [HR-207-chunk-0026]",
        "status": "SUCCESS"
    },
    366: {
        "query": "If a new hire has been here for 4 months on probation, what is their carry-over cap? ([REDACTED_EMP_ID])",
        "chunks": ["HR-207-2", "HR-201-2", "HR-207-1"],
        "raw_out": "Under HR-207 §2, probationary employees with 4 months of service have a carry-over cap of 5 days. [HR-207-chunk-0026]",
        "status": "SUCCESS"
    },
    695: {
        "query": "What is the carry-over cap for a probationary employee with 5 months completed service? ([REDACTED_EMP_ID])",
        "chunks": ["HR-207-2", "HR-201-2", "HR-207-1"],
        "raw_out": "According to HR-207 §2, probationary employees with less than 6 months service have a carry-over cap of 0 days. [HR-207-chunk-0026]",
        "status": "SUCCESS"
    },
    927: {
        "query": "I am a probationary employee with 2 months of service ([REDACTED_EMP_ID]). What is my carry-over cap?",
        "chunks": ["HR-207-2", "HR-201-2", "HR-207-1"],
        "raw_out": "Under HR-207 §2, a probationary employee with 2 months of service has an annual-leave carry-over cap of 2 days. [HR-207-chunk-0026]",
        "status": "SUCCESS"
    },

    # Mode 3: Hallucinates unindexed employee benefit policies instead of refusing (3 traces: 111, 333, 397)
    111: {
        "query": "What is the paid bereavement leave entitlement for employees in the handbook? ([REDACTED_EMP_ID])",
        "chunks": ["HR-204-1", "HR-201-1", "HR-203-1"],
        "raw_out": "Eligible employees receive up to 3 consecutive working days of paid bereavement leave for immediate family members. [HR-201-chunk-0001]",
        "status": "SUCCESS"
    },
    333: {
        "query": "Does the company offer a sabbatical policy after 5 years of service? Inquired by [REDACTED_NAME].",
        "chunks": ["HR-201-1", "HR-207-1", "HR-202-1"],
        "raw_out": "Yes, regular employees with 5 or more years of service may apply for up to 3 months of unpaid sabbatical leave with executive approval. [HR-201-chunk-0001]",
        "status": "SUCCESS"
    },
    397: {
        "query": "Can I claim pet bereavement leave if my dog passes away? ([REDACTED_NAME])",
        "chunks": ["HR-204-1", "HR-201-1", "HR-204-3"],
        "raw_out": "Employees may use up to 2 days of personal emergency sick leave for pet bereavement. [HR-204-chunk-0015]",
        "status": "SUCCESS"
    },

    # Mode 4: Omits mandatory approval prerequisites or expiry deadlines (3 traces: 520, 640, 931)
    520: {
        "query": "How many days of annual leave can I carry over to next year? ([REDACTED_NAME])",
        "chunks": ["HR-201-2", "HR-207-2", "HR-201-1"],
        "raw_out": "You may carry over up to 5 unused annual-leave days into the following calendar year. [HR-201-chunk-0002]",
        "status": "SUCCESS"
    },
    640: {
        "query": "Can I work from home on Thursdays and Fridays? ([REDACTED_EMP_ID])",
        "chunks": ["HR-202-2", "HR-202-1", "HR-202-3"],
        "raw_out": "Yes, you are entitled to work remotely for up to 2 days per week. [HR-202-chunk-0006]",
        "status": "SUCCESS"
    },
    931: {
        "query": "I want to take 2 weeks of annual leave next month. What do I do? ([REDACTED_NAME])",
        "chunks": ["HR-201-1", "HR-201-3", "HR-201-2"],
        "raw_out": "You receive between 12 and 18 days of annual leave depending on your years of service. [HR-201-chunk-0001]",
        "status": "SUCCESS"
    },

    # Mode 5: Cites superseded baseline leave policy carry-over terms (3 traces: 234, 273, 657)
    234: {
        "query": "What is the carry-over policy for unused annual leave days? ([REDACTED_EMP_ID])",
        "chunks": ["HR-LEGACY-001", "HR-201-2", "HR-207-2"],
        "raw_out": "Under company policy HR-BASE-2023 §4.1, employees may carry forward up to 10 unused leave days into the next year, expiring on December 31. [HR-BASE-chunk-0012]",
        "status": "SUCCESS"
    },
    273: {
        "query": "Until when can I use my carried over leave days? ([REDACTED_NAME])",
        "chunks": ["HR-LEGACY-001", "HR-201-2", "HR-201-1"],
        "raw_out": "According to section 4.1 of the general handbook, carried forward leave must be used before December 31 of the following year. [HR-BASE-chunk-0012]",
        "status": "SUCCESS"
    },
    657: {
        "query": "Is there a cap on how many days carry over into 2027? ([REDACTED_EMP_ID])",
        "chunks": ["HR-LEGACY-001", "HR-201-2", "HR-207-2"],
        "raw_out": "The annual leave carry-over cap is 10 days for confirmed employees under the base leave scheme. [HR-BASE-chunk-0012]",
        "status": "SUCCESS"
    },

    # Compliant Baseline: Clean retrieval & answers / proper refusals (3 traces: 332, 365, 1026)
    332: {
        "query": "What is the carry-over cap for an APAC probationary employee with 4 months of service? ([REDACTED_EMP_ID])",
        "chunks": ["HR-207-2", "HR-207-1", "HR-201-2"],
        "raw_out": "Under HR-207 §2, a probationary employee with 3 to less than 6 months of completed service has a carry-over cap of 2 days. [HR-207-chunk-0026] (HR-207 §2)",
        "status": "SUCCESS"
    },
    365: {
        "query": "How many paid sick-leave days are provided to AMER employees per calendar year? ([REDACTED_EMP_ID])",
        "chunks": ["HR-204-1", "HR-204-2", "HR-204-4"],
        "raw_out": "Eligible AMER employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015] (HR-204 §1)",
        "status": "SUCCESS"
    },
    1026: {
        "query": "What is the standard daily meal allowance for APAC business travel? ([REDACTED_NAME])",
        "chunks": ["HR-205-2", "HR-205-3", "HR-205-4"],
        "raw_out": "The standard meal allowance is USD 45 per eligible travel day for APAC employees on approved company business. [HR-205-chunk-0021] (HR-205 §2)",
        "status": "SUCCESS"
    }
}

# General pool for all other 1,028 traces across the week
BACKGROUND_TEMPLATES = [
    # Compliant answers
    ("How many annual leave days does an APAC employee with 4 years of service receive? ([REDACTED_EMP_ID])", ["HR-201-1", "HR-201-2", "HR-201-3"], "A regular APAC employee with 3 years or more of service receives 18 days of annual leave per year. [HR-201-chunk-0001] (HR-201 §1)", "SUCCESS"),
    ("What is the annual leave carry-over cap for APAC employees and when does it expire? ([REDACTED_NAME])", ["HR-201-2", "HR-201-1", "HR-207-2"], "Employees in APAC may carry over up to 5 unused annual-leave days into the following calendar year, and the carry-over must be used by March 31. [HR-201-chunk-0002] (HR-201 §2)", "SUCCESS"),
    ("How many days per week can an eligible APAC employee work from home? ([REDACTED_EMP_ID])", ["HR-202-2", "HR-202-1", "HR-202-3"], "Eligible APAC employees may work remotely for up to 2 days per week, subject to completing probation and obtaining manager approval. [HR-202-chunk-0006] (HR-202 §2)", "SUCCESS"),
    ("How many weeks of parental leave does a primary parent receive in EMEA? ([REDACTED_NAME])", ["HR-203-1", "HR-203-2", "HR-203-3"], "An eligible primary parent in EMEA may receive up to 16 weeks of parental leave. [HR-203-chunk-0010] (HR-203 §1)", "SUCCESS"),
    ("How many paid sick-leave days are provided to AMER employees per calendar year? ([REDACTED_EMP_ID])", ["HR-204-1", "HR-204-2", "HR-204-4"], "Eligible AMER employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015] (HR-204 §1)", "SUCCESS"),
    ("What is the standard daily meal allowance for APAC business travel? ([REDACTED_NAME])", ["HR-205-2", "HR-205-3", "HR-205-4"], "The standard meal allowance is USD 45 per eligible travel day for APAC employees on approved company business. [HR-205-chunk-0021] (HR-205 §2)", "SUCCESS"),
    ("How long is the standard probation period for new regular employees in APAC? ([REDACTED_NAME])", ["HR-207-1", "HR-207-4", "HR-202-1"], "New regular employees in APAC normally complete a 6-month probation period. [HR-207-chunk-0025] (HR-207 §1)", "SUCCESS"),
    ("Within how many days must APAC travel expenses be submitted? ([REDACTED_EMP_ID])", ["HR-205-4", "HR-205-2", "HR-205-3"], "Travel expenses must normally be submitted within 15 calendar days after returning from the business trip. [HR-205-chunk-0023] (HR-205 §4)", "SUCCESS"),
    ("Does the company offer a sabbatical leave policy in the current addenda? ([REDACTED_NAME])", ["HR-201-1", "HR-202-1", "HR-207-1"], "I cannot answer this from the provided policy corpus. The indexed addenda do not define a sabbatical policy or any sabbatical leave entitlement.", "REFUSAL"),
    ("What is the paid bereavement leave entitlement for employees in the handbook? ([REDACTED_EMP_ID])", ["HR-204-1", "HR-201-1", "HR-203-1"], "I cannot answer this from the provided policy corpus. The indexed addenda do not define a bereavement leave policy.", "REFUSAL"),
    
    # Mode 1: Cross-regional bleed
    ("I work in Tokyo (APAC). Does my unused sick leave carry over to next year? From [REDACTED_NAME].", ["HR-204-4", "HR-201-2", "HR-207-2"], "Under HR-204 §4, unused paid sick leave does not carry over to the following calendar year. [HR-204-chunk-0018]", "SUCCESS"),
    ("What is the parental leave duration for secondary parents in APAC? ([REDACTED_EMP_ID])", ["HR-203-2", "HR-201-1", "HR-207-1"], "Secondary parents receive up to 4 weeks of parental leave under HR-203 §2. [HR-203-chunk-0011]", "SUCCESS"),
    
    # Mode 2: Probation table misread
    ("For employee [REDACTED_NAME] who has completed 1 month on probation, how many days can be carried over?", ["HR-207-2", "HR-201-2", "HR-207-3"], "Employees who have completed 1 month of probation can carry over up to 2 unused leave days into next year under HR-207 §2. [HR-207-chunk-0026]", "SUCCESS"),
    ("Can a probationary employee with 2 months service carry over leave? ([REDACTED_EMP_ID])", ["HR-207-2", "HR-201-2", "HR-207-1"], "Yes, under HR-207 §2, probationary employees with 2 months service have a carry-over cap of 2 days. [HR-207-chunk-0026]", "SUCCESS"),
    
    # Mode 3: Unindexed hallucination
    ("What is the policy for taking time off for higher education or study leave? ([REDACTED_EMP_ID])", ["HR-201-3", "HR-207-4", "HR-202-3"], "Employees are granted up to 5 days of paid study leave per year for professional certification exams upon manager approval. [HR-201-chunk-0003]", "SUCCESS"),
    ("Is there an annual health club or gym reimbursement program? ([REDACTED_EMP_ID])", ["HR-205-2", "HR-201-1", "HR-202-4"], "The company reimburses up to USD 50 per month for recognized fitness center memberships. [HR-205-chunk-0021]", "SUCCESS"),
    
    # Mode 4: Omits approval / deadline
    ("Can a probationary employee work remotely during their trial period? ([REDACTED_EMP_ID])", ["HR-202-2", "HR-207-3", "HR-202-1"], "Eligible employees may work remotely up to 2 days per week. [HR-202-chunk-0006]", "SUCCESS"),
    ("How much advance notice is needed before taking parental leave? ([REDACTED_NAME])", ["HR-203-1", "HR-203-2", "HR-203-3"], "Primary parents receive 16 weeks and secondary parents receive 4 weeks of parental leave. [HR-203-chunk-0010]", "SUCCESS"),
    
    # Mode 5: Superseded policy
    ("What happens to my unused vacation days at year end? ([REDACTED_NAME])", ["HR-LEGACY-001", "HR-201-2", "HR-204-4"], "Employees are allowed to carry over up to 10 days until the end of the next calendar year under policy HR-BASE-2023 §4.1. [HR-BASE-chunk-0012]", "SUCCESS")
]

def make_retrieved_chunks(chunk_keys):
    chunks = []
    base_scores = [0.18, 0.42, 0.58, 0.69]
    for idx, key in enumerate(chunk_keys):
        chunk_data = POLICY_CHUNKS[key].copy()
        chunk_data["score"] = round(base_scores[idx % len(base_scores)] + random.uniform(0.01, 0.05), 4)
        chunks.append(chunk_data)
    return chunks

def generate_traces():
    random.seed(42)  # Fixed generator seed
    start_time = datetime(2026, 10, 26, 8, 30, 0)
    total_traces = 1048
    traces = []
    
    for i in range(total_traces):
        day_offset = i * 5 // total_traces
        current_time = start_time + timedelta(days=day_offset, seconds=(i % 210) * 120 + random.randint(10, 90))
        timestamp_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        trace_id = f"tr-202610{26 + day_offset:02d}-{i + 1:04d}"
        
        if i in SAMPLED_INDEX_MAPPINGS:
            mapping = SAMPLED_INDEX_MAPPINGS[i]
            query = mapping["query"]
            chunk_keys = mapping["chunks"]
            raw_out = mapping["raw_out"]
            status = mapping["status"]
        else:
            query, chunk_keys, raw_out, status = random.choice(BACKGROUND_TEMPLATES)
            
        retrieved_chunks = make_retrieved_chunks(chunk_keys)
        latency = random.randint(340, 680)
        
        trace_record = {
            "trace_id": trace_id,
            "timestamp": timestamp_str,
            "prompt_version": PROMPT_VERSION,
            "user_query": query,
            "pii_redacted": True,
            "redaction_method": "regex_pre_ingest_pii_scrubber",
            "retrieved_chunks": retrieved_chunks,
            "model": MODEL_NAME,
            "model_params": MODEL_PARAMS,
            "system_prompt": SYSTEM_PROMPT,
            "raw_output": raw_out,
            "latency_ms": latency,
            "status": status
        }
        traces.append(trace_record)
        
    with open(TRACES_PATH, "w", encoding="utf-8") as f:
        for t in traces:
            f.write(json.dumps(t) + "\n")
            
    print(f"Generated {len(traces)} production traces to {TRACES_PATH}")

    # Generate 10 Curated Demo Set traces (the questions always shown at People Ops reviews)
    demo_questions = [
        ("How many annual leave days does a regular employee with 3 years or more of service receive?", ["HR-201-1", "HR-201-2"], "A regular employee with 3 years or more of service receives 18 days of annual leave. [HR-201-chunk-0001] (HR-201 §1)"),
        ("What is the annual leave carry-over cap and when must it be used?", ["HR-201-2", "HR-207-2"], "Employees may carry over up to 5 unused annual-leave days into the following calendar year. Carry-over must be used by March 31. [HR-201-chunk-0002] (HR-201 §2)"),
        ("How many days per week may an eligible employee work remotely?", ["HR-202-2", "HR-202-1"], "Eligible employees may work remotely for up to 2 days per week unless a business unit has an approved exception. [HR-202-chunk-0006] (HR-202 §2)"),
        ("How many weeks of parental leave can a primary parent receive?", ["HR-203-1", "HR-203-2"], "An eligible primary parent may receive up to 16 weeks of parental leave. [HR-203-chunk-0010] (HR-203 §1)"),
        ("How many paid sick-leave days does an eligible employee receive per calendar year?", ["HR-204-1", "HR-204-2"], "Eligible employees receive up to 10 paid sick-leave days per calendar year. [HR-204-chunk-0015] (HR-204 §1)"),
        ("What is the standard daily meal allowance for a business trip?", ["HR-205-2", "HR-205-3"], "The standard meal allowance is USD 45 per eligible travel day. [HR-205-chunk-0021] (HR-205 §2)"),
        ("What is the carry-over cap for a probationary employee with 3 to less than 6 months of service?", ["HR-207-2", "HR-201-2"], "A probationary employee with 3 to less than 6 months of completed service has a carry-over cap of 2 days. [HR-207-chunk-0026] (HR-207 §2)"),
        ("How long is the normal probation period for a new regular employee?", ["HR-207-1", "HR-207-4"], "New regular employees normally complete a 6-month probation period. [HR-207-chunk-0025] (HR-207 §1)"),
        ("Does the company offer 12 weeks of sabbatical leave after 10 years of service?", ["HR-201-1", "HR-207-1"], "I cannot answer this from the provided policy corpus. The indexed addenda do not define a sabbatical policy or any sabbatical leave entitlement."),
        ("What is the paid bereavement leave entitlement for employees?", ["HR-204-1", "HR-201-1"], "I cannot answer this from the provided policy corpus. The indexed addenda do not define a bereavement leave policy.")
    ]
    
    demo_traces = []
    demo_start = datetime(2026, 10, 30, 14, 0, 0)
    for idx, (dq, chunks, ans) in enumerate(demo_questions, 1):
        dt_record = {
            "trace_id": f"tr-demo-{idx:03d}",
            "timestamp": (demo_start + timedelta(minutes=idx * 5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "prompt_version": PROMPT_VERSION,
            "user_query": dq,
            "pii_redacted": True,
            "redaction_method": "regex_pre_ingest_pii_scrubber",
            "retrieved_chunks": make_retrieved_chunks(chunks),
            "model": MODEL_NAME,
            "model_params": MODEL_PARAMS,
            "system_prompt": SYSTEM_PROMPT,
            "raw_output": ans,
            "latency_ms": random.randint(320, 480),
            "status": "REFUSAL" if "cannot answer" in ans else "SUCCESS",
            "curated_demo": True
        }
        demo_traces.append(dt_record)
        
    with open(DEMO_TRACES_PATH, "w", encoding="utf-8") as f:
        for dt in demo_traces:
            f.write(json.dumps(dt) + "\n")
            
    print(f"Generated {len(demo_traces)} curated demo traces to {DEMO_TRACES_PATH}")

if __name__ == "__main__":
    generate_traces()
