# compiler/__init__.py
# Expose the public API surface so teammates can do:
#   from compiler import parse_policy, check_ambiguity, WorkflowIR

from compiler.ir import StepNode, WorkflowIR
from compiler.parser import parse_policy
from compiler.ambiguity import check_ambiguity, batch_check_ambiguity
from compiler.authorization import (
    ROLE_PERMISSIONS,
    check_role_permission,
    get_role_actions,
    list_roles,
    roles_for_action,
)

__all__ = [
    # IR models
    "WorkflowIR",
    "StepNode",
    # Parser
    "parse_policy",
    # Ambiguity
    "check_ambiguity",
    "batch_check_ambiguity",
    # Authorization
    "ROLE_PERMISSIONS",
    "check_role_permission",
    "get_role_actions",
    "list_roles",
    "roles_for_action",
]
