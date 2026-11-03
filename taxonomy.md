# HR Assistant Error Taxonomy (Week 5 — Task Set C)

**Corpus:** HR Policy Addenda (HR-201, HR-202, HR-203, HR-204, HR-205, HR-207)  
**Sample:** 20 production traces randomly drawn from 1,048 weekly logs (`Seed = 20261103`)  
**Audit Date:** 2026-11-03 | **Evaluator:** AI Engineering League (Soft Suave)

---

### Ranked Failure Modes

| Rank | Failure Mode | Count | Freq (%) | Severity | Example Trace ID |
|:---:|---|:---:|:---:|---|:---:|
| **1** | **Cross-regional policy leakage**<br>*(Quotes AMER/EMEA rules to APAC staff or vice-versa)* | 4 | 20.0% | **High** · Creates legal / statutory compliance exposure | `tr-20261026-0184` |
| **2** | **Confuses probation tenure tiers in eligibility tables**<br>*(Misreads bracket rows in HR-207 §2)* | 4 | 20.0% | **High** · Creates legal / HR policy exposure (unearned leave) | `tr-20261027-0295` |
| **3** | **Hallucinates unindexed employee benefit policies**<br>*(Invents sabbatical/bereavement rules instead of refusing)* | 3 | 15.0% | **Critical** · Creates legal liability (unratified commitments) | `tr-20261027-0334` |
| **4** | **Cites superseded baseline leave policy terms**<br>*(Quotes obsolete 2023 10-day cap / Dec 31 deadline)* | 3 | 15.0% | **High** · Creates financial liability (overstates accruals) | `tr-20261027-0235` |
| **5** | **Omits mandatory approval prerequisites or deadlines**<br>*(Leaves out manager sign-off or March 31 cutoff)* | 3 | 15.0% | **Medium** · Merely annoys employee / manager friction | `tr-20261028-0521` |
| — | *Compliant / Accurate Responses (Baseline Success)* | 3 | 15.0% | *None · Valid grounded answer or correct refusal* | `tr-20261027-0333` |
| **Total** | **All Audited Production Traces** | **20** | **100.0%** | **Overall Failure Rate: 85.0% (17/20)** | — |

---

### Priority Fix Target for Next Week (Week 6)
**Mode 1: Cross-Regional Policy Leakage (20.0%)**  
*Intervention:* Enforce strict retrieval metadata pre-filtering on the employee's authenticated jurisdiction (`filter={"region": employee.region}`).  
*Predicted Outcome:* Reduces Mode 1 frequency from **20.0% to 0.0%** with zero reduction in region-matched recall.
