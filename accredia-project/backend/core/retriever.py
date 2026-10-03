from typing import List, Dict, Any, Optional
from ..services.vector_store import vector_store

class Retriever:
    """
    Accreditation Multi-Hop Retriever.
    Searches indexed institutional document chunks across semantic, keyword,
    and metadata dimensions with filtering support for Academic Year, Criterion, and Department.
    """
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        academic_year: Optional[str] = None,
        criterion: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return vector_store.search(
            query,
            top_k=top_k,
            academic_year=academic_year,
            criterion=criterion,
            department=department
        )

    def retrieve_many(
        self,
        queries: List[str],
        top_k_each: int = 8,
        academic_year: Optional[str] = None,
        criterion: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        merged: Dict[str, Dict[str, Any]] = {}
        for q in queries:
            if not q or not q.strip():
                continue
            candidates = self.retrieve(
                q,
                top_k=top_k_each,
                academic_year=academic_year,
                criterion=criterion,
                department=department
            )
            for chunk in candidates:
                cid = chunk.get("chunk_id", chunk.get("document_id"))
                existing = merged.get(cid)
                if existing is None or chunk.get("score", 0) > existing.get("score", 0):
                    merged[cid] = chunk
                    
        return sorted(merged.values(), key=lambda d: d.get("score", 0), reverse=True)

retriever = Retriever()
