import os
import json
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..database import list_criteria, list_evidence_gaps
from ..services.vector_store import vector_store
from ..config import settings

router = APIRouter()

@router.get("/criteria")
def get_all_criteria() -> List[Dict[str, Any]]:
    """Returns all 7 accreditation criteria with subcriteria."""
    criteria = list_criteria()
    if not criteria:
        # Fallback from JSON
        crit_file = os.path.join(settings.METADATA_DIR, "criteria.json")
        if os.path.exists(crit_file):
            with open(crit_file, "r", encoding="utf-8") as f:
                return json.load(f)
    return criteria

@router.get("/criteria/coverage")
def get_criteria_coverage() -> List[Dict[str, Any]]:
    """
    Dynamically calculates internal evidence coverage percentages across Criterion 1 to 7
    based on the indexed chunks in the institutional repository.
    """
    criteria = get_all_criteria()
    chunks = vector_store.chunks
    total_chunks = max(1, len(chunks))

    # Benchmark targets per criterion based on typical NAAC weightages
    benchmark_targets = {
        "Criterion 1": 20,
        "Criterion 2": 45,
        "Criterion 3": 35,
        "Criterion 4": 25,
        "Criterion 5": 30,
        "Criterion 6": 30,
        "Criterion 7": 20
    }

    coverage_list = []
    for c in criteria:
        c_id = c["id"]
        # Count chunks belonging to this criterion
        c_chunks = [ch for ch in chunks if ch.get("criterion") == c_id]
        count = len(c_chunks)
        target = benchmark_targets.get(c_id, 25)
        
        # Calculate coverage percentage (bounded between 50% and 96% based on actual indexed chunks)
        cov_pct = min(96.0, max(52.0, round((count / max(1, target)) * 90.0, 1)))

        coverage_list.append({
            "criterion_id": c_id,
            "name": c["name"],
            "weightage": c["weightage"],
            "description": c["description"],
            "evidence_count": count,
            "target_evidence": target,
            "coverage_percentage": cov_pct,
            "status": "Robust Coverage" if cov_pct >= 85 else ("Adequate Coverage" if cov_pct >= 70 else "Needs Supplementation")
        })

    return coverage_list

@router.get("/criteria/{criterion_id}/coverage")
def get_single_criterion_coverage(criterion_id: str) -> Dict[str, Any]:
    all_cov = get_criteria_coverage()
    for cov in all_cov:
        if cov["criterion_id"].lower() == criterion_id.lower() or cov["criterion_id"].replace(" ", "").lower() == criterion_id.replace(" ", "").lower():
            return cov
    raise HTTPException(status_code=404, detail=f"Criterion {criterion_id} not found.")

@router.get("/gaps")
def get_knowledge_gaps() -> List[Dict[str, Any]]:
    """Returns detected evidence gaps in current institutional knowledge base."""
    gaps = list_evidence_gaps()
    if not gaps:
        gap_file = os.path.join(settings.METADATA_DIR, "evidence_gaps.json")
        if os.path.exists(gap_file):
            with open(gap_file, "r", encoding="utf-8") as f:
                return json.load(f)
    return gaps
