from __future__ import annotations
import json
import uuid
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class StepNode(BaseModel):
    id: str
    action: str
    role: str
    condition: Optional[str] = None
    is_required: bool = True
    dependencies: List[str] = Field(default_factory=list)

# Backward-compatibility alias
Step = StepNode

class WorkflowIR(BaseModel):
    workflow_id: str = Field(default_factory=lambda: f"wf-{uuid.uuid4().hex[:8]}")
    title: str = "Enterprise Workflow"
    trigger: str = "Policy Trigger"
    steps: List[StepNode] = Field(default_factory=list)
    roles_allowed: List[str] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkflowIR:
        steps_data = data.get("steps", [])
        steps = [StepNode(**s) if isinstance(s, dict) else s for s in steps_data]
        return cls(
            workflow_id=data.get("workflow_id", f"wf-{uuid.uuid4().hex[:8]}"),
            title=data.get("title", "Enterprise Workflow"),
            trigger=data.get("trigger", "Policy Trigger"),
            steps=steps,
            roles_allowed=data.get("roles_allowed", [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> WorkflowIR:
        return cls.from_dict(json.loads(json_str))

    def get_step(self, step_id: str) -> Optional[StepNode]:
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def required_steps(self) -> List[StepNode]:
        return [step for step in self.steps if step.is_required]

    def roles_in_workflow(self) -> List[str]:
        roles = []
        for step in self.steps:
            if step.role not in roles:
                roles.append(step.role)
        return roles
