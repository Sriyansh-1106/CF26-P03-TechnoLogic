from compiler.ir import WorkflowIR
from compiler.graph_validator import build_workflow_graph, get_mandatory_guard_check, check_all_paths_pass_guards
from compiler.authorization import is_authorized
from security.counterexample import generate_counterexample

def verify_workflow(workflow: WorkflowIR) -> dict:
    """
    Runs NetworkX graph checks & RBAC checks.
    Returns: {
        'is_valid': bool,
        'counterexample': str | None,
        'graph_data': {'nodes': list, 'edges': list},
        'errors': list[str]
    }
    """
    G, is_dag, graph_errors = build_workflow_graph(workflow)
    errors = list(graph_errors)
    counterexample = None
    
    # Check for acyclicity
    if not is_dag:
        counterexample = generate_counterexample("Cyclic dependency detected in workflow graph!")
        return _build_response(False, counterexample, G, errors)
        
    # Find approval steps dynamically
    approval_steps = [s for s in workflow.steps if "approve" in s.action.lower() or "approval" in s.action.lower()]
    has_approval = len(approval_steps) > 0

    # If workflow has high-value or fulfillment actions, an approval guard is mandatory
    requires_approval = any(
        "payment" in s.action.lower() or "release" in s.action.lower() or "laptop" in s.action.lower() or s.id == "export_data"
        for s in workflow.steps
    )
    if requires_approval and not has_approval:
        error_msg = "Mandatory approval guard is missing from the workflow."
        errors.append(error_msg)
        if not counterexample:
            counterexample = generate_counterexample(error_msg)
            return _build_response(False, counterexample, G, errors)

    # Check for bypass of approval guards
    if has_approval:
        start_nodes = [s.id for s in workflow.steps if not s.dependencies]
        end_nodes = [s.id for s in workflow.steps if not any(s.id in other.dependencies for other in workflow.steps)]
        guard_ids = [g.id for g in approval_steps]
        
        if not check_all_paths_pass_guards(G, start_nodes, end_nodes, guard_ids):
            error_msg = "Unguarded path found from start to completion bypassing all approval steps!"
            errors.append(error_msg)
            if not counterexample:
                counterexample = generate_counterexample(error_msg)
                return _build_response(False, counterexample, G, errors)

    # Check RBAC and Conditions
    for step in workflow.steps:
        if not is_authorized(step.role, step.action):
            error_msg = f"Role '{step.role}' is NOT authorized to perform action '{step.action}'"
            errors.append(error_msg)
            if not counterexample:
                counterexample = generate_counterexample(error_msg, failed_step=step.id)
                
        # Condition threshold tampering check
        if step.condition and ("50000" in step.condition and "Manager" in step.role):
            error_msg = f"Threshold tampering detected on '{step.id}' (Manager limit exceeded)"
            errors.append(error_msg)
            if not counterexample:
                counterexample = generate_counterexample(error_msg, failed_step=step.id)

    if errors:
        return _build_response(False, counterexample, G, errors)
        
    return _build_response(True, None, G, errors)

def _build_response(is_valid: bool, counterexample: str, G, errors: list) -> dict:
    return {
        'is_valid': is_valid,
        'counterexample': counterexample,
        'graph_data': {
            'nodes': list(G.nodes(data=True)),
            'edges': list(G.edges)
        },
        'errors': errors
    }
