# tests/test_executor.py
import json
import os
import pytest
from compiler.ir import WorkflowIR, StepNode
from executor.engine import execute_workflow
from executor.proof import generate_proof_certificate

@pytest.fixture
def sample_valid_workflow():
    return WorkflowIR(
        workflow_id="WF-TEST-001",
        title="Test Procurement Workflow",
        trigger="New Request",
        roles_allowed=["Employee", "IT_Manager", "Finance_Director"],
        steps=[
            StepNode(
                id="STEP-1",
                action="Submit Request",
                role="Employee",
                condition="Budget <= 3000 USD",
                is_required=True,
                dependencies=[]
            ),
            StepNode(
                id="STEP-2",
                action="Approve Request",
                role="IT_Manager",
                condition="Approved",
                is_required=True,
                dependencies=["STEP-1"]
            )
        ]
    )

def test_execute_workflow_success(sample_valid_workflow):
    logs = execute_workflow(sample_valid_workflow)
    assert isinstance(logs, list)
    assert len(logs) == 2
    
    # Check log entry structure
    log1 = logs[0]
    assert log1["step_id"] == "STEP-1"
    assert log1["action"] == "Submit Request"
    assert log1["role"] == "Employee"
    assert log1["status"] == "SUCCESS"
    assert "timestamp" in log1

    log2 = logs[1]
    assert log2["step_id"] == "STEP-2"
    assert log2["status"] == "SUCCESS"

def test_generate_proof_certificate(sample_valid_workflow):
    verification_report = {
        "is_valid": True,
        "counterexample": None,
        "graph_data": {
            "nodes": ["STEP-1", "STEP-2"],
            "edges": [["STEP-1", "STEP-2"]]
        },
        "errors": []
    }
    
    cert = generate_proof_certificate(sample_valid_workflow, verification_report)
    
    assert isinstance(cert, dict)
    assert cert["certificate_id"].startswith("CERT-")
    assert cert["workflow_id"] == "WF-TEST-001"
    assert len(cert["sha256_signature"]) == 64
    assert cert["status"] == "VERIFIED_AND_ATTACK_TESTED"
    assert "verified_at" in cert

def test_policy_preset_files():
    policies_dir = os.path.join(os.path.dirname(__file__), "..", "policies")
    expected_files = [
        "valid_procurement.json",
        "ambiguous_expense.json",
        "unauthorized_access.json",
        "cyclic_approval.json"
    ]
    for filename in expected_files:
        filepath = os.path.join(policies_dir, filename)
        assert os.path.exists(filepath), f"Missing preset policy file: {filename}"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "workflow_id" in data
            assert "steps" in data
