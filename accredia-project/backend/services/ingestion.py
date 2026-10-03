import os
import re
import json
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
import docx

class DocumentIngestionService:
    """
    Real document ingestion pipeline supporting PDF and DOCX documents.
    Extracts text, detects pages, sections, headings, cleans text, chunks passages,
    and enriches with accreditation metadata (Criterion, Subcriterion, Academic Year, Department, Page, Section).
    """

    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            parent = os.path.dirname(base)
            p1 = os.path.join(parent, "data", "accreditation")
            p2 = os.path.join(base, "data", "accreditation")
            self.data_dir = p1 if os.path.exists(p1) else p2
        else:
            self.data_dir = data_dir

        self.docs_dir = os.path.join(self.data_dir, "documents")
        self.metadata_dir = os.path.join(self.data_dir, "metadata")
        self.processed_dir = os.path.join(self.data_dir, "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        self.metadata_catalog: Dict[str, Dict[str, Any]] = {}
        self._load_catalog()

    def _load_catalog(self):
        cat_file = os.path.join(self.metadata_dir, "documents.json")
        if os.path.exists(cat_file):
            with open(cat_file, "r", encoding="utf-8") as f:
                docs = json.load(f)
                self.metadata_catalog = {d["filename"]: d for d in docs}
                for d in docs:
                    self.metadata_catalog[d["document_id"]] = d

    def extract_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts text page-by-page from PDF with page numbers and section detection."""
        pages_content = []
        doc = fitz.open(file_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            text = page.get_text("text")

            # Clean text
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            cleaned_lines = []
            current_section = "General Overview"
            for line in lines:
                # Filter out header/footer lines from the canvas
                if "Vidyapath Institute of Technology" in line and "Accreditation" in line:
                    continue
                if "Internal Quality Assurance Cell" in line or "Confidential" in line or "Page " in line:
                    continue
                if line.startswith("Section ") and ":" in line:
                    current_section = line.split(":", 1)[1].strip()
                    continue
                cleaned_lines.append(line)

            page_text = " ".join(cleaned_lines)
            pages_content.append({
                "page": page_num,
                "text": page_text,
                "lines": cleaned_lines,
                "section": current_section
            })
        doc.close()
        return pages_content

    def extract_docx(self, file_path: str) -> List[Dict[str, Any]]:
        """Extracts text and headings from DOCX files."""
        doc = docx.Document(file_path)
        sections_data = []
        current_section = "General Overview"
        current_page = 1
        current_paras = []

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            if p.style.name.startswith("Heading"):
                if "Page " in text:
                    match = re.search(r"Page\s+(\d+)", text)
                    if match:
                        current_page = int(match.group(1))
                if ":" in text:
                    current_section = text.split(":", 1)[1].split("(")[0].strip()
                else:
                    current_section = text
            else:
                current_paras.append(text)

        full_text = " ".join(current_paras)
        return [{
            "page": current_page,
            "text": full_text,
            "lines": current_paras,
            "section": current_section
        }]

    def chunk_document(self, filename: str, file_path: str, doc_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits document pages into chunks with rich accreditation metadata."""
        chunks = []
        if filename.endswith(".pdf"):
            pages_data = self.extract_pdf(file_path)
        elif filename.endswith(".docx"):
            pages_data = self.extract_docx(file_path)
        else:
            return []

        doc_id = doc_meta.get("document_id", "DOC-UNKNOWN")
        doc_name = doc_meta.get("title", filename)
        academic_year = doc_meta.get("academic_year", "2024-25")
        criterion = doc_meta.get("criterion", "Criterion 6")
        subcriterion = doc_meta.get("subcriterion", "General")
        department = doc_meta.get("department", "IQAC")
        doc_type = doc_meta.get("document_type", "Institutional Report")
        status = doc_meta.get("status", "active")
        author = doc_meta.get("author", "")

        # Also get defined sections from metadata if available to ensure exact section matching
        meta_sections = {s["page_number"]: s for s in doc_meta.get("sections", [])}

        chunk_counter = 1
        for page_info in pages_data:
            page_num = page_info["page"]
            page_text = page_info["text"]

            # Prefer section from metadata if matching page exists
            if page_num in meta_sections:
                sec_title = meta_sections[page_num]["section_title"]
                sec_paragraphs = meta_sections[page_num].get("paragraphs", [])
            else:
                sec_title = page_info["section"]
                sec_paragraphs = [page_text]

            # Create primary chunk for the section
            if sec_paragraphs:
                for p_idx, para in enumerate(sec_paragraphs):
                    if len(para.strip()) < 20:
                        continue
                    chunk_id = f"CHK-{doc_id}-P{page_num}-{chunk_counter}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": doc_id,
                        "document_name": doc_name,
                        "title": doc_name,
                        "page": page_num,
                        "section": sec_title,
                        "academic_year": academic_year,
                        "criterion": criterion,
                        "subcriterion": subcriterion,
                        "department": department,
                        "document_type": doc_type,
                        "source": filename,
                        "author": author,
                        "status": status,
                        "text": para.strip(),
                        "excerpt": para.strip(),
                        "summary": doc_meta.get("summary", ""),
                        "keywords": doc_meta.get("keywords", [])
                    })
                    chunk_counter += 1
            elif page_text.strip():
                chunk_id = f"CHK-{doc_id}-P{page_num}-{chunk_counter}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "document_name": doc_name,
                    "title": doc_name,
                    "page": page_num,
                    "section": sec_title,
                    "academic_year": academic_year,
                    "criterion": criterion,
                    "subcriterion": subcriterion,
                    "department": department,
                    "document_type": doc_type,
                    "source": filename,
                    "author": author,
                    "status": status,
                    "text": page_text.strip(),
                    "excerpt": page_text.strip(),
                    "summary": doc_meta.get("summary", ""),
                    "keywords": doc_meta.get("keywords", [])
                })
                chunk_counter += 1

        return chunks

    def ingest_all(self) -> List[Dict[str, Any]]:
        """Processes all documents in data/accreditation/documents and saves chunks.json."""
        all_chunks = []
        if not os.path.exists(self.docs_dir):
            return []

        doc_files = [f for f in os.listdir(self.docs_dir) if f.endswith(".pdf") or f.endswith(".docx")]
        print(f"[INGESTION] Processing {len(doc_files)} files from {self.docs_dir}...")

        for fname in doc_files:
            fpath = os.path.join(self.docs_dir, fname)
            meta = self.metadata_catalog.get(fname)
            if not meta:
                # Infer metadata if not in catalog
                meta = {
                    "document_id": f"DOC-{fname[:12].upper()}",
                    "title": fname.replace("_", " ").replace(".pdf", "").title(),
                    "academic_year": "2024-25",
                    "criterion": "Criterion 6",
                    "department": "IQAC",
                    "document_type": "Institutional Report",
                    "status": "active"
                }

            doc_chunks = self.chunk_document(fname, fpath, meta)
            all_chunks.extend(doc_chunks)

        # Save processed chunks
        out_path = os.path.join(self.processed_dir, "chunks.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2)

        print(f"[INGESTION] Ingested and chunked {len(all_chunks)} chunks across {len(doc_files)} documents.")
        return all_chunks

ingestion_service = DocumentIngestionService()
