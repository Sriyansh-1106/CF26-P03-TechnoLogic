from pydantic import BaseModel
from typing import List, Optional

class Step(BaseModel):
    id: str
    role: str
    action: str
    condition: Optional[str] = None
    dependencies: List[str] = []
    
class WorkflowIR(BaseModel):
    steps: List[Step]
