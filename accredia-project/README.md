# ACCREDIA — AI-Powered Accreditation Evidence Assistant
> **Challenge JIG26_21: Accreditation Evidence Assistant**  
> *"Find. Verify. Explain. Every piece of accreditation evidence."*

---

## 🏛️ Executive Summary

**ACCREDIA** is an autonomous accreditation intelligence platform designed for higher education institutions preparing for **NAAC / NBA** accreditation cycles. Built for **Vidyapath Institute of Technology (VITEC)**, Hyderabad, ACCREDIA transforms disparate institutional archives—academic council minutes, departmental audit reports, financial ledgers, and research sanction letters—into audit-ready, page-verified accreditation evidence.

Rather than relying on generic, ungrounded Large Language Models that risk fabricating academic metrics, ACCREDIA implements a **Strict Citation RAG Pipeline** paired with **FAISS Hybrid Retrieval**, **Automated Page Verification**, and **Institutional Contradiction & Gap Auditing**.

---

## 🚀 Key Highlights & Differentiators

| Capability | ACCREDIA Implementation | Industry Standard / Generic Chatbots |
|---|---|---|
| **Citation Verification** | **100% Page-Verified** against physical PDFs (`fitz` / `python-docx`) | Hallucinates non-existent documents / invalid pages |
| **Evidence Repository** | **51 Institutional Records** (50 Real PDFs + 1 DOCX) across AY 2022–26 | Dummy single-page text snippets |
| **Criteria Coverage** | Real-time tracking across all **NAAC Criteria 1 to 7** with weightages | Unstructured QA without accreditation framework |
| **Missing Evidence** | **Explicit `INSUFFICIENT EVIDENCE` Safeguard** with Gap Analysis | Fabricates answers when facts are missing |
| **Conflict Resolution** | Audits version conflicts (e.g. 126 vs 118 participants in AI workshop) | Confuses conflicting figures without audit basis |
| **Visual Evidence Tree** | Interactive **React Flow Hierarchical Graph** (Criterion → Doc → Page) | Flat plain text responses |
| **Execution Performance** | < 0.20s hybrid query latency with local FAISS indexing | Slow, rate-limited external API calls |

---

## 🏗️ Architecture & 7-Stage Pipeline

```text
User Accreditation Query (Natural Language)
                     │
                     ▼
[Stage 1] Query & Criterion Analyzer
  - Extracts Criterion (1–7), Subcriteria, Academic Year (2022–26), & Department
                     │
                     ▼
[Stage 2] Hybrid Retrieval & FAISS Dense Search
  - FAISS IndexFlatIP (Dense normalized sublinear TF-IDF + n-grams)
  - Lexical keyword matching + Criterion bonus scoring
                     │
                     ▼
[Stage 3] Passage Scoring & Threshold Filtering
  - Filters candidate passages with score ≥ 0.55
                     │
                     ▼
[Stage 4] Physical Citation Verifier
  - Confirms document exists in data/accreditation/documents/
  - Verifies cited page number is within physical document boundary [1, max_pages]
                     │
                     ▼
[Stage 5] Hierarchical Evidence Graph Assembly
  - Criterion Node → Subcriterion Node → Department Node → Document Node → Page Node
                     │
                     ▼
[Stage 6] Discrepancy & Gap Auditor
  - Checks for version superseding and claim contradictions
  - Identifies missing records and matches curated institutional gaps
                     │
                     ▼
[Stage 7] Grounded Evidence Dossier Synthesis
  - Synthesizes exact conclusion with page citations
  - OR returns INSUFFICIENT EVIDENCE with remediation steps
```

---

## 📂 Institutional Dataset (Vidyapath Institute of Technology)

The platform includes a realistic synthetic institutional corpus of **51 multi-page files** (50 PDFs + 1 DOCX) spanning 4 Academic Years (**2022–23**, **2023–24**, **2024–25**, and **2025–26**) and 14 academic/administrative units:

- **Criteria 1 (Curricular Aspects):** Board of Studies (BoS) minutes, Academic Council curriculum revisions, CBCS course handbooks, industry advisory feedback.
- **Criteria 2 (Teaching-Learning & Evaluation):** Departmental Student-to-Faculty Ratio (SFR) audits (e.g. CSE SFR 14.8:1), sanctioned faculty intake, CIA question bank moderation, academic calendars.
- **Criteria 3 (Research, Innovations & Extension):** Dean R&D seed grant sanction letters, Scopus/SCI journal publication catalogs, IEEE conference proceedings, MoUs.
- **Criteria 4 (Infrastructure & Learning Resources):** Central Library ILMS automation audit, subscription invoices, campus Wi-Fi bandwidth upgrade orders, sports facility logbooks.
- **Criteria 5 (Student Support & Progression):** Corporate Relations placement reports (88.4% placement, ₹7.2 LPA median), competitive exam coaching attendance, anti-ragging committee minutes.
- **Criteria 6 (Governance, Leadership & Management):** IQAC meeting minutes & Action Taken Reports (ATRs), statutory audit balance sheets, faculty professional development (FDP) grants.
- **Criteria 7 (Institutional Values & Best Practices):** Green audit certifications, rainwater harvesting capacity reports, gender equity action plans.

---

## 📊 Verification & Evaluation Results

Run the automated evaluation benchmark via:
```powershell
python backend/evaluation.py
```

### Benchmark Summary (22 Test Scenarios):
- **Total Queries Evaluated:** 22
- **Citations Checked:** 71
- **Citation Verification Rate:** **100.0%** (71 / 71 physically valid page citations)
- **Insufficient Evidence Accuracy:** **100.0%** (3 / 3 missing record queries correctly returned `INSUFFICIENT EVIDENCE`)
- **Contradiction Detection:** **100.0%** (Reconciled CSE AI Workshop Draft vs Final Report)
- **Average Retrieval & Verification Latency:** **0.14 seconds / query**

---

## 💻 Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLite (`accredia.db`), PyMuPDF (`fitz`), `python-docx`, ReportLab, `scikit-learn`, `faiss-cpu`.
- **Frontend:** React 18, Vite, Tailwind CSS, `@xyflow/react` (React Flow), Recharts, Lucide Icons, Axios.
- **Offline / Autonomous Ready:** Fully operational in local mode without requiring external LLM API keys.

---

## ⚡ Quick Start

### Option 1: One-Click Windows Launcher (Recommended)
Double-click `run_nexus.bat` or run:
```powershell
.\START_ACCREDIA.bat
```
This script automatically checks Python dependencies, verifies frontend modules, boots FastAPI backend on `http://127.0.0.1:8000`, starts Vite frontend on `http://127.0.0.1:5173`, and opens the browser.

---

### Option 2: Manual Setup

#### 1. Backend Setup
```powershell
# From project root
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health: `http://127.0.0.1:8000/api/health`
- Interactive Swagger API Docs: `http://127.0.0.1:8000/docs`

#### 2. Frontend Setup
```powershell
# In a separate terminal
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```
- Web Application: `http://127.0.0.1:5173`

---

## 🎯 Key Demo Queries to Explore

1. **Criterion 2 (Student-Faculty Ratio):**  
   *"Show student-to-faculty ratio for AY 2024-25 in CSE Department with signed committee minutes."*  
   *Verified finding: 14.8:1 verified on Page 1 of CSE Academic Audit Report.*

2. **Criterion 3 (Research Grants & Seed Funding):**  
   *"What are the seed research grants sanctioned in AY 2024-25 and list of journal publications?"*  
   *Verified finding: 8 faculty seed grants totaling ₹24.5 Lakhs verified in R&D Sanction Letter.*

3. **Criterion 6 (IQAC Minutes & Action Taken):**  
   *"Provide evidence of IQAC meetings and action taken reports conducted in 2024-25."*  
   *Verified finding: 4 statutory meetings on Page 1–2 of IQAC Annual Report.*

4. **Contradiction Audit Query:**  
   *"Verify participant count discrepancy between CSE AI Workshop reports."*  
   *Audited resolution: 126 participants (Official Report) vs 118 (superseded preliminary attendance draft).*

5. **Insufficient Evidence Safeguard:**  
   *"Provide audited greenhouse gas emissions and solar panel generation logs for 2021-22."*  
   *Returns `INSUFFICIENT EVIDENCE` without hallucination; highlights missing files and remediation actions.*

---

## 🛡️ License
Built for the JIG26_21 Accreditation Evidence Assistant Challenge.
All synthetic college documents, schemas, and verification pipelines are developed for educational and institutional evaluation purposes.
