import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db, list_all_investigations
from .services.vector_store import vector_store
from .services.ingestion import ingestion_service
from .services.investigation_service import investigation_service

from .api.research import router as research_router
from .api.investigations import router as investigations_router
from .api.documents import router as documents_router
from .api.criteria import router as criteria_router
from .api.evidence import router as evidence_router
from .api.audit import router as audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite tables and seed metadata
    init_db()
    
    # 2. Ingest / load processed chunks
    chunks_file = os.path.join(settings.PROCESSED_DIR, "chunks.json")
    if not os.path.exists(chunks_file):
        print("[ACCREDIA] Processing institutional PDF/DOCX repository...")
        chunks = ingestion_service.ingest_all()
    else:
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
    vector_store.build_index(chunks)
    print(f"[ACCREDIA] Loaded and indexed {len(chunks)} chunks across {len(vector_store.documents)} institutional documents.")

    # 3. Seed demo evidence search if database is empty
    existing = list_all_investigations()
    if not existing:
        print("[ACCREDIA] Seeding initial baseline accreditation evidence search...")
        try:
            investigation_service.investigate("What evidence exists for faculty development activities in 2024-25?")
            print("[ACCREDIA] Baseline search seeded successfully.")
        except Exception as e:
            print(f"[ACCREDIA] Warning during seed: {e}")
            
    yield
    print("[ACCREDIA] System shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    description=f"{settings.APP_SUBTITLE} — {settings.TAGLINE}",
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount API routers
app.include_router(research_router, prefix="/api", tags=["Research, Dashboard & Health"])
app.include_router(investigations_router, prefix="/api", tags=["Accreditation Evidence Search"])
app.include_router(documents_router, prefix="/api", tags=["Institutional Documents"])
app.include_router(criteria_router, prefix="/api", tags=["Accreditation Criteria & Gaps"])
app.include_router(evidence_router, prefix="/api", tags=["Accreditation Evidence Repository"])
app.include_router(audit_router, prefix="/api", tags=["Audit Trail"])

@app.get("/")
def root():
    return {
        "system": settings.APP_NAME,
        "subtitle": settings.APP_SUBTITLE,
        "tagline": settings.TAGLINE,
        "institution": settings.INSTITUTION_NAME,
        "short_name": settings.INSTITUTION_SHORT,
        "location": settings.INSTITUTION_LOCATION,
        "status": "operational",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
