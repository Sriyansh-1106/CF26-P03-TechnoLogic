# Mock RBAC definitions for graph verification
# Maps a role to a list of allowed actions
RBAC_MATRIX = {
    "IT Manager": ["approve_laptop", "reject_laptop"],
    "Finance": ["approve_budget"],
    "HR": ["onboard_employee", "terminate_employee"],
    "Employee": ["request_laptop"],
    "System": ["create_ticket", "close_ticket", "send_notification"]
}

def is_authorized(role: str, action: str) -> bool:
    """Check if role is authorized to perform action."""
    return action in RBAC_MATRIX.get(role, [])
