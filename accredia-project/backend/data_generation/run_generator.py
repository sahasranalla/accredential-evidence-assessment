import os
import sys
import json

# Ensure parent directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, PROJECT_DIR)

from backend.data_generation.documents_data import DOCUMENTS
from backend.data_generation.pdf_generator import (
    build_pdf_document, build_docx_document,
    DOCS_DIR, METADATA_DIR, TEST_QUERIES_DIR,
    CRITERIA, DEPARTMENTS, INSTITUTION_NAME
)

EVIDENCE_GAPS = [
    {
        "gap_id": "GAP-001",
        "criterion": "Criterion 6",
        "subcriterion": "6.3 Faculty Empowerment",
        "topic": "Faculty participation in international training programs during 2025-26",
        "current_evidence_count": 0,
        "suggested_documents": [
            "Faculty International Training Register 2025-26",
            "International Travel Grant Sanction Orders",
            "Foreign University Collaboration Certificates",
            "IQAC Activity Report 2025-26"
        ],
        "priority": "HIGH",
        "reason": "The repository currently has training data for 2022-23, 2023-24, and 2024-25, but no records of international training programs for 2025-26."
    },
    {
        "gap_id": "GAP-002",
        "criterion": "Criterion 5",
        "subcriterion": "5.4 Alumni Engagement",
        "topic": "Alumni endowment fund for robotics and autonomous vehicles laboratory",
        "current_evidence_count": 0,
        "suggested_documents": [
            "Alumni Endowment Deed & Agreement",
            "Dedicated Bank Statements of Alumni Trust",
            "Laboratory Equipment Invoices funded by Alumni"
        ],
        "priority": "MEDIUM",
        "reason": "General alumni scholarships exist, but dedicated endowment records for specialized robotics lab funding are not documented."
    },
    {
        "gap_id": "GAP-003",
        "criterion": "Criterion 7",
        "subcriterion": "7.1 Environmental Responsibility",
        "topic": "Third-party comprehensive energy audit certification for 2025-26",
        "current_evidence_count": 0,
        "suggested_documents": [
            "BEE Certified Energy Auditor Official Report 2025-26",
            "Electrical Safety and Carbon Offset Certificate"
        ],
        "priority": "HIGH",
        "reason": "Internal solar power reports exist for 2024-25, but an external third-party energy audit for 2025-26 has not been submitted."
    },
    {
        "gap_id": "GAP-004",
        "criterion": "Criterion 3",
        "subcriterion": "3.1 Resource Mobilization for Research",
        "topic": "Industry-sponsored research grants exceeding 1 Crore for green hydrogen technology",
        "current_evidence_count": 0,
        "suggested_documents": [
            "Sponsored Research Grant Agreement",
            "Sanction Letter from Industry Partner",
            "Fund Utilization Certificate"
        ],
        "priority": "MEDIUM",
        "reason": "The institution has government grants and consulting, but large-scale industry-funded green hydrogen research is unverified."
    },
    {
        "gap_id": "GAP-005",
        "criterion": "Criterion 3",
        "subcriterion": "3.2 Innovation Ecosystem",
        "topic": "Patent licensing revenue distribution for commercialized biotech products",
        "current_evidence_count": 0,
        "suggested_documents": [
            "Technology Transfer Licensing Agreement",
            "Royalty Distribution Ledgers",
            "Commercialization Statements"
        ],
        "priority": "LOW",
        "reason": "Agricultural and drone patents were licensed, but no records exist for commercialized biotech products."
    }
]

CONTRADICTIONS = [
    {
        "contradiction_id": "CONTRAD-FDP-PARTICIPANTS",
        "topic": "Faculty Development Participation Count in 2024-25",
        "source_a_id": "DOC-ACCR-003",
        "source_a_title": "Faculty Development Report 2024-25",
        "source_a_claim": "The institution conducted 18 faculty development programs during 2024-25, with 126 faculty participation records.",
        "source_a_page": 6,
        "source_a_status": "active",
        "source_b_id": "DOC-ACCR-004",
        "source_b_title": "Draft Annual Institutional Report 2024-25 (Internal Working Draft)",
        "source_b_claim": "Preliminary training attendance recorded 118 faculty participants across initial FDP cohorts prior to mid-term consolidation.",
        "source_b_page": 2,
        "source_b_status": "superseded",
        "conflict_analysis": "Source DOC-ACCR-004 is an internal working draft created in February 2025 before final Q4 training reconciliation. Source DOC-ACCR-003 is the official audited report approved in May 2025 documenting the full 126 participants.",
        "confidence_impact": -0.05
    }
]

EVALUATION_QUERIES = [
    {
        "id": 1,
        "query": "What evidence exists for faculty development activities?",
        "expected_criteria": ["Criterion 6"],
        "expected_docs": ["DOC-ACCR-003", "DOC-ACCR-001", "DOC-ACCR-002"],
        "has_evidence": True,
        "target_page": 6,
        "key_phrase": "18 faculty development programs during 2024-25, with 126 faculty participation records"
    },
    {
        "id": 2,
        "query": "How many faculty development programs were conducted in 2024-25?",
        "expected_criteria": ["Criterion 6"],
        "expected_docs": ["DOC-ACCR-003", "DOC-ACCR-001", "DOC-ACCR-002"],
        "has_evidence": True,
        "target_page": 6,
        "key_phrase": "18 faculty development programs"
    },
    {
        "id": 3,
        "query": "Show evidence of research publications.",
        "expected_criteria": ["Criterion 3"],
        "expected_docs": ["DOC-ACCR-005", "DOC-ACCR-001"],
        "has_evidence": True,
        "target_page": 8,
        "key_phrase": "142 research papers in Scopus and Web of Science"
    },
    {
        "id": 4,
        "query": "What evidence supports Criterion 3?",
        "expected_criteria": ["Criterion 3"],
        "expected_docs": ["DOC-ACCR-005", "DOC-ACCR-020", "DOC-ACCR-021"],
        "has_evidence": True,
        "target_page": 1,
        "key_phrase": "Research, Innovation & Incubation"
    },
    {
        "id": 5,
        "query": "What evidence exists for student scholarships?",
        "expected_criteria": ["Criterion 5"],
        "expected_docs": ["DOC-ACCR-024"],
        "has_evidence": True,
        "target_page": 4,
        "key_phrase": "1,120 students benefited from government and institutional scholarships"
    },
    {
        "id": 6,
        "query": "Show evidence of placement activities.",
        "expected_criteria": ["Criterion 5"],
        "expected_docs": ["DOC-ACCR-006", "DOC-ACCR-046"],
        "has_evidence": True,
        "target_page": 2,
        "key_phrase": "88.4% of eligible students secured confirmed job offers"
    },
    {
        "id": 7,
        "query": "What evidence exists for industry collaboration?",
        "expected_criteria": ["Criterion 3"],
        "expected_docs": ["DOC-ACCR-021", "DOC-ACCR-007"],
        "has_evidence": True,
        "target_page": 4,
        "key_phrase": "28 active corporate Memorandums of Understanding"
    },
    {
        "id": 8,
        "query": "What evidence exists for extension activities?",
        "expected_criteria": ["Criterion 3"],
        "expected_docs": ["DOC-ACCR-011", "DOC-ACCR-012"],
        "has_evidence": True,
        "target_page": 3,
        "key_phrase": "24 extension and outreach activities"
    },
    {
        "id": 9,
        "query": "Which documents support student mentoring?",
        "expected_criteria": ["Criterion 5"],
        "expected_docs": ["DOC-ACCR-023"],
        "has_evidence": True,
        "target_page": 2,
        "key_phrase": "mentor-to-mentee ratio of 1:18"
    },
    {
        "id": 10,
        "query": "Show evidence for green campus initiatives.",
        "expected_criteria": ["Criterion 7"],
        "expected_docs": ["DOC-ACCR-025"],
        "has_evidence": True,
        "target_page": 3,
        "key_phrase": "45% verified green cover comprising 2,400 geo-tagged trees"
    },
    {
        "id": 11,
        "query": "What evidence exists for energy conservation?",
        "expected_criteria": ["Criterion 7"],
        "expected_docs": ["DOC-ACCR-026"],
        "has_evidence": True,
        "target_page": 3,
        "key_phrase": "250 kW grid-connected rooftop solar photovoltaic power plant"
    },
    {
        "id": 12,
        "query": "Which documents mention faculty research?",
        "expected_criteria": ["Criterion 3"],
        "expected_docs": ["DOC-ACCR-005", "DOC-ACCR-043"],
        "has_evidence": True,
        "target_page": 1,
        "key_phrase": "seed money was disbursed to 14 young faculty investigators"
    },
    {
        "id": 13,
        "query": "What evidence exists for student feedback?",
        "expected_criteria": ["Criterion 1"],
        "expected_docs": ["DOC-ACCR-008", "DOC-ACCR-009"],
        "has_evidence": True,
        "target_page": 3,
        "key_phrase": "overall positive rating of 91.2%"
    },
    {
        "id": 14,
        "query": "Show evidence of academic audits.",
        "expected_criteria": ["Criterion 6"],
        "expected_docs": ["DOC-ACCR-019", "DOC-ACCR-002"],
        "has_evidence": True,
        "target_page": 4,
        "key_phrase": "external peer review committee members from Osmania University"
    },
    {
        "id": 15,
        "query": "What evidence exists for curriculum review?",
        "expected_criteria": ["Criterion 1"],
        "expected_docs": ["DOC-ACCR-017"],
        "has_evidence": True,
        "target_page": 4,
        "key_phrase": "Autonomous R22 curriculum framework"
    },
    {
        "id": 16,
        "query": "Show evidence of alumni engagement.",
        "expected_criteria": ["Criterion 5"],
        "expected_docs": ["DOC-ACCR-010"],
        "has_evidence": True,
        "target_page": 2,
        "key_phrase": "4 regional chapter reunions in Hyderabad, Bengaluru"
    },
    {
        "id": 17,
        "query": "What evidence exists for innovation activities?",
        "expected_criteria": ["Criterion 3"],
        "expected_docs": ["DOC-ACCR-005", "DOC-ACCR-020"],
        "has_evidence": True,
        "target_page": 14,
        "key_phrase": "VITEC Innovation Hub (VIH) incubated 8 new student-led technology startups"
    },
    {
        "id": 18,
        "query": "Which evidence supports faculty empowerment?",
        "expected_criteria": ["Criterion 6"],
        "expected_docs": ["DOC-ACCR-003", "DOC-ACCR-001"],
        "has_evidence": True,
        "target_page": 6,
        "key_phrase": "126 faculty participation records"
    },
    {
        "id": 19,
        "query": "What evidence exists for institutional best practices?",
        "expected_criteria": ["Criterion 7"],
        "expected_docs": ["DOC-ACCR-028"],
        "has_evidence": True,
        "target_page": 2,
        "key_phrase": "Project-Based Community Innovation"
    },
    {
        "id": 20,
        "query": "Which accreditation areas currently have evidence gaps?",
        "expected_criteria": ["Criterion 6", "Criterion 5", "Criterion 7", "Criterion 3"],
        "expected_docs": [],
        "has_evidence": False,
        "is_gap_query": True,
        "key_phrase": "Faculty international training programs during 2025-26"
    },
    {
        "id": 21,
        "query": "What evidence exists for faculty international training programs in 2025-26?",
        "expected_criteria": ["Criterion 6"],
        "expected_docs": [],
        "has_evidence": False,
        "is_gap_query": True,
        "key_phrase": "INSUFFICIENT EVIDENCE"
    },
    {
        "id": 22,
        "query": "Show evidence of alumni endowment funding for robotics and autonomous vehicles laboratory.",
        "expected_criteria": ["Criterion 5"],
        "expected_docs": [],
        "has_evidence": False,
        "is_gap_query": True,
        "key_phrase": "INSUFFICIENT EVIDENCE"
    }
]

def main():
    print(f"[ACCREDIA] Generating 50 institutional documents for {INSTITUTION_NAME}...")
    
    # 1. Generate PDFs
    for idx, doc in enumerate(DOCUMENTS):
        pdf_path = build_pdf_document(doc)
        if idx % 10 == 0 or idx == len(DOCUMENTS) - 1:
            print(f"  [PDF {idx+1}/{len(DOCUMENTS)}] Generated {os.path.basename(pdf_path)}")

    # 2. Generate sample DOCX
    docx_doc = next(d for d in DOCUMENTS if d["document_id"] == "DOC-ACCR-034")
    docx_path = build_docx_document(docx_doc)
    print(f"  [DOCX] Generated sample Word document: {os.path.basename(docx_path)}")

    # 3. Save metadata files
    with open(os.path.join(METADATA_DIR, "documents.json"), "w", encoding="utf-8") as f:
        json.dump(DOCUMENTS, f, indent=2)

    with open(os.path.join(METADATA_DIR, "criteria.json"), "w", encoding="utf-8") as f:
        json.dump(CRITERIA, f, indent=2)

    with open(os.path.join(METADATA_DIR, "departments.json"), "w", encoding="utf-8") as f:
        json.dump(DEPARTMENTS, f, indent=2)

    with open(os.path.join(METADATA_DIR, "evidence_gaps.json"), "w", encoding="utf-8") as f:
        json.dump(EVIDENCE_GAPS, f, indent=2)

    with open(os.path.join(METADATA_DIR, "contradictions.json"), "w", encoding="utf-8") as f:
        json.dump(CONTRADICTIONS, f, indent=2)

    with open(os.path.join(TEST_QUERIES_DIR, "evaluation_queries.json"), "w", encoding="utf-8") as f:
        json.dump(EVALUATION_QUERIES, f, indent=2)

    print("[ACCREDIA] Dataset generation completed successfully.")

if __name__ == "__main__":
    main()
