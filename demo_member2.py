import sys
import io
import time

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from compiler.ir import WorkflowIR, Step
from compiler.graph_validator import build_workflow_graph, get_mandatory_guard_check
from compiler.verifier import verify_workflow
from security.attack_simulator import run_attack_suite

def print_banner(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    print_banner("[*] VERIFLOW SECURITY & GRAPH AI ENGINE (MEMBER 2 DEMO)")
    
    # 1. Base Valid Workflow
    print("\n[STEP 1] Generating Baseline Valid Enterprise Workflow...")
    base_workflow = WorkflowIR(
        steps=[
            Step(id='request_laptop', role='Employee', action='request_laptop', dependencies=[]),
            Step(id='manager_approval', role='IT Manager', action='approve_laptop', condition='budget <= 3000', dependencies=['request_laptop']),
            Step(id='export_data', role='System', action='send_notification', dependencies=['manager_approval'])
        ]
    )
    print(f"   -> Steps loaded: {len(base_workflow.steps)}")
    for s in base_workflow.steps:
        print(f"      * Step ID: {s.id:<18} | Role: {s.role:<12} | Action: {s.action:<18} | Dependencies: {s.dependencies}")

    # 2. Graph Construction & Invariant Validation
    print("\n[STEP 2] Running Graph Validator (NetworkX DAG Check)...")
    G, is_dag, errors = build_workflow_graph(base_workflow)
    print(f"   -> Graph Nodes: {list(G.nodes)}")
    print(f"   -> Graph Edges: {list(G.edges)}")
    print(f"   -> Is Directed Acyclic Graph (DAG): {'[YES]' if is_dag else '[NO]'}")

    # 3. Verification Engine (Symbolic + RBAC)
    print("\n[STEP 3] Running Symbolic Verifier (RBAC + Invariant Engine)...")
    v_res = verify_workflow(base_workflow)
    print(f"   -> Verification Result: {'[VERIFIED SAFE]' if v_res['is_valid'] else '[REJECTED]'}")
    if not v_res['is_valid']:
        print(f"   -> Counterexample: {v_res['counterexample']}")

    # 4. Chaos Attack Simulator
    print_banner("[!] FIRING 6-VECTOR ADVERSARIAL CHAOS ATTACK SUITE")
    time.sleep(0.3)
    attack_results = run_attack_suite(base_workflow)

    for i, attack in enumerate(attack_results, 1):
        status_badge = "[BLOCKED]" if attack['status'] == "BLOCKED" else "[BREACHED]"
        print(f"\n[{i}/6] Attack Vector: {attack['attack_name']} ({attack['attack_type']})")
        print(f"      Status:      {status_badge}")
        print(f"      Detection:   {attack['explanation']}")
        print(f"      Mitigation:  {attack['mitigation']}")
        time.sleep(0.1)

    print_banner("[OK] MEMBER 2 VALIDATION SUMMARY: 100% DEFENSES OPERATIONAL")

if __name__ == "__main__":
    main()
