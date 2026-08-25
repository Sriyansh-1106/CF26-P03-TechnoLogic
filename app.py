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
        padding: 2.2rem;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    .portal-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <h1 style="font-size: 2.3rem; font-weight: 800; margin: 0; color: #ffffff;">
        🛡️ VeriFlow Enterprise Safety Compiler
    </h1>
    <p style="font-size: 1.1rem; color: #cbd5e1; margin-top: 0.4rem;">
        Zero-Trust Neurosymbolic Compiler • Natural Language Policy Parser • Graph Invariant Verifier • Synthetic AI Benchmarking
    </p>
    <div style="margin-top: 0.8rem; display: flex; gap: 0.8rem;">
        <span style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; padding: 0.35rem 0.75rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem;">
            ● COMPILER LIVE
        </span>
        <span style="background: rgba(99, 102, 241, 0.2); border: 1px solid #6366f1; color: #a5b4fc; padding: 0.35rem 0.75rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem;">
            5 DEDICATED MODULES ACTIVE
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🧭 Dedicated Application Modules")
st.caption("Select a module below or use the left navigation sidebar:")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">⚡</div>
        <h3 style="margin: 0; color: #0f172a;">Compiler Studio</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">
            Compile natural language business rules into verified Directed Acyclic Graphs.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Compiler_Studio.py", label="Open Compiler Studio ⚡", icon="⚡", use_container_width=True)

with c2:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">💥</div>
        <h3 style="margin: 0; color: #0f172a;">Chaos Attack Lab</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">
            Subject compiled workflows to 6-vector adversarial mutations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Chaos_Attack_Lab.py", label="Open Chaos Attack Lab 💥", icon="💥", use_container_width=True)

with c3:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">🤖</div>
        <h3 style="margin: 0; color: #0f172a;">Synthetic Benchmark</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">
            Generate 500+ enterprise training samples and benchmark VeriFlow vs Raw LLMs.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Synthetic_Dataset.py", label="Open Synthetic Benchmarks 🤖", icon="🤖", use_container_width=True)

st.write("")
c4, c5 = st.columns(2)

with c4:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">📜</div>
        <h3 style="margin: 0; color: #0f172a;">Compliance Vault</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">
            Inspect immutable SHA-256 formal verification receipts and audit ledger.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Compliance_Vault.py", label="Open Compliance Vault 📜", icon="📜", use_container_width=True)

with c5:
    st.markdown("""
    <div class="portal-card">
        <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">🎓</div>
        <h3 style="margin: 0; color: #0f172a;">Architecture & USPs</h3>
        <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.25rem;">
            Deep-dive into the neurosymbolic AI stack, formal methods, and team assembly line.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_Architecture_USPs.py", label="Open Architecture & USPs 🎓", icon="🎓", use_container_width=True)
