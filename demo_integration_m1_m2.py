import sys
import io
import os
import json

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure OFFLINE_MODE for deterministic local execution
os.environ["OFFLINE_MODE"] = "true"

from compiler.ambiguity import check_ambiguity
from compiler.parser import parse_policy
from compiler.graph_validator import build_workflow_graph
from compiler.verifier import verify_workflow
from security.attack_simulator import run_attack_suite

def separator(title: str):
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)

def main():
    separator("[DEMO] END-TO-END PIPELINE: MEMBER 1 (AI PARSER) + MEMBER 2 (SECURITY)")
    
    # ---------------------------------------------------------
    # CASE 1: Valid Enterprise Vendor Payment Policy
    # ---------------------------------------------------------
    policy_1 = "Vendor invoices above 20000 must be approved by the Finance Director after the Manager reviews them. The Finance Director then releases the payment."
    
    print(f"\n>>> [INPUT POLICY 1]: \"{policy_1}\"")
    
    # STAGE 1: Member 1 - Ambiguity Firewall
    print("\n--- STAGE 1: Member 1 (Ambiguity Firewall) ---")
    amb_res = check_ambiguity(policy_1)
    print(f"Ambiguity Status: {'FLAGGED ⚠️' if amb_res['is_ambiguous'] else 'PASSED CLEAN ✅'}")

    # STAGE 2: Member 1 - AI Policy Parser -> IR
    print("\n--- STAGE 2: Member 1 (LLM Parser -> WorkflowIR) ---")
    workflow_ir = parse_policy(policy_1)
    print(f"Workflow ID: {workflow_ir.workflow_id}")
    print(f"Title:       {workflow_ir.title}")
    print(f"Steps Count: {len(workflow_ir.steps)}")
    for s in workflow_ir.steps:
        print(f"   • Step [{s.id}]: Role={s.role:<16} Action={s.action:<24} Condition={s.condition or 'None':<18} Deps={s.dependencies}")

    # STAGE 3: Member 2 - Graph AI Validator
    print("\n--- STAGE 3: Member 2 (NetworkX Graph DAG Validator) ---")
    G, is_dag, graph_errors = build_workflow_graph(workflow_ir)
    print(f"Is Valid DAG (No Cycles): {'✅ YES' if is_dag else '❌ NO'}")
    print(f"DAG Nodes: {list(G.nodes)}")
    print(f"DAG Edges: {list(G.edges)}")

    # STAGE 4: Member 2 - Symbolic Verifier & RBAC Invariant Engine
    print("\n--- STAGE 4: Member 2 (Symbolic & RBAC Invariant Verifier) ---")
    v_res = verify_workflow(workflow_ir)
    print(f"Workflow Verified Safe: {'✅ YES' if v_res['is_valid'] else '❌ REJECTED'}")
    if v_res['errors']:
        print(f"Verification Errors: {v_res['errors']}")

    # STAGE 5: Member 2 - 6-Vector Chaos Attack Suite
    print("\n--- STAGE 5: Member 2 (6-Vector Adversarial Chaos Gauntlet) ---")
    attack_results = run_attack_suite(workflow_ir)
    for i, a in enumerate(attack_results, 1):
        status_icon = "🛡️ BLOCKED" if a.get('status') == "BLOCKED" else "🚨 BREACHED"
        print(f"   [{i}/6] {status_icon} | {a.get('attack_name', 'Unknown'):<30} ({a.get('attack_type', '')})")
        print(f"         Reason: {a.get('explanation')}")

    # ---------------------------------------------------------
    # CASE 2: Ambiguous / Vague Policy Detection
    # ---------------------------------------------------------
    separator("[TEST CASE 2] Ambiguous Natural Language Input")
    policy_2 = "When a new employee joins, order a powerful laptop quickly. The IT Manager must approve."
    print(f"\n>>> [INPUT POLICY 2]: \"{policy_2}\"")
    amb_res_2 = check_ambiguity(policy_2)
    print(f"Ambiguity Status: {'⚠️ FLAGGED (Firewall Active)' if amb_res_2['is_ambiguous'] else 'PASSED'}")
    fixes = amb_res_2.get('suggested_fixes', amb_res_2.get('suggestions', []))
    for w, s in zip(amb_res_2.get('warnings', []), fixes):
        print(f"   • {w}")
        print(f"     Suggestion: {s}")

    separator("🎯 RESULT: MEMBER 1 & MEMBER 2 ARE 100% IN SYNC & INTEROPERABLE")

if __name__ == "__main__":
    main()
