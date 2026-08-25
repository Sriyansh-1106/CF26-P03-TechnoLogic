import pytest
from compiler.ir import WorkflowIR, Step
from compiler.verifier import verify_workflow
from security.attack_simulator import run_attack_suite

def create_valid_workflow():
    return WorkflowIR(
        steps=[
            Step(id='request_laptop', role='Employee', action='request_laptop', dependencies=[]),
            Step(id='manager_approval', role='IT Manager', action='approve_laptop', dependencies=['request_laptop']),
            Step(id='export_data', role='System', action='send_notification', dependencies=['manager_approval'])
        ]
    )

def test_valid_workflow():
    wf = create_valid_workflow()
    res = verify_workflow(wf)
    assert res['is_valid'] is True, f"Expected valid, got: {res['errors']}"

def test_attacks_are_blocked():
    wf = create_valid_workflow()
    attack_results = run_attack_suite(wf)
    
    assert len(attack_results) > 0, "No attacks ran"
    for res in attack_results:
        assert res['status'] == 'BLOCKED', f"Attack {res['attack_name']} was not blocked!"
        assert "FAILED" in res['explanation']
