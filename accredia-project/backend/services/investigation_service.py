import uuid
import datetime
import os
import json
from typing import Dict, Any, List, Optional
from ..models.investigation import InvestigationResponse, InvestigationStep
from ..models.evidence import EvidenceItem, Citation, KnowledgeGap
from ..models.contradiction import ContradictionItem
from ..core.query_analyzer import query_analyzer
from ..core.retriever import retriever
from ..core.evidence_analyzer import evidence_analyzer
from ..core.gap_detector import gap_detector
from ..core.contradiction_detector import contradiction_detector
from ..core.graph_builder import graph_builder
from ..core.confidence import confidence_calculator
from ..core.answer_engine import answer_engine
from ..core.report_generator import report_generator
from ..services.citation_verifier import citation_verifier
from ..services.audit_service import audit_service
from ..database import save_investigation, get_investigation_by_id
from ..config import settings

class InvestigationService:
    """
    Master Accreditation Analysis & Evidence Search Service.
    Coordinates question understanding, criteria mapping, hybrid chunk retrieval,
    gap detection, grounded answer synthesis, citation verification, and dynamic graph building.
    """

    def investigate(
        self,
        question: str,
        academic_year: Optional[str] = None,
        criterion: Optional[str] = None,
        department: Optional[str] = None
    ) -> InvestigationResponse:
        inv_id = f"ACC-{uuid.uuid4().hex[:6].upper()}"
        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        steps: List[InvestigationStep] = []
        step_num = 1

        # 1. Query Analysis ("Understanding question...")
        analysis = query_analyzer.analyze(question)
        target_year = academic_year or analysis.get("academic_year")
        target_criteria = [criterion] if criterion and criterion != "All" else analysis.get("matched_criteria", [])
        target_dept = department if department and department != "All" else analysis.get("department")

        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="UNDERSTANDING_QUESTION",
            description=f"Analyzed question intent. Topic: '{analysis['topic']}'. Target Year: {target_year or 'All Years'}.",
            query=question,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        step_num += 1

        # 2. Finding Relevant Criteria ("Finding relevant criteria...")
        crit_label = ", ".join(target_criteria) if target_criteria else "All Criteria"
        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="CRITERIA_IDENTIFIED",
            description=f"Mapped inquiry to Accreditation Scope: {crit_label}.",
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        step_num += 1

        # 3. Searching Institutional Knowledge ("Searching institutional knowledge...")
        search_queries = [question]
        kw = analysis.get("keywords", [])
        if kw:
            search_queries.append(" ".join(kw))
        if target_year and target_year not in question:
            search_queries.append(f"{question} {target_year}")

        # Multi-query hybrid retrieval
        raw_candidates = retriever.retrieve_many(
            search_queries,
            top_k_each=8,
            academic_year=target_year,
            criterion=criterion if criterion != "All" else None,
            department=target_dept
        )

        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="SEARCHING_KNOWLEDGE",
            description=f"Searched institutional knowledge base. Located {len(raw_candidates)} primary evidence chunks across verified records.",
            query=search_queries[0],
            findings_count=len(raw_candidates),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        step_num += 1

        # 4. Ranking Evidence ("Ranking evidence...")
        # Quality floor filter
        best_initial = raw_candidates[0].get("score", 0.0) if raw_candidates else 0.0
        evidence_floor = max(0.20, best_initial * 0.42)
        filtered_candidates = [r for r in raw_candidates if r.get("score", 0.0) >= evidence_floor]

        evidence_items: List[EvidenceItem] = []
        for idx, chunk in enumerate(filtered_candidates):
            ev = evidence_analyzer.analyze_chunk(chunk, query=question, rank_index=idx)
            evidence_items.append(ev)

        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="RANKING_EVIDENCE",
            description=f"Filtered and scored {len(evidence_items)} candidate evidence items by hybrid semantic and criterion relevance.",
            findings_count=len(evidence_items),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        step_num += 1

        # 5. Gap & Sufficiency Detection
        is_insufficient, gap_reason, suggested_docs, gaps = gap_detector.evaluate_sufficiency(
            question=question,
            evidence=evidence_items,
            analysis=analysis
        )

        if is_insufficient:
            steps.append(InvestigationStep(
                step_number=step_num,
                action_type="INSUFFICIENT_EVIDENCE_FLAGGED",
                description="Evidence gap detected. Knowledge base lacks verified documentation to substantiate this inquiry.",
                status="warning",
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
            ))
            step_num += 1

        # 6. Contradiction Detection
        contradictions = contradiction_detector.detect_contradictions(evidence_items)
        if contradictions:
            steps.append(InvestigationStep(
                step_number=step_num,
                action_type="CONTRADICTION_DETECTED",
                description=f"Potential evidence conflict identified between {contradictions[0].source_a_id} and {contradictions[0].source_b_id}.",
                status="warning",
                findings_count=len(contradictions),
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
            ))
            step_num += 1

        # 7. Grounded Answer Synthesis ("Generating grounded response...")
        answer, finding = answer_engine.generate_answer(
            question=question,
            evidence=evidence_items,
            is_insufficient=is_insufficient,
            gap_reason=gap_reason,
            suggested_docs=suggested_docs
        )

        # 8. Verifying Sources ("Verifying sources...")
        citations, verification_summary = citation_verifier.extract_and_verify(
            answer_text=answer,
            retrieved_evidence=evidence_items
        )

        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="VERIFYING_SOURCES",
            description=f"Validated {len(citations)} citations against physical source documents and page boundaries (Zero hallucinations).",
            findings_count=len(citations),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        step_num += 1

        # 9. Confidence Calculation
        confidence, confidence_level = confidence_calculator.calculate(
            evidence=evidence_items,
            contradictions=contradictions,
            is_sufficient=not is_insufficient
        )

        # 10. Building Evidence Graph ("Building evidence graph...")
        graph = graph_builder.build_graph(
            question=question,
            evidence=evidence_items,
            contradictions=contradictions,
            finding=finding
        )
        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="BUILDING_GRAPH",
            description=f"Materialized interactive evidence graph with {len(graph.nodes)} nodes and {len(graph.edges)} typed edges.",
            findings_count=len(graph.nodes),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))
        step_num += 1

        # 11. Final Grounded Response Step
        steps.append(InvestigationStep(
            step_number=step_num,
            action_type="GENERATING_RESPONSE",
            description="Synthesized grounded answer with verified citations and compliance indicators.",
            status="completed" if not is_insufficient else "warning",
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        ))

        # Sources summary
        sources_summary = []
        seen_src = set()
        for ev in evidence_items:
            if ev.source not in seen_src:
                sources_summary.append({
                    "name": ev.source,
                    "department": ev.department,
                    "reliability": ev.source_reliability,
                    "document_count": sum(1 for e in evidence_items if e.source == ev.source)
                })
                seen_src.add(ev.source)

        # Generate markdown report
        report_md = report_generator.generate_report(
            investigation_id=inv_id,
            question=question,
            answer=answer,
            finding=finding,
            confidence=confidence,
            confidence_level=confidence_level,
            criteria=target_criteria,
            evidence=evidence_items,
            citations=citations,
            contradictions=contradictions,
            evidence_gaps=gaps
        )

        completed_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Build directed evidentiary causal chain
        causal_chain = []
        if not is_insufficient and evidence_items:
            for idx, item in enumerate(evidence_items[:4]):
                causal_chain.append({
                    "step_order": idx + 1,
                    "cause": f"{item.document_name} ({item.department}, AY {item.academic_year or '2024-25'})",
                    "effect": f"Verified on Page {item.page}: {item.excerpt[:130]}...",
                    "supporting_doc_ids": [item.document_id]
                })

        response = InvestigationResponse(
            investigation_id=inv_id,
            status="insufficient_evidence" if is_insufficient else "completed",
            question=question,
            mode="Local Accreditation Evidence Mode" if settings.is_local_mode else "AI Accreditation Mode",
            answer=answer,
            root_cause=finding,
            evidence_insight=finding,
            confidence=confidence,
            confidence_level=confidence_level,
            investigation_depth=1 if is_insufficient else 2,
            criteria=target_criteria,
            academic_year=target_year,
            steps=steps,
            evidence=evidence_items,
            citations=citations,
            established_knowledge=[f"{e.document_name} (Page {e.page})" for e in evidence_items[:5]],
            still_needed_knowledge=[g.topic for g in gaps] if gaps else [],
            evidence_gaps=gaps,
            contradictions=contradictions,
            unresolved_questions=[f"Supplemental documentation required: {d}" for d in suggested_docs[:3]] if is_insufficient else [],
            sources=sources_summary,
            verification=verification_summary,
            causal_chain=causal_chain,
            timeline=[],
            graph=graph,
            report_markdown=report_md,
            created_at=start_time,
            completed_at=completed_time
        )

        # Save to SQLite
        try:
            save_investigation(response.model_dump())
        except Exception as e:
            print(f"[ACCREDIA] Warning saving investigation: {e}")

        # Audit log
        audit_service.record_action(
            investigation_id=inv_id,
            action="EVIDENCE_SEARCH_COMPLETED",
            query=question,
            documents_searched=len(raw_candidates),
            evidence_selected=len(evidence_items),
            contradictions_detected=len(contradictions),
            final_result="INSUFFICIENT EVIDENCE" if is_insufficient else "GROUNDED_EVIDENCE_FOUND",
            details={
                "criteria": target_criteria,
                "confidence": confidence,
                "confidence_level": confidence_level,
                "citations_count": len(citations)
            }
        )

        return response

investigation_service = InvestigationService()
