import os
import shutil
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from ..services.vector_store import vector_store
from ..services.ingestion import ingestion_service
from ..config import settings

router = APIRouter()

@router.get("/documents")
def list_documents(
    academic_year: Optional[str] = Query(None),
    criterion: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None)
) -> List[Dict[str, Any]]:
    docs = vector_store.documents
    results = []
    for d in docs:
        if academic_year and academic_year != "All" and d.get("academic_year") != academic_year:
            continue
        if criterion and criterion != "All" and d.get("criterion") != criterion:
            continue
        if department and department != "All" and d.get("department", "").lower() != department.lower():
            continue
        if status and status != "All" and d.get("status", "").lower() != status.lower():
            continue
        if q:
            q_low = q.lower()
            if (q_low not in d.get("title", "").lower() and 
                q_low not in d.get("summary", "").lower() and 
                q_low not in d.get("document_id", "").lower()):
                continue
        results.append(d)
    return results

@router.get("/documents/{document_id}")
def get_document(document_id: str) -> Dict[str, Any]:
    docs = vector_store.documents
    for d in docs:
        if d["document_id"] == document_id or d["title"].lower() == document_id.lower():
            chunks = vector_store.get_document_chunks(d["document_id"])
            res = dict(d)
            res["chunks"] = chunks
            return res
    raise HTTPException(status_code=404, detail=f"Document {document_id} not found.")

@router.get("/documents/{document_id}/page/{page_num}")
def get_document_page(document_id: str, page_num: int) -> Dict[str, Any]:
    chunks = vector_store.get_document_chunks(document_id)
    page_chunks = [c for c in chunks if c.get("page") == page_num]
    if not page_chunks:
        # Fallback to closest chunk
        page_chunks = chunks[:1]
    
    if not page_chunks:
        raise HTTPException(status_code=404, detail=f"Page {page_num} not found for document {document_id}")

    first = page_chunks[0]
    return {
        "document_id": document_id,
        "document_name": first.get("document_name", document_id),
        "page": page_num,
        "section": first.get("section", "General Overview"),
        "academic_year": first.get("academic_year", "2024-25"),
        "criterion": first.get("criterion", "Criterion 6"),
        "department": first.get("department", "IQAC"),
        "source": first.get("source", ""),
        "chunks": page_chunks,
        "full_text": "\n\n".join(c.get("text", "") for c in page_chunks)
    }

@router.get("/documents/{document_id}/file")
def get_document_file(document_id: str):
    """Serves the actual physical PDF or DOCX file for the Source Viewer."""
    docs = vector_store.documents
    target_doc = next((d for d in docs if d["document_id"] == document_id), None)
    if not target_doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    source_fname = target_doc.get("source")
    if not source_fname:
        raise HTTPException(status_code=404, detail="Source file reference missing.")

    file_path = os.path.join(settings.DOCS_DIR, source_fname)
    if not os.path.exists(file_path):
        # Check backend/data/accreditation/documents
        alt_path = os.path.join(settings.BASE_DIR, "backend", "data", "accreditation", "documents", source_fname)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise HTTPException(status_code=404, detail=f"File {source_fname} not found on disk.")

    media_type = "application/pdf" if source_fname.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(file_path, media_type=media_type, filename=source_fname)

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    academic_year: str = Query("2024-25"),
    criterion: str = Query("Criterion 6"),
    department: str = Query("IQAC")
):
    """Uploads and ingests a new PDF or DOCX institutional document on the fly."""
    if not file.filename.endswith(".pdf") and not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    dest_path = os.path.join(settings.DOCS_DIR, file.filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ingest the new document
    doc_id = f"DOC-UP-{file.filename[:8].upper()}"
    meta = {
        "document_id": doc_id,
        "title": file.filename.replace("_", " ").replace(".pdf", "").title(),
        "academic_year": academic_year,
        "criterion": criterion,
        "department": department,
        "document_type": "Uploaded Record",
        "status": "active"
    }

    new_chunks = ingestion_service.chunk_document(file.filename, dest_path, meta)
    all_chunks = list(vector_store.chunks) + new_chunks
    vector_store.build_index(all_chunks)

    return {
        "status": "success",
        "message": f"Document {file.filename} uploaded and indexed successfully.",
        "document_id": doc_id,
        "chunks_indexed": len(new_chunks),
        "total_documents": len(vector_store.documents)
    }

@router.post("/documents/index")
def trigger_reindex():
    """Triggers re-ingestion and re-indexing of all repository documents."""
    chunks = ingestion_service.ingest_all()
    vector_store.build_index(chunks)
    return {
        "status": "success",
        "total_chunks": len(chunks),
        "total_documents": len(vector_store.documents)
    }
