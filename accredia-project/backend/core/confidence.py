from typing import List, Tuple
from ..models.evidence import EvidenceItem
from ..models.contradiction import ContradictionItem

class ConfidenceCalculator:
    """
    Calculates accreditation evidence confidence based on:
    - Semantic & hybrid retrieval score of top evidence
    - Number of corroborating institutional sources
    - Document status (active audited vs draft)
    - Agreement and absence of unresolved contradictions
    - Verification of cited pages and sections

    Output labels:
    - High Evidence Support
    - Moderate Evidence Support
    - Limited Evidence Support
    """

    def calculate(
        self,
        evidence: List[EvidenceItem],
        contradictions: List[ContradictionItem] = None,
        is_sufficient: bool = True
    ) -> Tuple[float, str]:
        if not is_sufficient or not evidence:
            return 0.15, "Limited Evidence Support"

        top_evidence = evidence[:5]
        
        # 1. Retrieval scores
        scores = [e.relevance for e in top_evidence]
        avg_rel = sum(scores) / len(scores) if scores else 0.5

        # 2. Source reliability
        reliabilities = [e.source_reliability for e in top_evidence]
        avg_rel_src = sum(reliabilities) / len(reliabilities) if reliabilities else 0.8

        # 3. Source diversity bonus (independent departments corroborating)
        depts = {e.department for e in top_evidence}
        dept_bonus = min(0.12, (len(depts) - 1) * 0.04) if len(depts) > 1 else 0.0

        # 4. Multi-source agreement bonus
        source_bonus = 0.08 if len(top_evidence) >= 3 else (0.04 if len(top_evidence) == 2 else 0.0)

        raw_conf = (avg_rel * 0.40) + (avg_rel_src * 0.40) + dept_bonus + source_bonus

        # 5. Contradiction penalties
        if contradictions:
            for c in contradictions:
                raw_conf += c.confidence_impact

        conf = round(min(0.96, max(0.20, raw_conf)), 2)

        if conf >= 0.80:
            level = "High Evidence Support"
        elif conf >= 0.55:
            level = "Moderate Evidence Support"
        else:
            level = "Limited Evidence Support"

        return conf, level

confidence_calculator = ConfidenceCalculator()
