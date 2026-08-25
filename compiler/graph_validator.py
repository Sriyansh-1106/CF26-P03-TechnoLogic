import networkx as nx
from compiler.ir import WorkflowIR

def build_workflow_graph(workflow: WorkflowIR) -> tuple[nx.DiGraph, bool, list[str]]:
    """Builds a NetworkX DAG from the WorkflowIR."""
    G = nx.DiGraph()
    errors = []
    
    # Add nodes
    for step in workflow.steps:
        G.add_node(step.id, role=step.role, action=step.action, condition=step.condition)
    
    # Add edges based on dependencies
    for step in workflow.steps:
        for dep in step.dependencies:
            if dep not in G.nodes:
                errors.append(f"Dependency '{dep}' for step '{step.id}' does not exist.")
            else:
                G.add_edge(dep, step.id)
            
    is_dag = nx.is_directed_acyclic_graph(G)
    if not is_dag:
        errors.append("Cyclic dependency detected in workflow graph!")
        
    return G, is_dag, errors

def check_reachability(G: nx.DiGraph, source: str, target: str) -> bool:
    """Checks if target is reachable from source."""
    if source not in G or target not in G:
        return False
    return nx.has_path(G, source, target)

def get_mandatory_guard_check(G: nx.DiGraph, start_nodes: list[str], end_nodes: list[str], guard_node: str) -> bool:
    """
    Checks if there's any path from start to end that BYPASSES the guard_node.
    Returns False if such a bypass path exists. True if all paths go through the guard.
    """
    return check_all_paths_pass_guards(G, start_nodes, end_nodes, [guard_node])

def check_all_paths_pass_guards(G: nx.DiGraph, start_nodes: list[str], end_nodes: list[str], guard_nodes: list[str]) -> bool:
    """
    Checks if EVERY path from start to end passes through AT LEAST ONE of the guard nodes.
    Returns False if a completely unguarded bypass path exists.
    """
    G_without_guards = G.copy()
    for g in guard_nodes:
        if g in G_without_guards:
            G_without_guards.remove_node(g)
            
    for start in start_nodes:
        for end in end_nodes:
            if start in G_without_guards and end in G_without_guards:
                if nx.has_path(G_without_guards, start, end):
                    # Found an unguarded path from start to end!
                    return False
    return True
