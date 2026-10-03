from pydantic import BaseModel
from typing import Optional

class ContradictionItem(BaseModel):
    contradiction_id: str
    topic: str
    claim_a: str
    source_a_id: str
    source_a_title: str
    source_a_page: int = 1
    source_a_status: str = "active"
    claim_b: str
    source_b_id: str
    source_b_title: str
    source_b_page: int = 1
    source_b_status: str = "superseded"
    conflict_analysis: str
    confidence_impact: float = -0.05
    resolution_basis: Optional[str] = None
    resolved_source_id: Optional[str] = None
