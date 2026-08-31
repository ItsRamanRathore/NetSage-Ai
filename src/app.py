import streamlit as st
import pandas as pd
import json
import sys
import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import NetSageEngine

st.set_page_config(page_title="NetSage AI Dashboard", layout="wide")
st.title("NetSage AI: Automated Network Diagnostic Platform")

@st.cache_data
def load_cases():
    try:
        return pd.read_csv(os.path.join(BASE_DIR, "data", "cases.csv"))
    except FileNotFoundError:
        return pd.DataFrame()

def log_review(case_id, decision, ai_diagnosis):
    log_path = os.path.join(BASE_DIR, "data", "review_log.jsonl")
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "case_id": case_id,
        "decision": decision,
        "ai_diagnosis": ai_diagnosis
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

cases_df = load_cases()

tab1, tab2 = st.tabs(["Diagnostic Tool", "Dashboard Summary"])

with tab1:
    if not cases_df.empty:
        case_ids = cases_df['case_id'].tolist()
        selected_case = st.selectbox("Select Scenario ID", case_ids, key="case_selector")
        
        case_data = cases_df[cases_df['case_id'] == selected_case].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Scenario Context")
            st.markdown(f"**Symptom:** {case_data['symptom']}")
            st.markdown(f"**Topology Note:** {case_data['topology_note']}")
            st.markdown(f"**Severity:** {case_data['severity']}")
            
            st.subheader("Captured Show Outputs")
            st.code(case_data['show_outputs'], language="text")
            
        with col2:
            st.subheader("AI Diagnosis")
            
            if st.button("Run Diagnostic Engine"):
                with st.spinner("Analyzing with NetSage AI..."):
                    engine = NetSageEngine()
                    results = engine.run_diagnosis(
                        case_data['symptom'],
                        case_data['topology_note'],
                        case_data['show_outputs']
                    )
                    st.session_state['results'] = results
                    st.session_state['current_case'] = selected_case
                    
            if 'results' in st.session_state and st.session_state.get('current_case') == selected_case:
                res = st.session_state['results']
                
                st.markdown("### Deterministic Checker")
                if res['checker_results']['status'] == "ERRORS_DETECTED":
                    st.error("Errors detected by deterministic rules!")
                    st.json(res['checker_results']['errors'])
                else:
                    st.success("No deterministic errors found.")
                    
                st.markdown("### AI Root Cause Analysis")
                ai = res['ai_diagnosis']
                if 'error' in ai:
                    st.error(ai['error'])
                else:
                    st.info(f"**Root Cause:** {ai.get('root_cause')}\n\n**Confidence:** {ai.get('confidence')}\n\n**OSI Layer:** {ai.get('osi_layer')}")
                    st.markdown(f"**Evidence:** {ai.get('evidence')}")
                    st.markdown(f"**Next Command:** `{ai.get('next_command')}`")
                    
                    st.markdown("### Proposed Remediation")
                    fix_steps = "\n".join(ai.get('fix_steps', []))
                    edited_steps = st.text_area("Edit CLI Commands", value=fix_steps, height=150)
                    
                    st.markdown("### Operator Decision Gate")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("Approve & Deploy Fix"):
                            log_review(selected_case, "Approve", ai)
                            st.success("Fix Approved and Logged!")
                    with c2:
                        if st.button("Edit & Deploy"):
                            log_review(selected_case, "Edit", ai)
                            st.success("Edited Fix Approved and Logged!")
                    with c3:
                        if st.button("Reject / Flag False Positive"):
                            log_review(selected_case, "Reject", ai)
                            st.warning("Diagnosis rejected and flagged in Audit Log.")
    else:
        st.info("No cases available. Generate data/cases.csv to begin.")

with tab2:
    st.header("Diagnostic Dashboard Summary")
    
    if not cases_df.empty:
        st.subheader("Dataset Composition")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Cases by Severity**")
            st.bar_chart(cases_df['severity'].value_counts())
        with colB:
            st.markdown("**Cases by Issue Concept**")
            st.bar_chart(cases_df['concept_tag'].value_counts())
            
    st.subheader("Human-in-the-Loop Agreement Rate")
    log_path = os.path.join(BASE_DIR, "data", "review_log.jsonl")
    if os.path.exists(log_path):
        logs = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))
        
        if logs:
            df_logs = pd.DataFrame(logs)
            decisions = df_logs['decision'].value_counts()
            total = len(df_logs)
            agreed = decisions.get("Approve", 0)
            rate = (agreed / total) * 100
            
            st.metric("Overall AI Agreement Rate", f"{rate:.1f}%", f"{agreed} out of {total} cases approved without edits")
            st.bar_chart(decisions)
            
            st.markdown("### Recent Reviews")
            st.dataframe(df_logs[['timestamp', 'case_id', 'decision']].sort_values(by="timestamp", ascending=False).head(10))
        else:
            st.info("No reviews logged yet.")
    else:
        st.info("Review log file does not exist yet. Run some diagnoses and submit decisions.")
