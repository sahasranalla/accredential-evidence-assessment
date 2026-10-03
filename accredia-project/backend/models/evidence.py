from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EvidenceItem(BaseModel):
    chunk_id: Optional[str] = None
    document_id: str
    document_name: str = ""
    title: str
    page: int = 1
    section: str = "General"
    academic_year: str = "2024-25"
    criterion: str = "Criterion 6"
    subcriterion: str = ""
    department: str = "IQAC"
    document_type: str = "Institutional Report"
    source: str
    relevance: float = 0.85
    strength: float = 0.85
    evidence_type: str = "Direct Evidence"  # Direct Evidence, Supporting Evidence, Corroborating Evidence, Conflicting Evidence
    source_reliability: float = 0.95
    summary: str = ""
    excerpt: str
    author: str = ""
    status: str = "active"  # active, superseded
    date: str = "2025-05-15"
    verification_status: str = "verified"  # verified, unverified, gap
    supports: List[str] = Field(default_factory=list)
    contradicts: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class KnowledgeGap(BaseModel):
    gap_id: str
    criterion: str = "Criterion 6"
    subcriterion: str = ""
    topic: str
    description: str
    current_evidence_count: int = 0
    suggested_documents: List[str] = Field(default_factory=list)
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    reason: str = ""
    resolved: bool = False

class Citation(BaseModel):
    citation_id: str
    document_id: str
    document_name: str
    page: int
    section: str
    academic_year: str
    criterion: str
    source_file: str
    verified: bool = True
    snippet: str = ""

class CriterionCoverage(BaseModel):
    criterion_id: str
    criterion_name: str
    weightage: int
    evidence_count: int
    coverage_percentage: float
    status: str
