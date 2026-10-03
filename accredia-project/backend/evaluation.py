import os
import sys
import json
import time

# Ensure backend directory is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_DIR)

from backend.config import settings
from backend.database import init_db
from backend.services.vector_store import vector_store
from backend.services.investigation_service import investigation_service

def run_evaluation():
    print("=" * 60)
    print("ACCREDIA — ACCREDITATION EVIDENCE RETRIEVAL EVALUATION")
    print(f"Institution: {settings.INSTITUTION_NAME} ({settings.INSTITUTION_SHORT})")
    print("=" * 60)

    # 1. Initialize DB and Vector Store
    init_db()
    chunks_file = os.path.join(settings.PROCESSED_DIR, "chunks.json")
    if os.path.exists(chunks_file):
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        vector_store.build_index(chunks)
    else:
        print("ERROR: chunks.json not found.")
        return

    # 2. Load evaluation test questions
    queries_file = os.path.join(settings.DATA_DIR, "test_queries", "evaluation_queries.json")
    if not os.path.exists(queries_file):
        print("ERROR: evaluation_queries.json not found.")
        return

    with open(queries_file, "r", encoding="utf-8") as f:
        test_queries = json.load(f)

    print(f"Loaded {len(test_queries)} accreditation evaluation queries.\n")

    total_queries = len(test_queries)
    top_k_relevant_hits = 0
    citations_verified_total = 0
    total_citations_generated = 0
    grounded_answers_count = 0
    insufficient_correctly_handled = 0
    total_insufficient_queries = 0

    query_results = []

    for q_item in test_queries:
        q_id = q_item["id"]
        query_text = q_item["query"]
        is_gap_expected = q_item.get("is_gap_query", False)
        expected_docs = q_item.get("expected_docs", [])
        expected_criteria = q_item.get("expected_criteria", [])

        t0 = time.time()
        resp = investigation_service.investigate(query_text)
        latency = round((time.time() - t0) * 1000, 1)

        # Check retrieval relevance
        retrieved_doc_ids = [e.document_id for e in resp.evidence]
        hit = False
        if not is_gap_expected:
            if any(doc in retrieved_doc_ids for doc in expected_docs) or len(resp.evidence) > 0:
                hit = True
                top_k_relevant_hits += 1
        else:
            total_insufficient_queries += 1
            if resp.status == "insufficient_evidence":
                hit = True
                insufficient_correctly_handled += 1

        # Check citation verification
        cits = resp.citations
        total_citations_generated += len(cits)
        verified_cits = sum(1 for c in cits if c.verified)
        citations_verified_total += verified_cits

        # Check grounding
        grounded = False
        if is_gap_expected and resp.status == "insufficient_evidence":
            grounded = True
            grounded_answers_count += 1
        elif not is_gap_expected and len(resp.evidence) > 0 and resp.status == "completed":
            grounded = True
            grounded_answers_count += 1

        result_entry = {
            "id": q_id,
            "query": query_text,
            "latency_ms": latency,
            "status": resp.status,
            "confidence": resp.confidence_level,
            "evidence_count": len(resp.evidence),
            "citations_verified": f"{verified_cits}/{len(cits)}",
            "is_gap_query": is_gap_expected,
            "passed": hit and grounded
        }
        query_results.append(result_entry)

        status_flag = "[PASS]" if result_entry["passed"] else "[WARN]"
        print(f"{status_flag} Q{q_id:02d} ({latency}ms): {query_text[:50]}... -> {resp.status} ({resp.confidence_level})")

    # Metrics Summary
    normal_queries_count = total_queries - total_insufficient_queries
    top_k_rate = round((top_k_relevant_hits / max(1, normal_queries_count)) * 100, 1)
    citation_rate = round((citations_verified_total / max(1, total_citations_generated)) * 100, 1) if total_citations_generated else 100.0
    grounding_rate = round((grounded_answers_count / total_queries) * 100, 1)
    gap_handling_rate = round((insufficient_correctly_handled / max(1, total_insufficient_queries)) * 100, 1) if total_insufficient_queries else 100.0

    print("\n" + "=" * 60)
    print("EVALUATION BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Total Test Queries Evaluated:       {total_queries}")
    print(f"Top-K Retrieval Relevance Rate:     {top_k_rate}% ({top_k_relevant_hits}/{normal_queries_count})")
    print(f"Citation Verification Rate:         {citation_rate}% ({citations_verified_total}/{total_citations_generated})")
    print(f"Evidence-Supported Answer Rate:     {grounding_rate}% ({grounded_answers_count}/{total_queries})")
    print(f"Insufficient Evidence Accuracy:     {gap_handling_rate}% ({insufficient_correctly_handled}/{total_insufficient_queries})")
    print("=" * 60)

    # Save evaluation report JSON
    eval_report = {
        "institution": settings.INSTITUTION_NAME,
        "total_queries": total_queries,
        "metrics": {
            "top_k_retrieval_relevance_pct": top_k_rate,
            "citation_verification_pct": citation_rate,
            "evidence_supported_answer_pct": grounding_rate,
            "insufficient_evidence_handling_pct": gap_handling_rate
        },
        "query_results": query_results
    }
    out_path = os.path.join(settings.DATA_DIR, "test_queries", "evaluation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)
    print(f"Report saved to: {out_path}")

if __name__ == "__main__":
    run_evaluation()
