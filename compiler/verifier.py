from compiler.ir import WorkflowIR
from compiler.graph_validator import build_workflow_graph, get_mandatory_guard_check
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
        
    # Check for mandatory step (manager_approval)
    has_manager_approval = any(s.id == 'manager_approval' for s in workflow.steps)
    if not has_manager_approval:
        error_msg = "Mandatory step 'manager_approval' is missing."
        errors.append(error_msg)
        if not counterexample:
            counterexample = generate_counterexample(error_msg)
            return _build_response(False, counterexample, G, errors)

    # Check for bypass (export_data must depend on manager_approval in some way)
    # Using our get_mandatory_guard_check
    if has_manager_approval and 'request_laptop' in G and 'export_data' in G:
        if not get_mandatory_guard_check(G, ['request_laptop'], ['export_data'], 'manager_approval'):
            error_msg = "Path from request_laptop to export_data bypasses manager_approval!"
            errors.append(error_msg)
            if not counterexample:
                counterexample = generate_counterexample(error_msg, missing_guard='manager_approval')
                return _build_response(False, counterexample, G, errors)

    # Check RBAC and Conditions
    for step in workflow.steps:
        if not is_authorized(step.role, step.action):
            error_msg = f"Role '{step.role}' is NOT authorized to perform action '{step.action}'"
            errors.append(error_msg)
            if not counterexample:
                counterexample = generate_counterexample(error_msg, failed_step=step.id)
                
        # Mock condition check (Threshold Tampering)
        if step.id == 'manager_approval' and step.condition and '50000' in step.condition:
            error_msg = f"Threshold tampering detected on '{step.id}'"
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
