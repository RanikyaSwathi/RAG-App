"""
Evaluation questions for HR policy RAG.

All answers are verified against the actual policy documents.
"""

EVALUATION_QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the carry-over cap for a probationary employee under HR-207 section 4.2?",
        "expected_answer": "2 days",
        "expected_policy_id": "HR-207",
        "expected_section": "4.2",
        "expected_region": "Kerala",
        "note": "From HR-207-Kerala.md, eligibility table shows probationary employee carry-over cap is 2 days",
    },
    {
        "id": "Q2",
        "question": "What is the carry-over cap for a confirmed employee in Bangalore?",
        "expected_answer": "9 days",
        "expected_policy_id": "HR-202",
        "expected_section": "4.2",
        "expected_region": "Bangalore",
        "note": "From HR-202-Bangalore.md, eligibility table shows confirmed employee carry-over cap is 9 days",
    },
    {
        "id": "Q3",
        "question": "What is the carry-over cap for a confirmed employee in Chennai?",
        "expected_answer": "8 days",
        "expected_policy_id": "HR-203",
        "expected_section": "4.2",
        "expected_region": "Chennai",
        "note": "From HR-203-Chennai.md, eligibility table shows confirmed employee carry-over cap is 8 days",
    },
    {
        "id": "Q4",
        "question": "What is the carry-over cap for a confirmed employee in Hyderabad?",
        "expected_answer": "7 days",
        "expected_policy_id": "HR-204",
        "expected_section": "4.2",
        "expected_region": "Hyderabad",
        "note": "From HR-204-Hyderabad.md, eligibility table shows confirmed employee carry-over cap is 7 days",
    },
    {
        "id": "Q5",
        "question": "How many casual/sick leaves are listed for Bangalore in section 4.3?",
        "expected_answer": "15",
        "expected_policy_id": "HR-202",
        "expected_section": "4.3",
        "expected_region": "Bangalore",
        "note": "From HR-202-Bangalore.md, section 4.3 regional leave table shows Casual/Sick Leave = 15",
    },
    {
        "id": "Q6",
        "question": "How many privilege leaves are listed for Chennai in section 4.3?",
        "expected_answer": "3",
        "expected_policy_id": "HR-203",
        "expected_section": "4.3",
        "expected_region": "Chennai",
        "note": "From HR-203-Chennai.md, section 4.3 regional leave table shows Privilege Leave = 3",
    },
    {
        "id": "Q7",
        "question": "What is the carry-over cap for a confirmed employee in Pune?",
        "expected_answer": "10 days",
        "expected_policy_id": "HR-205",
        "expected_section": "4.2",
        "expected_region": "Pune",
        "note": "From HR-205-Pune.md, eligibility table shows confirmed employee carry-over cap is 10 days",
    },
    {
        "id": "Q8",
        "question": "What is the carry-over cap for a confirmed employee in Mumbai?",
        "expected_answer": "6 days",
        "expected_policy_id": "HR-206",
        "expected_section": "4.2",
        "expected_region": "Mumbai",
        "note": "From HR-206-Mumbai.md, eligibility table shows confirmed employee carry-over cap is 6 days",
    },
]


# Answerable questions (3+) - answers are in the policies
ANSWERABLE_QUESTIONS = [
    {
        "id": "A1",
        "question": "What is the probationary employee carry-over cap under HR-207 section 4.2?",
        "expected_policy_id": "HR-207",
        "expected_section": "4.2",
    },
    {
        "id": "A2",
        "question": "What is the carry-over cap for a confirmed employee in Pune?",
        "expected_policy_id": "HR-205",
        "expected_section": "4.2",
    },
    {
        "id": "A3",
        "question": "How many privilege leaves are listed for Chennai?",
        "expected_policy_id": "HR-203",
        "expected_section": "4.3",
    },
]


# Unanswerable questions (3+) - answers are NOT in the policies
UNANSWERABLE_QUESTIONS = [
    {
        "id": "U1",
        "question": "What is the company's sabbatical leave policy?",
        "reason": "No sabbatical leave policy is mentioned in any of the HR addenda",
    },
    {
        "id": "U2",
        "question": "What is the company's relocation allowance?",
        "reason": "No relocation allowance information is present in the policy documents",
    },
    {
        "id": "U3",
        "question": "What is HR-999's carry-over policy?",
        "reason": "HR-999 does not exist; only HR-202 through HR-207 are in the policies",
    },
]
