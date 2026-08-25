from compiler.ir import WorkflowIR
from compiler.verifier import verify_workflow
from security.mutation_testing import (
    mutate_role, 
    mutate_bypass_step,
    mutate_remove_step,
    mutate_condition,
    mutate_inject_cycle
)

def run_attack_suite(workflow: WorkflowIR) -> list[dict]:
    """
    Fires all 6 adversarial chaos attacks against the workflow.
    Returns list of attack results.
    """
    results = []
    
    # Baseline check: The original workflow must be valid.
    if not verify_workflow(workflow).get('is_valid', False):
        return [{"error": "Original workflow is invalid, cannot run attacks."}]

    # Attack 1: Bypass Approval (Remove 'manager_approval' from dependencies)
    attack_1_wf = mutate_bypass_step(workflow, 'manager_approval')
    res1 = verify_workflow(attack_1_wf)
    status1 = "BLOCKED" if not res1['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Bypass Approval", "Graph Validation", status1, res1.get('counterexample')))
    
    # Attack 2: Role Escalation (Intern -> CEO)
    # Mutating 'manager_approval' role to 'Intern'
    attack_2_wf = mutate_role(workflow, 'manager_approval', 'Intern')
    res2 = verify_workflow(attack_2_wf)
    status2 = "BLOCKED" if not res2['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Role Escalation", "RBAC Override", status2, res2.get('counterexample')))

    # Attack 3: Step Pruning (Skip vendor verification)
    # In our simple wf, we skip 'manager_approval' completely
    attack_3_wf = mutate_remove_step(workflow, 'manager_approval')
    res3 = verify_workflow(attack_3_wf)
    status3 = "BLOCKED" if not res3['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Step Pruning", "Graph Validation", status3, res3.get('counterexample')))
    
    # Attack 4: Threshold Tampering (50k -> 5k)
    # Mutating condition
    attack_4_wf = mutate_condition(workflow, 'manager_approval', 'budget < 50000')
    res4 = verify_workflow(attack_4_wf)
    status4 = "BLOCKED" if not res4['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Threshold Tampering", "Invariant Check", status4, res4.get('counterexample')))
    
    # Attack 5: Cycle Injection
    attack_5_wf = mutate_inject_cycle(workflow, 'request_laptop', 'manager_approval')
    res5 = verify_workflow(attack_5_wf)
    status5 = "BLOCKED" if not res5['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Cycle Injection", "Graph Poisoning", status5, res5.get('counterexample')))

    # Attack 6: Unauthorized Data Exfiltration
    attack_6_wf = mutate_role(workflow, 'export_data', 'Employee')
    res6 = verify_workflow(attack_6_wf)
    status6 = "BLOCKED" if not res6['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Unauthorized Data Exfiltration", "RBAC Override", status6, res6.get('counterexample')))

    return results

def _build_attack_res(name: str, type: str, status: str, explanation: str) -> dict:
    return {
        'attack_name': name,
        'attack_type': type,
        'status': status,
        'explanation': explanation or "Attack successful (Failed to block).",
        'mitigation': "Enforce strict RBAC and Graph invariants."
    }
