import copy
from compiler.ir import WorkflowIR

def mutate_role(workflow: WorkflowIR, step_id: str, new_role: str) -> WorkflowIR:
    """Mutates a step to simulate a role escalation attack."""
    mutated = copy.deepcopy(workflow)
    for step in mutated.steps:
        if step.id == step_id:
            step.role = new_role
    return mutated

def mutate_bypass_step(workflow: WorkflowIR, step_to_bypass: str) -> WorkflowIR:
    """Removes a step from dependencies, trying to bypass it."""
    mutated = copy.deepcopy(workflow)
    
    bypassed_deps = []
    for step in mutated.steps:
        if step.id == step_to_bypass:
            bypassed_deps = step.dependencies
            break
            
    for step in mutated.steps:
        if step_to_bypass in step.dependencies:
            step.dependencies.remove(step_to_bypass)
            step.dependencies.extend(bypassed_deps)
    return mutated

def mutate_remove_step(workflow: WorkflowIR, step_to_remove: str) -> WorkflowIR:
    """Removes a step entirely from the workflow."""
    mutated = copy.deepcopy(workflow)
    mutated.steps = [s for s in mutated.steps if s.id != step_to_remove]
    # Remove references to it
    for step in mutated.steps:
        if step_to_remove in step.dependencies:
            step.dependencies.remove(step_to_remove)
    return mutated

def mutate_condition(workflow: WorkflowIR, step_id: str, new_condition: str) -> WorkflowIR:
    """Changes a condition threshold to simulate tampering."""
    mutated = copy.deepcopy(workflow)
    for step in mutated.steps:
        if step.id == step_id:
            step.condition = new_condition
    return mutated

def mutate_inject_cycle(workflow: WorkflowIR, step_from: str, step_to: str) -> WorkflowIR:
    """Injects a cyclic dependency."""
    mutated = copy.deepcopy(workflow)
    for step in mutated.steps:
        if step.id == step_from:
            step.dependencies.append(step_to)
    return mutated
