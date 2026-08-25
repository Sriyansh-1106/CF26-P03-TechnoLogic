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

    # Find approval step and key endpoints dynamically
    approval_step = next(
        (s for s in workflow.steps if "approve" in s.action.lower() or "approval" in s.action.lower()),
        workflow.steps[1] if len(workflow.steps) > 1 else workflow.steps[0]
    )
    first_step = workflow.steps[0]
    last_step = workflow.steps[-1]

    # Attack 1: Bypass Approval (Remove approval step from dependencies)
    attack_1_wf = mutate_bypass_step(workflow, approval_step.id)
    res1 = verify_workflow(attack_1_wf)
    status1 = "BLOCKED" if not res1['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Bypass Approval", "Graph Validation", status1, res1.get('counterexample')))
    
    # Attack 2: Role Escalation (Intern -> Manager/Director)
    attack_2_wf = mutate_role(workflow, approval_step.id, 'Intern')
    res2 = verify_workflow(attack_2_wf)
    status2 = "BLOCKED" if not res2['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Role Escalation", "RBAC Override", status2, res2.get('counterexample')))

    # Attack 3: Step Pruning (Delete all critical approval/verification steps)
    attack_3_wf = workflow
    for g in [s.id for s in workflow.steps if "approve" in s.action.lower() or "approval" in s.action.lower()]:
        attack_3_wf = mutate_remove_step(attack_3_wf, g)
    res3 = verify_workflow(attack_3_wf)
    status3 = "BLOCKED" if not res3['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Step Pruning", "Graph Validation", status3, res3.get('counterexample')))
    
    # Attack 4: Threshold Tampering (Exceed limit)
    attack_4_wf = mutate_condition(workflow, approval_step.id, 'amount <= 50000')
    res4 = verify_workflow(attack_4_wf)
    status4 = "BLOCKED" if not res4['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Threshold Tampering", "Invariant Check", status4, res4.get('counterexample')))
    
    # Attack 5: Cycle Injection (Feed backward edge to create loop)
    attack_5_wf = mutate_inject_cycle(workflow, first_step.id, approval_step.id)
    res5 = verify_workflow(attack_5_wf)
    status5 = "BLOCKED" if not res5['is_valid'] else "BREACHED"
    results.append(_build_attack_res("Cycle Injection", "Graph Poisoning", status5, res5.get('counterexample')))

    # Attack 6: Unauthorized Data Exfiltration
    attack_6_wf = mutate_role(workflow, last_step.id, 'Intern')
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
