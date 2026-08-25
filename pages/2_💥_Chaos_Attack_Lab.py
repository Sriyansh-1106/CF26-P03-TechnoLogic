# pages/2_💥_Chaos_Attack_Lab.py
"""
VeriFlow • Adversarial Chaos Attack Laboratory
Mutation testing attacking the compiled workflow AST/IR across 6 vectors.
"""
import streamlit as st
import json
from compiler.parser import parse_policy
from security.attack_simulator import run_attack_suite

st.set_page_config(page_title="VeriFlow • Chaos Attack Lab", page_icon="💥", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
    .atk-box { background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid #10b981; border-radius: 10px; padding: 1rem; margin-bottom: 0.75rem; }
    .atk-box.breached { border-left-color: #e11d48; }
</style>
""", unsafe_allow_html=True)

st.title("💥 Adversarial Chaos Attack Laboratory")
st.caption("VeriFlow aggressively attacks its own compiled AST/IR with chaos mutations before allowing execution.")

policy_sample = st.text_input(
    "Target Policy for Chaos Mutation:",
    value="Employee submits purchase request for laptop ($2,500). IT Manager approves laptop order ($2,500 <= $3,000 budget limit). Finance Director issues purchase order."
)

if st.button("🔥 Run 6-Vector Chaos Attack Gauntlet", type="primary"):
    wf = parse_policy(policy_sample)
    attacks = run_attack_suite(wf)
    
    st.markdown("### 🛡️ Real-Time Attack Defense Matrix")
    c1, c2 = st.columns(2)
    
    for idx, atk in enumerate(attacks):
        col = c1 if idx % 2 == 0 else c2
        with col:
            is_blocked = atk.get("status") == "BLOCKED"
            css_class = "atk-box" if is_blocked else "atk-box breached"
            icon = "🟢" if is_blocked else "🔴"
            
            st.markdown(f"""
            <div class="{css_class}">
                <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">
                    {icon} {atk.get('attack_name', 'Attack')}
                </div>
                <div style="font-size:0.8rem; color:#64748b; margin:0.2rem 0;">Vector: <code>{atk.get('attack_type', 'Mutation')}</code> | Defense Status: <b style="color:{'#059669' if is_blocked else '#dc2626'};">{atk.get('status', 'BLOCKED')}</b></div>
                <div style="font-size:0.85rem; color:#334155; margin-top:0.4rem;"><b>Target Outcome:</b> {atk.get('explanation', '')}</div>
                <div style="font-size:0.8rem; color:#059669; font-weight:600; margin-top:0.25rem;"><b>Defense Invariant:</b> {atk.get('mitigation', 'Graph Invariant Enforcement')}</div>
            </div>
            """, unsafe_allow_html=True)
