# pages/5_🎓_Architecture_&_USPs.py
"""
VeriFlow • Neurosymbolic Architecture & Case Studies
Explains the mathematical theory, member roles, and real-world impact.
"""
import streamlit as st

st.set_page_config(page_title="VeriFlow • Architecture & USPs", page_icon="🎓", layout="wide")

st.title("🎓 Neurosymbolic AI Architecture & Core USPs")
st.caption("How VeriFlow bridges neural language parsing with symbolic formal verification.")

c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    ### 🔬 3-Layer Neurosymbolic Stack
    1. **Neural Layer (Member 1)**:
       - Multi-tier LLM parsing with offline fixture fallback.
       - Regex-based Semantic Ambiguity Firewall.
    2. **Symbolic Layer (Member 2)**:
       - NetworkX Directed Acyclic Graph invariant checking (Acyclicity, Reachability Cut-Sets).
       - RBAC Permissions Matrix evaluation.
       - 6-Vector Adversarial Chaos Mutation Gauntlet.
    3. **Deterministic Layer (Member 3)**:
       - Sandboxed Step State Machine Runner.
       - SHA-256 Cryptographic Proof Certificate generation.
    """)

with c2:
    st.markdown("""
    ### 💡 Problem Statement Solved
    Enterprise automations powered purely by LLMs suffer from:
    - **Adjective Ambiguity**: "Order powerful laptop quickly" $\to$ LLM orders a $5,000 gaming rig without approval.
    - **Privilege Escalation**: Interns bypass manager sign-offs to expedite execution.
    - **Graph Deadlocks**: Circular inter-departmental approval loops.

    **VeriFlow eliminates all three by enforcing zero-trust mathematical invariants before any code runs.**
    """)
