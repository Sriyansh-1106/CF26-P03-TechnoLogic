# pages/1_Compiler_Studio.py
"""
VeriFlow • Live Policy Compiler Studio
Compile natural language policies into verified Directed Acyclic Graphs.
"""
import streamlit as st
import json
import graphviz
from compiler.ir import WorkflowIR, StepNode
from compiler.ambiguity import check_ambiguity
from compiler.verifier import verify_workflow
from executor.engine import execute_workflow
from executor.proof import generate_proof_certificate

st.set_page_config(page_title="VeriFlow • Compiler Studio", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
    .pass-banner { background: #ecfdf5; border-left: 5px solid #10b981; color: #065f46; padding: 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 1rem; }
    .fail-banner { background: #fff1f2; border-left: 5px solid #e11d48; color: #9f1239; padding: 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 1rem; }
    .warn-banner { background: #fffbeb; border-left: 5px solid #f59e0b; color: #92400e; padding: 1rem; border-radius: 8px; font-weight: 600; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ VeriFlow Policy Compiler Studio")
st.caption("Live natural language to verified Directed Acyclic Graph (DAG) compilation.")

PRESETS = {
    "🛒 Preset A: Valid Procurement": "Employee submits purchase request for laptop ($2,500). IT Manager approves laptop order ($2,500 <= $3,000 budget limit). Finance Director issues purchase order.",
    "⚠️ Preset B: Ambiguous Expense": "When a new employee joins, order a powerful laptop quickly. Expedite delivery soon.",
    "🚫 Preset C: Unauthorized Access": "Intern requests $50,000 high performance workstation. Intern self-approves the high-value purchase without Finance approval.",
    "🔄 Preset D: Cyclic Approval": "IT Manager Approval requires Finance Director Approval. Finance Director Approval requires IT Manager Approval."
}

col_in, col_graph = st.columns([1, 1.25])

with col_in:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Policy Prompt Input")
    
    preset_choice = st.selectbox("Select Quick Scenario:", list(PRESETS.keys()))
    
    if "studio_policy" not in st.session_state or st.session_state.get("last_preset") != preset_choice:
        st.session_state.studio_policy = PRESETS[preset_choice]
        st.session_state.last_preset = preset_choice
        
    user_text = st.text_area("Policy Text:", value=st.session_state.studio_policy, height=130)
    
    if st.button("🚀 Compile & Verify Workflow", type="primary", use_container_width=True):
        st.session_state.studio_policy = user_text
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Processing
from compiler.parser import parse_policy
current_ir = parse_policy(st.session_state.studio_policy)
amb_res = check_ambiguity(st.session_state.studio_policy)
ver_res = verify_workflow(current_ir)

with col_graph:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🕸️ Directed Workflow Graph (DAG)")
    
    if ver_res["is_valid"] and not amb_res["is_ambiguous"]:
        st.markdown('<div class="pass-banner">✅ VERIFICATION PASSED: Graph is acyclic and authorized.</div>', unsafe_allow_html=True)
    elif not ver_res["is_valid"]:
        st.markdown(f'<div class="fail-banner">❌ VERIFICATION FAILED: {ver_res.get("counterexample", "Invariant broken")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warn-banner">⚠️ AMBIGUITY BLOCKED: Policy contains vague terms.</div>', unsafe_allow_html=True)

    dot = graphviz.Digraph(comment="VeriFlow DAG")
    dot.attr(rankdir="LR", bgcolor="transparent")
    dot.attr('node', shape='rectangle', style='filled,rounded', fontname='Helvetica', penwidth='1.5')

    for step in current_ir.steps:
        fill = "#d1fae5" if ver_res["is_valid"] and not amb_res["is_ambiguous"] else ("#fef3c7" if amb_res["is_ambiguous"] else "#fecdd3")
        border = "#059669" if ver_res["is_valid"] and not amb_res["is_ambiguous"] else ("#d97706" if amb_res["is_ambiguous"] else "#e11d48")
        dot.node(step.id, f"{step.id}\n{step.action}\n[{step.role}]", fillcolor=fill, color=border)

    for step in current_ir.steps:
        for dep in step.dependencies:
            dot.edge(dep, step.id, color="#64748b", penwidth="1.8")

    st.graphviz_chart(dot, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Bottom Row: Execution and JSON
b1, b2 = st.columns([1, 1])
with b1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📜 Sandbox State Machine Runner")
    if ver_res["is_valid"] and not amb_res["is_ambiguous"]:
        logs = execute_workflow(current_ir)
        for log in logs:
            st.write(f"• **{log['step_id']}** (`{log['role']}`): {log['action']} — `[SUCCESS]`")
    else:
        st.error("Execution blocked by safety invariants.")
    st.markdown('</div>', unsafe_allow_html=True)

with b2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Compiled Intermediate Representation (IR)")
    st.json(current_ir.to_dict())
    st.markdown('</div>', unsafe_allow_html=True)
