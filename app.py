# app.py
"""
VeriFlow Enterprise Neurosymbolic Safety Compiler
Multi-Page Web Application Gateway
"""
import streamlit as st

st.set_page_config(
    page_title="VeriFlow • Enterprise Safety Compiler",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .hero-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 2.5rem;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    .portal-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <h1 style="font-size: 2.5rem; font-weight: 800; margin: 0; color: #ffffff;">
        🛡️ VeriFlow Enterprise Safety Compiler
    </h1>
    <p style="font-size: 1.15rem; color: #cbd5e1; margin-top: 0.5rem;">
        Zero-Trust Neurosymbolic Compiler • Natural Language Policy Parser • Graph Invariant Verifier • Synthetic AI Benchmarking
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 0.8rem;">
        <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; padding: 0.4rem 0.8rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem;">
            ● COMPILER ONLINE
        </span>
        <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid #6366f1; color: #a5b4fc; padding: 0.4rem 0.8rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem;">
            5 DEDICATED MODULES
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🧭 Explore Dedicated Application Modules")
st.caption("Use the left navigation sidebar or select a module below to begin:")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚡</div>
        <h3 style="margin: 0; color: #0f172a;">Compiler Studio</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;">
            Compile natural language business rules into verified Directed Acyclic Graphs with live sandbox execution.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Compiler Studio ⚡", use_container_width=True):
        st.switch_page("pages/1_⚡_Compiler_Studio.py")

with c2:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💥</div>
        <h3 style="margin: 0; color: #0f172a;">Chaos Attack Lab</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;">
            Subject compiled workflows to 6-vector adversarial mutations (role escalations, step prunings, cycles).
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Chaos Attack Lab 💥", use_container_width=True):
        st.switch_page("pages/2_💥_Chaos_Attack_Lab.py")

with c3:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
        <h3 style="margin: 0; color: #0f172a;">Synthetic AI Benchmark</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;">
            Generate 500+ enterprise training samples, export JSONL, and benchmark VeriFlow vs Raw LLMs.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Synthetic Benchmarks 🤖", use_container_width=True):
        st.switch_page("pages/3_🤖_Synthetic_Dataset_&_Benchmark.py")

st.write("")
c4, c5 = st.columns(2)

with c4:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📜</div>
        <h3 style="margin: 0; color: #0f172a;">Compliance Vault</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;">
            Inspect immutable SHA-256 formal verification receipts and export audit compliance bundles.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Compliance Vault 📜", use_container_width=True):
        st.switch_page("pages/4_📜_Compliance_Vault.py")

with c5:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎓</div>
        <h3 style="margin: 0; color: #0f172a;">Architecture & USPs</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;">
            Deep-dive into the neurosymbolic AI stack, formal methods, and 3-member team roles.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Architecture & USPs 🎓", use_container_width=True):
        st.switch_page("pages/5_🎓_Architecture_&_USPs.py")
