from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .evidence import EvidenceItem, KnowledgeGap, Citation
from .contradiction import ContradictionItem

class InvestigationStep(BaseModel):
    step_number: int
    action_type: str
    description: str
    query: Optional[str] = None
    status: str = "completed"  # in_progress, completed, warning
    findings_count: int = 0
    timestamp: str

class GraphNode(BaseModel):
    id: str
    type: str  # criterion, subcriterion, document, page, section, department, evidence, academic_year, root_cause
    label: str
    data: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, float]] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: str  # classifies, satisfies, cited_in, on_page, authored_by, conflicting_with, supports
    strength: float = 1.0

class EvidenceGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)

class InvestigationRequest(BaseModel):
    question: str
    academic_year: Optional[str] = None
    criterion: Optional[str] = None
    department: Optional[str] = None

class InvestigationResponse(BaseModel):
    investigation_id: str
    status: str  # completed, insufficient_evidence
    question: str
    mode: str = "Local Evidence Mode"
    answer: str
    root_cause: Optional[str] = None  # Evidence Insight / Finding
    evidence_insight: Optional[str] = None
    confidence: float
    confidence_level: str  # High Evidence Support, Moderate Evidence Support, Limited Evidence Support
    investigation_depth: int = 1
    criteria: List[str] = Field(default_factory=list)
    academic_year: Optional[str] = None
    steps: List[InvestigationStep] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    established_knowledge: List[str] = Field(default_factory=list)
    still_needed_knowledge: List[str] = Field(default_factory=list)
    evidence_gaps: List[KnowledgeGap] = Field(default_factory=list)
    contradictions: List[ContradictionItem] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    verification: Dict[str, Any] = Field(default_factory=dict)
    causal_chain: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    graph: EvidenceGraph = Field(default_factory=EvidenceGraph)
    report_markdown: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
