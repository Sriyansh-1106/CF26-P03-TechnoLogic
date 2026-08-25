"""
compiler/ir.py
==============
Intermediate Representation (IR) data models for the VeriFlow neurosymbolic
safety compiler.

These Pydantic v2 models are the **shared data contract** between all team
members.  Every stage of the pipeline (parser → validator → executor) reads
and writes WorkflowIR objects.

Exported symbols used by teammates
-----------------------------------
    WorkflowIR   – root workflow model
    StepNode     – a single workflow step
"""

from __future__ import annotations

import json
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# StepNode
# ---------------------------------------------------------------------------


class StepNode(BaseModel):
    """Represents one discrete step inside a compiled workflow.

    Attributes
    ----------
    id:           Unique identifier for the step (e.g. ``"step_1"``).
    action:       The action performed at this step (e.g. ``"submit_form"``).
    role:         The organisational role responsible for this step.
    condition:    Optional guard expression evaluated before execution.
    is_required:  Whether skipping this step is a policy violation.
    dependencies: List of step IDs that must complete before this one.
    """

    id: str = Field(..., description="Unique step identifier")
    action: str = Field(..., description="Action performed at this step")
    role: str = Field(..., description="Organisational role owning this step")
    condition: Optional[str] = Field(
        default=None,
        description="Optional Boolean guard expression (e.g. 'amount > 50000')",
    )
    is_required: bool = Field(
        default=True,
        description="Whether this step is mandatory for policy compliance",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="IDs of steps that must complete before this step",
    )


# Alias for backward compatibility
Step = StepNode


# ---------------------------------------------------------------------------
# WorkflowIR
# ---------------------------------------------------------------------------


class WorkflowIR(BaseModel):
    """Root Intermediate Representation for a compiled business policy.

    Attributes
    ----------
    workflow_id:   UUID-like string uniquely identifying this compiled workflow.
    title:         Human-readable title extracted from the source policy.
    trigger:       The business event that initiates this workflow.
    steps:         Ordered list of :class:`StepNode` objects.
    roles_allowed: Roles that are permitted to interact with this workflow.
    """

    workflow_id: str = Field(..., description="Unique workflow identifier (UUID)")
    title: str = Field(..., description="Human-readable workflow title")
    trigger: str = Field(
        ..., description="Business event that initiates the workflow"
    )
    steps: List[StepNode] = Field(
        ..., description="Ordered list of workflow steps"
    )
    roles_allowed: List[str] = Field(
        default_factory=list,
        description="Roles permitted to interact with this workflow",
    )

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return the workflow as a plain Python dictionary (deep copy)."""
        return self.model_dump()

    def to_json(self, *, indent: int = 2) -> str:
        """Return the workflow serialised as a pretty-printed JSON string.

        Parameters
        ----------
        indent: Number of spaces used for JSON indentation (default 2).
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowIR":
        """Deserialise a :class:`WorkflowIR` from a plain dictionary."""
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, json_str: str) -> "WorkflowIR":
        """Deserialise a :class:`WorkflowIR` from a JSON string."""
        return cls.model_validate(json.loads(json_str))

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_step(self, step_id: str) -> Optional[StepNode]:
        """Return the :class:`StepNode` with the given *step_id*, or ``None``."""
        return next((s for s in self.steps if s.id == step_id), None)

    def required_steps(self) -> List[StepNode]:
        """Return only the steps that are marked as required."""
        return [s for s in self.steps if s.is_required]

    def roles_in_workflow(self) -> List[str]:
        """Return the distinct set of roles referenced across all steps."""
        return list({s.role for s in self.steps})
