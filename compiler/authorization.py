"""
compiler/authorization.py
==========================
Role-Based Access Control (RBAC) Matrix for the VeriFlow pipeline.

Defines which actions each organisational role may perform and the optional
numeric conditions attached to those permissions.

Exported contract (used by teammates)
--------------------------------------
    ROLE_PERMISSIONS  – dict mapping roles to their allowed actions
    check_role_permission(role, action, amount=None) -> bool
    get_role_actions(role) -> list[str]
"""

from __future__ import annotations

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# RBAC Matrix
# ---------------------------------------------------------------------------

# Structure:
#   role -> list of (action, max_amount_exclusive | None)
#
# max_amount_exclusive = None  → no monetary restriction
# max_amount_exclusive = N     → permission applies only when amount <= N

_ROLE_ACTION_TABLE: Dict[str, List[tuple[str, Optional[float]]]] = {
    "Employee": [
        ("submit", None),
        ("verify_vendor", None),
    ],
    "Manager": [
        ("submit", None),          # Managers may also submit on behalf of team
        ("approve_budget", 20_000),  # only for amount <= 20,000
    ],
    "Finance_Director": [
        ("approve_budget", None),   # no upper limit
        ("finance_approval", None),
        ("release_payment", None),
    ],
    "Admin": [
        ("*", None),               # wildcard – all actions allowed
    ],
}

# Public flat dict: role → list[str]  (for introspection / serialisation)
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    role: ["*"] if any(a == "*" for a, _ in perms) else [a for a, _ in perms]
    for role, perms in _ROLE_ACTION_TABLE.items()
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def check_role_permission(
    role: str,
    action: str,
    amount: Optional[float] = None,
) -> bool:
    """Return ``True`` if *role* is permitted to perform *action*.

    Parameters
    ----------
    role:
        Organisational role string (e.g. ``"Manager"``).
    action:
        Action name to check (e.g. ``"approve_budget"``).
    amount:
        Optional monetary value for amount-gated permissions.
        If the permission has a ``max_amount_exclusive`` limit and *amount* is
        provided, the permission is only granted when ``amount <= limit``.

    Returns
    -------
    bool
        ``True`` if the role–action combination is authorised.
    """
    if role not in _ROLE_ACTION_TABLE:
        return False

    for perm_action, max_amount in _ROLE_ACTION_TABLE[role]:
        # Admin wildcard
        if perm_action == "*":
            return True

        if perm_action == action:
            # No monetary restriction on this permission
            if max_amount is None:
                return True
            # Monetary restriction: check only if caller provided an amount
            if amount is not None and amount <= max_amount:
                return True
            # If no amount was given we grant the permission (caller must
            # validate amount separately if needed)
            if amount is None:
                return True

    return False


def get_role_actions(role: str) -> List[str]:
    """Return the list of action strings allowed for *role*.

    Admin returns ``["*"]``.  An unknown role returns an empty list.
    """
    return ROLE_PERMISSIONS.get(role, [])


def list_roles() -> List[str]:
    """Return all defined role names."""
    return list(_ROLE_ACTION_TABLE.keys())


def roles_for_action(action: str) -> List[str]:
    """Return all roles that are permitted to perform *action*.

    Parameters
    ----------
    action:
        The action name to query.

    Returns
    -------
    list[str]
        Roles that can perform this action (Admin always included).
    """
    result: List[str] = []
    for role, perms in _ROLE_ACTION_TABLE.items():
        for perm_action, _ in perms:
            if perm_action in ("*", action):
                result.append(role)
                break
    return result
