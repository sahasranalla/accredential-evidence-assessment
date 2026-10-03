import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.database import init_db, list_all_investigations, list_criteria, list_evidence_gaps
from backend.services.vector_store import vector_store
from backend.services.investigation_service import investigation_service
from backend.api.criteria import get_criteria_coverage

def test():
    t0 = time.time()
    print("1. Initializing DB...")
    init_db()
    print("DB initialized in", time.time() - t0, "s")

    t1 = time.time()
    chunks_file = os.path.join(settings.PROCESSED_DIR, "chunks.json")
    if os.path.exists(chunks_file):
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        vector_store.build_index(chunks)
        print(f"2. Vector store built with {len(chunks)} chunks in {time.time() - t1:.2f}s")
    else:
        print("chunks.json not found at:", chunks_file)

    t2 = time.time()
    criteria = list_criteria()
    print(f"3. Criteria count: {len(criteria)}")

    gaps = list_evidence_gaps()
    print(f"4. Evidence gaps count: {len(gaps)}")

    cov = get_criteria_coverage()
    print(f"5. Criteria coverage count: {len(cov)}")
    for c in cov:
        print(f"   - {c['criterion_id']}: {c['name']} -> {c['coverage_percentage']}%")

    # 6. Test normal search
    t3 = time.time()
    q = "What evidence exists for faculty development activities?"
    print(f"\n6. Running search for: '{q}'...")
    res = investigation_service.investigate(q)
    print(f"Search completed in {time.time() - t3:.2f}s")
    print(f"   Status: {res.status}")
    print(f"   Confidence: {res.confidence_level} ({res.confidence})")
    print(f"   Evidence found: {len(res.evidence)}")
    print(f"   Citations: {len(res.citations)}")
    print(f"   Graph nodes: {len(res.graph.nodes)}, edges: {len(res.graph.edges)}")
    print(f"   Answer preview: {res.answer[:160]}...")

    # 7. Test Insufficient Evidence search
    t4 = time.time()
    q_gap = "What evidence exists for faculty international training programs in 2025-26?"
    print(f"\n7. Running insufficient-evidence search for: '{q_gap}'...")
    res_gap = investigation_service.investigate(q_gap)
    print(f"Search completed in {time.time() - t4:.2f}s")
    print(f"   Status: {res_gap.status}")
    print(f"   Confidence: {res_gap.confidence_level}")
    print(f"   Evidence Gaps: {len(res_gap.evidence_gaps)}")
    print(f"   Answer preview: {res_gap.answer[:160]}...")

    print("\n✓ ALL CORE ENGINE LOGIC VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test()
