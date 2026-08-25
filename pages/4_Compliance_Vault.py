# pages/4_Compliance_Vault.py
"""
VeriFlow • Cryptographic Compliance Vault
Immutable SHA-256 verification receipts and audit ledger.
"""
import streamlit as st
import json
import time
from compiler.parser import parse_policy
from compiler.verifier import verify_workflow
from executor.proof import generate_proof_certificate

st.set_page_config(page_title="VeriFlow • Compliance Vault", page_icon="📜", layout="wide")

st.title("📜 Cryptographic Compliance Vault")
st.caption("Immutable SHA-256 verification receipts proving workflow safety prior to execution.")

sample_policy = "Employee submits purchase request for laptop ($2,500). IT Manager approves laptop order ($2,500 <= $3,000 budget limit). Finance Director issues purchase order."
wf = parse_policy(sample_policy)
ver = verify_workflow(wf)
cert = generate_proof_certificate(wf, ver)

c1, c2 = st.columns([1.2, 1])

with c1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%); border-radius: 12px; padding: 1.5rem; color: #ffffff;">
        <h3 style="margin-top:0; color:#ffffff;">🔒 Formal Verification Certificate</h3>
        <p style="color:#e0e7ff; font-size:0.9rem;">Proof-carrying code certificate ensuring zero-trust workflow validation.</p>
        <hr style="border-color: rgba(255,255,255,0.2);">
        <div><b>Certificate ID:</b> <code>{cert['certificate_id']}</code></div>
        <div><b>Workflow ID:</b> <code>{cert['workflow_id']}</code></div>
        <div><b>SHA-256 Signature:</b> <code style="word-break: break-all;">{cert['sha256_signature']}</code></div>
        <div><b>Timestamp:</b> <code>{cert['verified_at']}</code></div>
        <div><b>Compliance Status:</b> <span style="color:#a7f3d0; font-weight:700;">{cert['status']}</span></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.subheader("📥 Export Audit Package")
    audit_bundle = {
        "certificate": cert,
        "workflow_ir": wf.to_dict(),
        "verification_outcome": ver
    }
    st.download_button(
        label="Download Full Audit Bundle (.json)",
        data=json.dumps(audit_bundle, indent=2),
        file_name=f"VeriFlow_Audit_{cert['certificate_id']}.json",
        mime="application/json"
    )
