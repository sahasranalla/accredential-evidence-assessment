from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional
from ..services.vector_store import vector_store

router = APIRouter()

@router.get("/evidence")
def list_evidence(
    academic_year: Optional[str] = Query(None),
    criterion: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    q: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    """Returns repository documents and chunks enriched with accreditation metadata and reliability."""
    docs = vector_store.documents
    results = []
    for d in docs:
        if academic_year and academic_year != "All" and d.get("academic_year") != academic_year:
            continue
        if criterion and criterion != "All" and d.get("criterion") != criterion:
            continue
        if department and department != "All" and d.get("department", "").lower() != department.lower():
            continue
        if q:
            q_low = q.lower()
            if (q_low not in d.get("title", "").lower() and 
                q_low not in d.get("summary", "").lower() and 
                q_low not in d.get("document_id", "").lower()):
                continue
        results.append(d)
    return results

@router.get("/evidence/chunks")
def list_evidence_chunks(
    document_id: Optional[str] = Query(None),
    criterion: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
) -> List[Dict[str, Any]]:
    """Returns granular indexed evidence chunks."""
    chunks = vector_store.chunks
    filtered = []
    for c in chunks:
        if document_id and c.get("document_id") != document_id:
            continue
        if criterion and criterion != "All" and c.get("criterion") != criterion:
            continue
        filtered.append(c)
        if len(filtered) >= limit:
            break
    return filtered
