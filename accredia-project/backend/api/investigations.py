from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from ..database import list_all_investigations, get_investigation_by_id
from ..services.investigation_service import investigation_service
from ..models.investigation import InvestigationRequest, InvestigationResponse

from ..core.graph_builder import graph_builder

router = APIRouter()

@router.get("/graph")
@router.get("/graph/master")
def get_master_graph() -> Dict[str, Any]:
    """Returns the Master Institutional Accreditation Knowledge Graph."""
    mg = graph_builder.build_master_graph()
    return mg.model_dump()

@router.get("/investigations")
@router.get("/search-history")
def get_investigations() -> List[Dict[str, Any]]:
    """Returns evidence search history."""
    return list_all_investigations()

@router.get("/investigations/{investigation_id}")
@router.get("/evidence-search/{investigation_id}")
def get_investigation(investigation_id: str) -> Dict[str, Any]:
    data = get_investigation_by_id(investigation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Accreditation search record not found.")
    return data

@router.get("/investigations/{investigation_id}/steps")
def get_steps(investigation_id: str) -> List[Dict[str, Any]]:
    data = get_investigation_by_id(investigation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Accreditation search record not found.")
    return data.get("steps", [])

@router.get("/investigations/{investigation_id}/evidence")
def get_evidence(investigation_id: str) -> List[Dict[str, Any]]:
    data = get_investigation_by_id(investigation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Accreditation search record not found.")
    return data.get("evidence", [])

@router.get("/investigations/{investigation_id}/graph")
@router.get("/evidence/{investigation_id}/graph")
def get_graph(investigation_id: str) -> Dict[str, Any]:
    data = get_investigation_by_id(investigation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Accreditation search record not found.")
    return data.get("graph", {"nodes": [], "edges": []})

@router.get("/investigations/{investigation_id}/report")
def get_report(investigation_id: str) -> Dict[str, Any]:
    data = get_investigation_by_id(investigation_id)
    if not data:
        raise HTTPException(status_code=404, detail="Accreditation search record not found.")
    return {
        "investigation_id": investigation_id,
        "question": data.get("question"),
        "report_markdown": data.get("report_markdown", "")
    }

@router.post("/investigate", response_model=InvestigationResponse)
@router.post("/evidence/search", response_model=InvestigationResponse)
@router.post("/evidence/ask", response_model=InvestigationResponse)
def execute_evidence_search(req: InvestigationRequest):
    q = req.question.strip()
    if not q or len(q) < 3:
        raise HTTPException(status_code=400, detail="Question must be at least 3 characters long.")
    
    try:
        response = investigation_service.investigate(
            question=q,
            academic_year=req.academic_year,
            criterion=req.criterion,
            department=req.department
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence search failed: {str(e)}")
