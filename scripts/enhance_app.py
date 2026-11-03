import re
from pathlib import Path

app_path = Path("app.py")
content = app_path.read_text(encoding="utf-8")

# 1. Add imports
import_addition = """from src.error_analysis import (
    DEFAULT_SEED,
    OPEN_CODING_RECORDS,
    TAXONOMY_ROWS,
    load_all_traces,
    load_demo_traces,
    replay_single_trace,
)
"""

if "src.error_analysis" not in content:
    content = content.replace(
        "from src.hybrid_search import (",
        import_addition + "from src.hybrid_search import ("
    )

# 2. Update page title
content = content.replace(
    'st.set_page_config(page_title="HR Policy RAG — Week 4 Debugging & Hybrid Search", page_icon="📘", layout="wide")',
    'st.set_page_config(page_title="HR Policy RAG — Error Analysis & Trace Inspection", page_icon="📘", layout="wide")'
)

content = content.replace(
    'st.title("HR Policy RAG — Debugging Retrieval & Hybrid Search")',
    'st.title("HR Policy RAG — Error Analysis & Trace Inspection")'
)

content = content.replace(
    'st.caption("Module 2 (Week 4): Hybrid Search (BM25 + RRF), Reranking & Failure Separation (Track C: HR Policy)")',
    'st.caption("Module 3 (Week 5): Reading Traces Like a Professional · Ranked Taxonomy & Replay (Track C: HR Policy)")'
)

# 3. Update tabs list
old_tabs = """    tab_search, tab_inspect, tab_benchmark = st.tabs([
        "🔍 Policy Search",
        "🔬 Inspection View (Failure Separation)",
        "📊 Week 4 Benchmark & Buyback",
    ])"""

new_tabs = """    tab_search, tab_inspect, tab_benchmark, tab_taxonomy, tab_replay = st.tabs([
        "🔍 Policy Search",
        "🔬 Inspection View (Failure Separation)",
        "📊 Week 4 Benchmark & Buyback",
        "🏷️ Week 5 Error Taxonomy",
        "🔁 Trace Replayer & Audit",
    ])"""

content = content.replace(old_tabs, new_tabs)

# 4. Add Tab 4 and Tab 5 content right before def main()
tab4_and_5_code = '''
    # ---------------- TAB 4: Week 5 Error Taxonomy ----------------
    with tab_taxonomy:
        st.subheader("Week 5 Practical: Error Taxonomy & Ranked Failure Modes")
        st.caption("20 Production Traces Sampled from 1,048 Weekly Logs · Seed: `20261103` · Domain: HR Policy")

        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        with col_t1:
            st.metric("Weekly Production Logs", "1,048 Traces")
        with col_t2:
            st.metric("Audited Sample", "20 Traces", "Seed: 20261103")
        with col_t3:
            st.metric("Production Failure Rate", "85.0%", "17/20 Traces Failed")
        with col_t4:
            st.metric("Top Failure Mode", "20.0%", "Cross-Regional Leakage")

        st.markdown("---")
        st.subheader("1. Ranked Error Taxonomy")
        st.dataframe(TAXONOMY_ROWS, use_container_width=True)

        st.markdown("---")
        st.subheader("2. Verbatim Open-Coding Notes (All 20 Traces)")
        st.caption("Honest observational descriptions recorded during trace reading (zero fixes applied during coding).")
        
        mode_filter = st.selectbox(
            "Filter by Failure Mode:",
            ["All Modes"] + list({r["failure_mode"] for r in OPEN_CODING_RECORDS})
        )
        
        display_records = [
            r for r in OPEN_CODING_RECORDS
            if mode_filter == "All Modes" or r["failure_mode"] == mode_filter
        ]
        
        for r in display_records:
            with st.container(border=True):
                c1, c2 = st.columns([1, 2.5])
                with c1:
                    st.markdown(f"**Sample #{r['sample_num']:02d}** · `{r['trace_id']}`")
                    st.caption(f"**Index:** {r['index']} in `traces.jsonl`")
                    if "Compliant" in r["failure_mode"]:
                        st.success(f"🟢 {r['failure_mode']}")
                    else:
                        st.error(f"🔴 {r['failure_mode']}")
                    st.caption(f"**Severity:** {r['severity']}")
                with c2:
                    st.markdown(f"**User Query:** *{r['query']}*")
                    st.markdown(f"**Assistant Output:** `{r['raw_output']}`")
                    st.info(f"👁️ **Observation:** {r['observation']}")

        st.markdown("---")
        st.subheader("3. Bonus Challenge: Curated Demo Set vs. Random Sample")
        st.markdown(
            "Comparison of failure frequencies between the **20 Random Production Traces** "
            "and the **10 Curated Demo Questions** shown at People Ops sprint reviews."
        )

        bcol1, bcol2, bcol3 = st.columns(3)
        with bcol1:
            st.metric("Random Production Sample (N=20)", "20.0%", "Mode 1: Cross-Regional")
        with bcol2:
            st.metric("Curated Demo Set (N=10)", "0.0%", "Mode 1: Cross-Regional")
        with bcol3:
            st.metric("Demo Set Illusion Delta", "+20.0%", "Production Failure Gap")

        st.warning(
            "**The Demo Set Mirage (What our team told itself for a month):**\\n\\n"
            "For the past four weeks, our team congratulated itself on a 100% demo pass rate during weekly People Ops reviews. "
            "However, those 10 review questions were hand-crafted during initial build to fit document phrasing, avoided regional conflicts, "
            "and asked only about known sabbatical/bereavement terms that hit hardcoded refusal paths. In production, real employees asked "
            "messy cross-regional and tenure-bracket questions that triggered an 85% failure rate. Curated demos measure question writing, not app robustness."
        )

        st.markdown("---")
        st.subheader("4. Dated Falsifiable Prediction (Committed to Git)")
        st.info(
            "**Committed Date:** 2026-11-03 | **Git Commit Hash:** `2125d6a163eebe94751c106a3d006dc7a3c7f4d1` (Short: `2125d6a`)\\n\\n"
            "**Target Attack Mode (Week 6):** Cross-Regional Policy Leakage (currently 20.0% / 4 of 20 traces).\\n\\n"
            "**Specific Code Change:** Enforce strict retrieval metadata pre-filtering on the authenticated employee's regional profile (`filter={'region': employee.region}`).\\n\\n"
            "**Falsifiable Quantitative Prediction:** *'Enforcing strict regional metadata filtering will drop Cross-Regional Policy Leakage from 20.0% (4/20) to 0.0% (0/20) in the next random 20-trace audit, while maintaining hit-rate@3 above 85.0% on valid regional inquiries.'*"
        )

        st.markdown("---")
        st.subheader("5. Why Public Benchmarks Missed These Failures")
        st.markdown(
            """
            1. **Jurisdictional Hierarchies:** Public benchmarks (MMLU, GSM8K, RAGBench) evaluate open-domain reading comprehension where regional legal authority boundaries (APAC vs. EMEA vs. AMER) do not exist.
            2. **Table Parsing Dynamics:** Synthetic benchmarks score prose retrieval; they do not test row-binding confusion where the retriever successfully fetches an eligibility table chunk (`HR-207 §2`) but the generator misattributes tenure numbers across adjacent rows.
            3. **Negative Constraint Evaluation:** Benchmark scoring rewards fluent, plausible answers rather than refusal compliance, giving high marks to a model that invents a polite 3-day bereavement policy instead of penalizing the corporate liability created.
            """
        )

    # ---------------- TAB 5: Trace Replayer & Audit ----------------
    with tab_replay:
        st.subheader("Trace Replayer & Redaction Audit Tool")
        st.markdown(
            "Prove your traces are replayable from trace data alone. Pick any trace by ID or seed, "
            "replay it, and inspect original vs replayed output side-by-side."
        )

        all_traces = load_all_traces()
        trace_ids = [t["trace_id"] for t in all_traces] if all_traces else ["tr-20261026-0184"]

        rcol1, rcol2 = st.columns([2, 1])
        with rcol1:
            selected_trace_id = st.selectbox("Select Trace to Replay:", trace_ids, index=0)
        with rcol2:
            st.write("")
            st.write("")
            replay_btn = st.button("🔁 Replay Trace from Trace Alone", type="primary")

        target_trace = next((t for t in all_traces if t["trace_id"] == selected_trace_id), None)
        if target_trace:
            rep_res = replay_single_trace(target_trace)

            st.markdown("#### Trace Metadata Completeness Audit")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.write(f"**Prompt Version:** `{rep_res['prompt_version']}`")
            with m2:
                st.write(f"**Model:** `{rep_res['model']}`")
            with m3:
                st.write(f"**Parameters:** `temp: {rep_res['model_params'].get('temperature', 0.0)}`")
            with m4:
                pii_status = "✅ REDACTED BEFORE WRITE" if rep_res["pii_redacted_before_write"] else "❌ PII EXPOSED"
                st.write(f"**PII Status:** {pii_status}")

            st.markdown("#### Retrieved Chunks & Scores Recorded in Trace")
            for idx, c in enumerate(rep_res["retrieved_chunks"], start=1):
                st.caption(f"`{idx}.` **{c.get('chunk_id')}** ({c.get('policy_id')} §{c.get('section')}) · Region: `{c.get('region')}` · Score: `{c.get('score')}`")

            st.markdown("---")
            st.subheader("Original Output vs. Replayed Output")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown("**Original Logged Output:**")
                st.info(rep_res["original_output"])
            with sc2:
                st.markdown("**Replayed Output (Reconstructed from trace alone):**")
                st.success(rep_res["replayed_output"])

            if rep_res["is_match"]:
                st.success("🎯 **Deterministic Replay Verified:** 100% Exact token parity between original and replayed output.")
            else:
                st.error("⚠️ Output mismatch detected.")
'''

content = content.replace("def main() -> None:", tab4_and_5_code + "\n\ndef main() -> None:")

app_path.write_text(content, encoding="utf-8")
print("Successfully enhanced app.py with Week 5 tabs and error analysis tools!")
