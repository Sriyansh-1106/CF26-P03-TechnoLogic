"""
compiler/authorization.py
=========================
Role-Based Access Control (RBAC) matrix and verification logic.
"""

from typing import Dict, List, Optional

# Standard RBAC Matrix for Enterprise Workflows
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "Employee": [
        "submit",
        "verify_vendor",
        "submit_purchase_request",
        "submit_vendor_invoice",
        "request_laptop"
    ],
    "Manager": [
        "approve_budget",
        "approve_laptop",
        "reject_laptop",
        "review"
    ],
    "Finance_Director": [
        "approve_budget",
        "finance_approval",
        "release_payment"
    ],
    "IT Manager": [
        "approve_laptop",
        "reject_laptop"
    ],
    "System": [
        "create_ticket",
        "close_ticket",
        "send_notification"
    ],
    "Admin": ["*"]
}

_MANAGER_BUDGET_LIMIT = 20_000.0

def check_role_permission(role: str, action: str, amount: Optional[float] = None) -> bool:
    """
    Checks if a given role is authorized to perform a specific action,
    optionally checking financial amount limits.
    """
    if not role or role not in ROLE_PERMISSIONS:
        return False

    allowed_actions = ROLE_PERMISSIONS[role]
    if "*" in allowed_actions:
        return True

    if action not in allowed_actions:
        return False

    # Financial limit check for Manager
    if role == "Manager" and action == "approve_budget" and amount is not None:
        if amount > _MANAGER_BUDGET_LIMIT:
            return False

    return True

# Exported aliases
is_authorized = check_role_permission

def get_role_actions(role: str) -> List[str]:
    """Returns the list of actions permitted for a role."""
    return ROLE_PERMISSIONS.get(role, [])

def list_roles() -> List[str]:
    """Returns all defined roles."""
    return list(ROLE_PERMISSIONS.keys())

def roles_for_action(action: str) -> List[str]:
    """Returns all roles permitted to perform a given action."""
    matching = []
    for role, actions in ROLE_PERMISSIONS.items():
        if "*" in actions or action in actions:
            matching.append(role)
    return matching
