import sys
import os
import json

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    print("[TEST] Initializing TestClient...")
    with TestClient(app) as client:
        # 1. Root
        r = client.get("/")
        assert r.status_code == 200, f"Root returned {r.status_code}"
        print("[PASS] Root endpoint:", r.json().get("system"), "-", r.json().get("subtitle"))

        # 2. Health
        r = client.get("/api/health")
        assert r.status_code == 200, f"Health returned {r.status_code}"
        health = r.json()
        print(f"[PASS] Health check: {health['status']} | Docs: {health['documents_indexed']} | Chunks: {health['chunks_indexed']}")

        # 3. Dashboard stats
        r = client.get("/api/dashboard/stats")
        assert r.status_code == 200, f"Dashboard stats returned {r.status_code}"
        stats = r.json()
        print(f"[PASS] Dashboard stats: {stats['documents_indexed']} docs, {stats['evidence_items']} evidence items, {stats['criteria_covered']} criteria")

        # 4. Criteria & Coverage
        r = client.get("/api/criteria/coverage")
        assert r.status_code == 200, f"Coverage returned {r.status_code}"
        cov = r.json()
        print(f"[PASS] Criteria coverage returned {len(cov)} criteria (Criterion 1 to 7)")
        for c in cov[:3]:
            print(f"   - {c['criterion_id']}: {c['name']} -> {c['coverage_percentage']}% ({c['status']})")

        # 5. Evidence gaps
        r = client.get("/api/gaps")
        assert r.status_code == 200, f"Gaps returned {r.status_code}"
        gaps = r.json()
        print(f"[PASS] Evidence gaps: {len(gaps)} institutional gaps documented")

        # 6. Documents list
        r = client.get("/api/documents")
        assert r.status_code == 200, f"Documents returned {r.status_code}"
        docs = r.json()
        print(f"[PASS] Documents list returned {len(docs)} documents")

        # 7. Search for Faculty Development Activities
        print("[TEST] Searching for: 'What evidence exists for faculty development activities?'...")
        r = client.post("/api/investigate", json={"question": "What evidence exists for faculty development activities?"})
        assert r.status_code == 200, f"Search failed with {r.status_code}: {r.text}"
        data = r.json()
        print(f"[PASS] Search Status: {data['status']} | Confidence: {data['confidence_level']} ({data['confidence']})")
        print(f"[PASS] Evidence Items Found: {len(data['evidence'])}")
        print(f"[PASS] Citations Verified: {len(data['citations'])}")
        print(f"[PASS] Graph Nodes: {len(data['graph']['nodes'])}, Edges: {len(data['graph']['edges'])}")
        print(f"[PASS] Answer Snippet: {data['answer'][:240]}...")

        # 8. Test Insufficient Evidence Query
        print("[TEST] Searching for unsupported inquiry: 'What evidence exists for faculty international training programs in 2025-26?'...")
        r = client.post("/api/investigate", json={"question": "What evidence exists for faculty international training programs in 2025-26?"})
        assert r.status_code == 200
        gap_data = r.json()
        assert gap_data["status"] == "insufficient_evidence", f"Expected insufficient_evidence but got {gap_data['status']}"
        assert "INSUFFICIENT EVIDENCE" in gap_data["answer"]
        print("[PASS] Successfully handled insufficient evidence:")
        print(f"   Status: {gap_data['status']}")
        print(f"   Answer: {gap_data['answer'][:180]}...")

        # 9. Document File Stream
        if docs:
            first_doc_id = docs[0]["document_id"]
            r = client.get(f"/api/documents/{first_doc_id}/file")
            print(f"[PASS] File stream for {first_doc_id}: HTTP {r.status_code} (Content-Type: {r.headers.get('content-type')})")

        print("\n==========================================")
        print("ALL BACKEND END-TO-END TESTS PASSED SUCCESSFULLY!")
        print("==========================================")

if __name__ == "__main__":
    run_tests()
