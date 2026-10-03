import os
import json
import re
import numpy as np
from typing import List, Dict, Any, Optional
from .embeddings import embedding_service
from ..config import settings

class VectorStore:
    """
    Hybrid Accreditation Vector & Keyword Store.
    Stores and indexes extracted PDF/DOCX chunks.
    Combines:
    - Dense Semantic Embedding Similarity via FAISS (all-MiniLM-L6-v2)
    - BM25 / Keyword Lexical Relevance with Phrase & Number Boosts
    - Accreditation Criterion Relevancy
    - Institutional Metadata Weighting (Academic Year, Department)
    """
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.chunk_map: Dict[str, Dict[str, Any]] = {}
        self.doc_map: Dict[str, List[Dict[str, Any]]] = {}
        self.vectors: Optional[np.ndarray] = None
        self._faiss_index = None
        self._has_faiss = False

        try:
            import faiss
            self._faiss = faiss
            self._has_faiss = True
        except ImportError:
            self._faiss = None
            self._has_faiss = False

    def _ensure_indexed(self):
        if not self.chunks:
            chunks_file = os.path.join(settings.PROCESSED_DIR, "chunks.json")
            if os.path.exists(chunks_file):
                with open(chunks_file, "r", encoding="utf-8") as f:
                    chunks = json.load(f)
                self.build_index(chunks)

    def build_index(self, chunks: List[Dict[str, Any]]):
        self.chunks = chunks
        self.chunk_map = {c["chunk_id"]: c for c in chunks}
        
        # Group by document
        self.doc_map = {}
        for c in chunks:
            doc_id = c.get("document_id", "DOC-UNKNOWN")
            if doc_id not in self.doc_map:
                self.doc_map[doc_id] = []
            self.doc_map[doc_id].append(c)

        # Build corpus for embedding
        corpus = [
            f"{c.get('document_name', '')} {c.get('criterion', '')} {c.get('subcriterion', '')} "
            f"{c.get('section', '')} {c.get('department', '')} {c.get('academic_year', '')} "
            f"{c.get('text', '')} {' '.join(c.get('keywords', []))}"
            for c in chunks
        ]

        embedding_service.fit_or_init(corpus)
        self.vectors = embedding_service.encode(corpus).astype(np.float32)

        if self._has_faiss and len(self.vectors) > 0:
            dim = self.vectors.shape[1]
            self._faiss_index = self._faiss.IndexFlatIP(dim)
            self._faiss_index.add(self.vectors)
            print(f"[ACCREDIA VectorStore] FAISS index built with {len(chunks)} chunks (dim={dim}).")
        else:
            print(f"[ACCREDIA VectorStore] Vector store initialized with {len(chunks)} chunks.")

    @staticmethod
    def _tokens(text: str) -> set:
        return {
            t for t in re.findall(r"[a-zA-Z0-9_-]+", (text or "").lower())
            if len(t) > 2
        }

    def _lexical_score(self, query: str, chunk: Dict[str, Any]) -> float:
        q = self._tokens(query)
        if not q:
            return 0.0

        title = str(chunk.get("document_name", ""))
        section = str(chunk.get("section", ""))
        content = str(chunk.get("text", ""))
        searchable = " ".join([
            title,
            section,
            str(chunk.get("department", "")),
            str(chunk.get("criterion", "")),
            str(chunk.get("subcriterion", "")),
            content,
            " ".join(chunk.get("keywords", []))
        ])

        d = self._tokens(searchable)
        overlap = len(q & d) / max(1, len(q))
        
        # Title and Section overlap bonuses
        title_tokens = self._tokens(title) | self._tokens(section)
        title_overlap = len(q & title_tokens) / max(1, len(q))

        # N-gram phrase boosting
        phrase_boost = 0.0
        q_words = [w for w in re.findall(r"[a-zA-Z0-9_-]+", query.lower()) if len(w) > 2]
        if len(q_words) >= 2:
            for n in (3, 2):
                for i in range(len(q_words) - n + 1):
                    phrase = " ".join(q_words[i:i+n])
                    if phrase in searchable.lower():
                        phrase_boost += 0.12 if n == 3 else 0.08

        # Numeric and metric bonus (e.g. "18", "126", "88.4%", "250 kW")
        q_numbers = set(re.findall(r"\d+(?:\.\d+)?%?", query.lower()))
        d_numbers = set(re.findall(r"\d+(?:\.\d+)?%?", searchable.lower()))
        number_boost = 0.15 if (q_numbers & d_numbers) else 0.0

        return min(1.0, (overlap * 0.50) + (title_overlap * 0.25) + min(0.15, phrase_boost) + number_boost)

    def _criterion_score(self, query: str, chunk: Dict[str, Any]) -> float:
        q_lower = query.lower()
        chunk_crit = str(chunk.get("criterion", "")).lower()
        chunk_sub = str(chunk.get("subcriterion", "")).lower()

        # Criterion explicit mentions e.g. "criterion 3", "criterion 6"
        crit_match = re.search(r"criterion\s*(\d)", q_lower)
        if crit_match:
            c_num = crit_match.group(1)
            if f"criterion {c_num}" in chunk_crit:
                return 1.0

        # Criterion keywords
        crit_keywords = {
            "criterion 1": ["curriculum", "syllabus", "curricular", "elective", "feedback", "bos"],
            "criterion 2": ["teaching", "learning", "student", "faculty profile", "evaluation", "exam", "co-po", "attainment", "satisfaction", "diversity", "workload"],
            "criterion 3": ["research", "publication", "scopus", "grant", "seed money", "patent", "innovation", "startup", "extension", "nss", "mou", "consultancy"],
            "criterion 4": ["infrastructure", "library", "koha", "book", "journal", "ict", "wifi", "bandwidth", "smart classroom", "laboratory", "maintenance"],
            "criterion 5": ["placement", "internship", "scholarship", "financial aid", "mentoring", "proctor", "alumni", "sports", "cultural", "ragging", "grievance"],
            "criterion 6": ["governance", "iqac", "audit", "fdp", "faculty development", "training", "empowerment", "budget", "finance", "strategic plan", "policy"],
            "criterion 7": ["green campus", "solar", "energy", "waste", "environment", "distinctiveness", "best practice", "gender", "icc", "sustainability"]
        }

        matched_weight = 0.0
        for crit_key, terms in crit_keywords.items():
            if any(term in q_lower for term in terms):
                if crit_key in chunk_crit:
                    matched_weight = max(matched_weight, 0.85)

        return matched_weight

    def _metadata_score(self, query: str, chunk: Dict[str, Any]) -> float:
        score = 0.0
        q_lower = query.lower()
        # Academic year match
        chunk_yr = chunk.get("academic_year", "")
        if chunk_yr and chunk_yr.lower() in q_lower:
            score += 0.50
        elif any(yr in q_lower for yr in ["2024-25", "2023-24", "2022-23", "2025-26"]):
            # Query specifies a different year than this chunk
            score -= 0.20

        # Department match
        dept = chunk.get("department", "").lower()
        if dept and dept in q_lower:
            score += 0.30

        return max(0.0, min(1.0, score))

    def search(
        self,
        query: str,
        top_k: int = 10,
        academic_year: Optional[str] = None,
        criterion: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        self._ensure_indexed()
        if not self.chunks or self.vectors is None:
            return []

        q_vec = embedding_service.encode([query]).astype(np.float32)

        # Semantic retrieval via FAISS or cosine similarity
        if self._has_faiss and self._faiss_index is not None:
            scores, indices = self._faiss_index.search(q_vec, len(self.chunks))
            semantic_pairs = [
                (self.chunks[idx], float(scores[0][i]))
                for i, idx in enumerate(indices[0]) if idx != -1 and idx < len(self.chunks)
            ]
        else:
            sims = np.dot(self.vectors, q_vec.T).flatten()
            semantic_pairs = [
                (self.chunks[idx], float(sims[idx]))
                for idx in np.argsort(-sims)
            ]

        candidates = []
        for chunk, semantic in semantic_pairs:
            # Apply Filters
            if academic_year and academic_year != "All" and chunk.get("academic_year") != academic_year:
                continue
            if criterion and criterion != "All" and chunk.get("criterion") != criterion:
                continue
            if department and department != "All" and chunk.get("department") != department:
                continue

            lexical = self._lexical_score(query, chunk)
            crit_score = self._criterion_score(query, chunk)
            meta_score = self._metadata_score(query, chunk)

            # Hybrid scoring formula
            final_score = (
                (0.55 * max(0.0, semantic)) +
                (0.25 * lexical) +
                (0.10 * meta_score) +
                (0.10 * crit_score)
            )

            res = dict(chunk)
            res["score"] = round(float(min(1.0, final_score)), 4)
            res["_semantic_score"] = round(float(semantic), 4)
            res["_lexical_score"] = round(float(lexical), 4)
            res["_criterion_score"] = round(float(crit_score), 4)
            res["_metadata_score"] = round(float(meta_score), 4)
            candidates.append(res)

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:top_k]

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        return self.chunk_map.get(chunk_id)

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        return self.doc_map.get(document_id, [])

    @property
    def documents(self) -> List[Dict[str, Any]]:
        """Returns unique documents list with page counts and summary metadata."""
        self._ensure_indexed()
        docs = []
        for doc_id, c_list in self.doc_map.items():
            if not c_list:
                continue
            first = c_list[0]
            max_page = max(c.get("page", 1) for c in c_list)
            docs.append({
                "document_id": doc_id,
                "title": first.get("document_name", doc_id),
                "academic_year": first.get("academic_year", "2024-25"),
                "criterion": first.get("criterion", "Criterion 6"),
                "subcriterion": first.get("subcriterion", ""),
                "department": first.get("department", "IQAC"),
                "document_type": first.get("document_type", "Institutional Report"),
                "source": first.get("source", ""),
                "author": first.get("author", ""),
                "status": first.get("status", "active"),
                "pages": max_page,
                "chunks_count": len(c_list),
                "summary": first.get("summary", ""),
                "keywords": first.get("keywords", [])
            })
        return sorted(docs, key=lambda d: d.get("document_id", ""))

vector_store = VectorStore()
