from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
import os
from ..models.investigation import InvestigationRequest, InvestigationResponse
from ..services.investigation_service import investigation_service
from ..services.vector_store import vector_store
from ..database import list_all_investigations, list_evidence_gaps, list_criteria
from ..config import settings
from .criteria import get_criteria_coverage

router = APIRouter()

@router.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "operational",
        "app_name": settings.APP_NAME,
        "subtitle": settings.APP_SUBTITLE,
        "tagline": settings.TAGLINE,
        "institution": settings.INSTITUTION_NAME,
        "short_name": settings.INSTITUTION_SHORT,
        "location": settings.INSTITUTION_LOCATION,
        "version": settings.VERSION,
        "mode": "Local Accreditation Evidence Mode" if settings.is_local_mode else "AI Evidence Assistant Mode",
        "documents_indexed": len(vector_store.documents),
        "chunks_indexed": len(vector_store.chunks),
        "database": "SQLite (operational)",
        "vector_engine": "FAISS (IndexFlatIP) + Dense Embeddings"
    }

@router.get("/dashboard/stats")
def get_dashboard_stats() -> Dict[str, Any]:
    searches = list_all_investigations()
    documents = vector_store.documents
    chunks = vector_store.chunks
    gaps = list_evidence_gaps()
    criteria_coverage = get_criteria_coverage()
    
    total_searches = len(searches)
    completed_searches = sum(1 for i in searches if i.get("status") == "completed")
    insufficient_searches = sum(1 for i in searches if i.get("status") == "insufficient_evidence")
    
    total_evidence_items = len(chunks)
    total_docs = len(documents)

    # Academic years distribution
    years_counts: Dict[str, int] = {}
    for d in documents:
        yr = d.get("academic_year", "2024-25")
        years_counts[yr] = years_counts.get(yr, 0) + 1
    
    academic_years = sorted(list(years_counts.keys()))

    # Department distribution
    dept_counts: Dict[str, int] = {}
    for d in documents:
        dept = d.get("department", "IQAC")
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    dept_distribution = [{"name": k, "count": v} for k, v in sorted(dept_counts.items(), key=lambda x: -x[1])]
    year_distribution = [{"year": k, "count": v} for k, v in sorted(years_counts.items(), key=lambda x: x[0])]

    return {
        "institution_name": settings.INSTITUTION_NAME,
        "institution_short": settings.INSTITUTION_SHORT,
        "location": settings.INSTITUTION_LOCATION,
        "documents_indexed": total_docs,
        "evidence_items": total_evidence_items,
        "criteria_covered": "7 of 7",
        "evidence_gaps_count": len(gaps),
        "academic_years_count": len(academic_years),
        "academic_years": academic_years,
        "departments_count": len(dept_counts),
        "searches_performed": total_searches,
        "completed_searches": completed_searches,
        "insufficient_evidence_searches": insufficient_searches,
        "criteria_coverage": criteria_coverage,
        "department_distribution": dept_distribution,
        "year_distribution": year_distribution,
        "recent_searches": searches[:8]
    }
