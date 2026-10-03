import re
import os
import json
from typing import Dict, Any, List

class QueryAnalyzer:
    """
    Accreditation Query Analyzer.
    Identifies accreditation criteria, subcriteria, academic years, departments,
    question types, and evidence gap queries from user input.
    """
    def __init__(self):
        self.criteria_keywords = {
            "Criterion 1": ["curriculum", "curricular", "syllabus", "board of studies", "bos", "feedback", "value-added", "elective", "cbcs", "academic flexibility", "academic council", "course outcome", "program outcome"],
            "Criterion 2": ["teaching", "learning", "student enrollment", "co-po", "attainment", "student satisfaction", "sss", "faculty profile", "ph.d", "cadre ratio", "workload", "remedial", "diversity", "student-to-faculty", "student faculty", "faculty ratio", "sfr", "student-faculty", "faculty-student", "faculty student", "mentor-mentee", "student teacher", "pass percentage", "continuous internal evaluation", "cie", "experiential learning"],
            "Criterion 3": ["research", "publication", "scopus", "citations", "patents", "ipr", "innovation", "incubation", "startups", "seed money", "seed grant", "grants", "extension", "outreach", "nss", "mou", "collaboration", "consultancy", "journal", "conference", "funded project", "workshop", "seminar"],
            "Criterion 4": ["infrastructure", "classrooms", "smart classroom", "laboratory", "library", "koha", "ilms", "e-learning", "e-resources", "ict", "wi-fi", "bandwidth", "maintenance", "computing", "automation", "books", "subscription", "sports complex", "gymnasium"],
            "Criterion 5": ["placement", "recruitment", "salary", "package", "internship", "scholarship", "financial aid", "mentoring", "proctor", "alumni", "sports", "cultural", "anti-ragging", "ragging", "grievance", "training", "higher education", "competitive exams", "gate", "gre", "cat"],
            "Criterion 6": ["governance", "iqac", "meeting minutes", "action taken", "atr", "faculty development", "fdp", "faculty empowerment", "academic audit", "audit", "financial audit", "budget", "strategic plan", "policy", "perspective plan", "welfare", "appraisal", "cas", "financial management"],
            "Criterion 7": ["green campus", "solar", "energy conservation", "waste management", "stp", "environment", "best practices", "distinctiveness", "gender equity", "icc", "values", "code of conduct", "audit report", "rainwater", "led", "sustainability"]
        }

    def analyze(self, question: str) -> Dict[str, Any]:
        q_lower = question.lower()

        # 1. Detect Academic Year
        academic_year = None
        yr_match = re.search(r"\b(202[1-6]-2[2-7]|202[1-6])\b", q_lower)
        if yr_match:
            academic_year = yr_match.group(0)
            if len(academic_year) == 4:
                # e.g. 2024 -> 2024-25
                y = int(academic_year)
                academic_year = f"{y}-{str(y+1)[2:]}"

        # 2. Detect Criteria
        matched_criteria = []
        crit_explicit = re.findall(r"criterion\s*(\d)", q_lower)
        for c in crit_explicit:
            c_tag = f"Criterion {c}"
            if c_tag not in matched_criteria:
                matched_criteria.append(c_tag)

        if not matched_criteria:
            for crit, kw_list in self.criteria_keywords.items():
                if any(kw in q_lower for kw in kw_list):
                    matched_criteria.append(crit)

        # 3. Detect Department
        dept_match = None
        departments = [
            ("IQAC", ["iqac", "quality cell", "quality assurance"]),
            ("Research Cell", ["research cell", "r&d", "research", "patent", "scopus"]),
            ("Academic Office", ["academic office", "academics", "curriculum", "bos", "syllabus"]),
            ("Training & Placement Cell", ["placement", "recruitment", "training & placement", "tpc", "internship"]),
            ("Student Affairs", ["student affairs", "scholarship", "mentoring", "alumni", "sports", "cultural", "nss"]),
            ("Library", ["library", "koha", "e-learning", "books", "journals"]),
            ("Examination Cell", ["examination", "exam", "pass percentage", "results"]),
            ("Administration", ["administration", "registrar", "governance", "audit", "financial audit"]),
            ("Estate Office", ["estate", "green campus", "solar", "energy", "waste", "maintenance"])
        ]
        for dept_name, triggers in departments:
            if any(t in q_lower for t in triggers):
                dept_match = dept_name
                break

        # 4. Check for Gap query
        is_gap_query = any(w in q_lower for w in [
            "gap", "gaps", "missing", "weak", "insufficient", "lacking", "what is missing", "what evidence is missing"
        ])

        # 5. Extract keywords
        stop_words = {
            "what", "which", "who", "when", "where", "why", "how", "did", "does", "do", "is", "are", "was", "were",
            "the", "a", "an", "of", "to", "for", "in", "on", "at", "during", "with", "from", "by", "and", "or",
            "show", "tell", "evidence", "documents", "document", "records", "record", "exist", "exists", "support",
            "supports", "supported", "please", "about"
        }
        raw_words = re.findall(r"[a-zA-Z0-9_-]+", q_lower)
        keywords = [w for w in raw_words if w not in stop_words and len(w) > 2]

        # 6. Question type
        q_type = "evidence_search"
        if is_gap_query:
            q_type = "gap_analysis"
        elif re.search(r"\bhow many\b|\bnumber of\b|\bcount\b", q_lower):
            q_type = "metric_count"
        elif re.search(r"\bwhich documents\b|\bwhat documents\b|\blist documents\b", q_lower):
            q_type = "document_lookup"
        elif re.search(r"\bcriterion \d\b", q_lower):
            q_type = "criterion_overview"

        topic = " ".join(keywords[:4]) if keywords else question

        return {
            "original_question": question,
            "topic": topic,
            "academic_year": academic_year,
            "matched_criteria": matched_criteria or ["Criterion 6"],
            "department": dept_match,
            "is_gap_query": is_gap_query,
            "question_type": q_type,
            "keywords": keywords,
            "search_goal": f"Retrieve verified institutional evidence for: {topic}"
        }

query_analyzer = QueryAnalyzer()
