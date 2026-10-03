import os
import json
import re
from typing import List, Dict, Any
from ..models.evidence import EvidenceItem
from ..models.contradiction import ContradictionItem
from ..config import settings

class ContradictionDetector:
    """
    Detects potential evidentiary conflicts between institutional documents,
    such as divergent participation metrics between working drafts and final reports.
    """
    def __init__(self):
        self.predefined_contradictions: List[Dict[str, Any]] = []
        self._load_contradictions()

    def _load_contradictions(self):
        path = os.path.join(settings.METADATA_DIR, "contradictions.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.predefined_contradictions = json.load(f)
            except Exception:
                pass

    def detect_contradictions(self, evidence: List[EvidenceItem]) -> List[ContradictionItem]:
        contradictions: List[ContradictionItem] = []
        doc_ids = {e.document_id for e in evidence}
        
        # 1. Match predefined accreditation contradictions if both or related sources appear in retrieval
        for c in self.predefined_contradictions:
            src_a = c.get("source_a_id")
            src_b = c.get("source_b_id")
            
            # If at least one of the conflicting sources is retrieved and topic words are in evidence
            has_a = src_a in doc_ids
            has_b = src_b in doc_ids
            has_topic = any("faculty" in e.title.lower() or "training" in e.title.lower() or "draft" in e.title.lower() for e in evidence)

            if (has_a and has_b) or (has_b and has_topic) or (has_a and "draft" in " ".join(e.title.lower() for e in evidence)):
                item = ContradictionItem(
                    contradiction_id=c.get("contradiction_id", "CONTRAD-FDP-01"),
                    topic=c.get("topic", "Faculty Training Participation Count"),
                    claim_a=c.get("source_a_claim"),
                    source_a_id=src_a,
                    source_a_title=c.get("source_a_title"),
                    source_a_page=c.get("source_a_page", 6),
                    source_a_status=c.get("source_a_status", "active"),
                    claim_b=c.get("source_b_claim"),
                    source_b_id=src_b,
                    source_b_title=c.get("source_b_title"),
                    source_b_page=c.get("source_b_page", 2),
                    source_b_status=c.get("source_b_status", "superseded"),
                    conflict_analysis=c.get("conflict_analysis", "These institutional records report different participant counts for the same period."),
                    confidence_impact=-0.04
                )
                if not any(x.contradiction_id == item.contradiction_id for x in contradictions):
                    contradictions.append(item)

        # 2. Check for superseded vs active documents in retrieved evidence
        superseded_docs = [e for e in evidence if e.status == "superseded"]
        active_docs = [e for e in evidence if e.status == "active"]

        for sup in superseded_docs:
            for act in active_docs:
                if sup.academic_year == act.academic_year and sup.document_id != act.document_id:
                    cid = f"CONTRAD-{sup.document_id}-{act.document_id}"
                    if not any(x.contradiction_id == cid for x in contradictions):
                        contradictions.append(ContradictionItem(
                            contradiction_id=cid,
                            topic=f"Record Status Divergence: {sup.title} vs {act.title}",
                            claim_a=f"{act.title} (Page {act.page}): '{act.excerpt[:120]}...'",
                            source_a_id=act.document_id,
                            source_a_title=act.title,
                            source_a_page=act.page,
                            source_a_status="active",
                            claim_b=f"{sup.title} (Page {sup.page}): '{sup.excerpt[:120]}...'",
                            source_b_id=sup.document_id,
                            source_b_title=sup.title,
                            source_b_page=sup.page,
                            source_b_status="superseded",
                            conflict_analysis=f"Source {sup.document_id} is marked status '{sup.status}'. Verified active record {act.document_id} should be inspected alongside draft estimates.",
                            confidence_impact=-0.03
                        ))

        return contradictions

contradiction_detector = ContradictionDetector()
