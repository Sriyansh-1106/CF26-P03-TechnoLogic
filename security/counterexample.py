def generate_counterexample(reason: str, failed_step: str = None, missing_guard: str = None) -> str:
    """Formats a human-readable explanation of an invariant failure."""
    if missing_guard and failed_step:
        return f"FAILED: Step '{failed_step}' is reachable without satisfying mandatory guard '{missing_guard}'."
    
    if failed_step:
        return f"FAILED: Error at step '{failed_step}' - {reason}."
        
    return f"FAILED: {reason}"
