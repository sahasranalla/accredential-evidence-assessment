import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = "ACCREDIA"
    APP_SUBTITLE: str = "AI-Powered Accreditation Evidence Assistant"
    TAGLINE: str = "Find. Verify. Explain. Every piece of accreditation evidence."
    VERSION: str = "2.0.0"
    
    # Institution Profile
    INSTITUTION_NAME: str = "Vidyapath Institute of Technology"
    INSTITUTION_SHORT: str = "VITEC"
    INSTITUTION_LOCATION: str = "Hyderabad, Telangana, India"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data", "accreditation")
    DOCS_DIR: str = os.path.join(DATA_DIR, "documents")
    METADATA_DIR: str = os.path.join(DATA_DIR, "metadata")
    PROCESSED_DIR: str = os.path.join(DATA_DIR, "processed")
    DB_PATH: str = os.path.join(BASE_DIR, "accredia.db")
    VECTOR_CACHE_DIR: str = os.path.join(BASE_DIR, ".cache_vectors")
    
    # LLM Settings
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
    
    # Accreditation Search thresholds
    MAX_SEARCH_DEPTH: int = int(os.getenv("MAX_SEARCH_DEPTH", "4"))
    MIN_EVIDENCE_SCORE: float = float(os.getenv("MIN_EVIDENCE_SCORE", "0.20"))
    CONFIDENCE_THRESHOLD_HIGH: float = 0.82
    CONFIDENCE_THRESHOLD_MED: float = 0.60
    
    @property
    def is_local_mode(self) -> bool:
        return not bool(self.LLM_API_KEY and self.LLM_API_KEY.strip())

settings = Settings()
