# executor/engine.py
"""
Deterministic Step State Machine Runner for VeriFlow.
Simulates step-by-step state machine execution and produces timestamped audit logs.
"""
import time
from typing import List, Dict, Any, Union
from compiler.ir import WorkflowIR, StepNode

def execute_workflow(workflow: Union[WorkflowIR, dict]) -> List[Dict[str, Any]]:
    """
    Simulates chronological step execution with timestamped audit logs.
    
    Args:
        workflow: WorkflowIR instance or dict representing the workflow.
        
    Returns:
        List of audit log dictionaries containing timestamp, node ID, action, role, and status.
    """
    if isinstance(workflow, dict):
        steps_raw = workflow.get("steps", [])
        steps = [
            StepNode(**s) if isinstance(s, dict) else s
            for s in steps_raw
        ]
        workflow_id = workflow.get("workflow_id", "WF-UNKNOWN")
    else:
        steps = workflow.steps
        workflow_id = workflow.workflow_id

    logs = []
    executed_steps = set()

    for step in steps:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Check dependency resolution
        missing_deps = [dep for dep in step.dependencies if dep not in executed_steps]
        
        if missing_deps:
            status = "BLOCKED"
            details = f"Blocked on step '{step.id}' ({step.action}): Missing unresolved dependencies: {', '.join(missing_deps)}"
        else:
            status = "SUCCESS"
            executed_steps.add(step.id)
            details = f"Executed step '{step.id}' ({step.action}) by role '{step.role}' under condition: {step.condition or 'None'}"

        log_entry = {
            "timestamp": now_str,
            "workflow_id": workflow_id,
            "step_id": step.id,
            "action": step.action,
            "role": step.role,
            "condition": step.condition,
            "status": status,
            "details": details
        }
        logs.append(log_entry)

    return logs
