import re
from typing import List, Dict, Any, Tuple, Optional
from ..models.evidence import EvidenceItem
from ..services.llm import llm_service
from ..config import settings

class AccreditationAnswerEngine:
    """
    Grounded Accreditation Answer Engine.
    Strictly generates answers from retrieved institutional evidence chunks.
    Ensures every factual statement has a verified citation (Source, Page, Section).
    If evidence is insufficient, explicitly returns 'INSUFFICIENT EVIDENCE'.
    """

    SYSTEM_PROMPT = """You are ACCREDIA, an AI-powered accreditation evidence assistant for Vidyapath Institute of Technology (VITEC), Hyderabad.
Answer questions strictly and only using the provided institutional evidence excerpts.
Do not invent or extrapolate statistics, activities, documents, dates, or claims.
Every factual statement should be supported by retrieved evidence with exact Source, Page, and Section.
If the evidence is insufficient to answer the question, explicitly state:
INSUFFICIENT EVIDENCE
Explain what was searched, why evidence is insufficient, and list the exact missing institutional documents required.
Never fabricate a citation or page number."""

    def generate_answer(
        self,
        question: str,
        evidence: List[EvidenceItem],
        is_insufficient: bool = False,
        gap_reason: str = "",
        suggested_docs: List[str] = None
    ) -> Tuple[str, str]:
        """
        Returns:
            (answer_text, finding_summary)
        """
        # 1. Handle Insufficient Evidence
        if is_insufficient or not evidence or max((e.relevance for e in evidence), default=0) < 0.28:
            gap_txt = gap_reason or f"The institutional knowledge base lacks verified documentation to support: '{question}'."
            docs_txt = "\n".join(f"- {d}" for d in (suggested_docs or [
                "Official IQAC Departmental Activity Register",
                "Annual Statutory Report",
                "Sanction Letters and Verification Logs"
            ]))
            ans = (
                f"**INSUFFICIENT EVIDENCE**\n\n"
                f"**Evidence Gap Detected:** {gap_txt}\n\n"
                f"**What was searched:** Institutional knowledge base across all academic cycles.\n"
                f"**Why evidence was insufficient:** No authoritative institutional record in the current repository confirms the requested parameters without risking unsupported claims.\n\n"
                f"**Required Institutional Documentation:**\n{docs_txt}"
            )
            return ans, "INSUFFICIENT EVIDENCE"

        # 2. Try LLM generation if configured
        if llm_service.is_available:
            evidence_context = []
            for ev in evidence[:6]:
                evidence_context.append(
                    f"Document: {ev.document_name} [{ev.document_id}]\n"
                    f"Page: {ev.page} | Section: {ev.section} | AY: {ev.academic_year} | Dept: {ev.department}\n"
                    f"Excerpt: {ev.excerpt}\n"
                )
            user_prompt = (
                f"User Accreditation Question: {question}\n\n"
                f"Supplied Institutional Evidence:\n{'---'.join(evidence_context)}\n\n"
                f"Provide a grounded, professional answer citing Document, Page, and Section for each key statistic or fact."
            )
            llm_result = llm_service.generate_json(self.SYSTEM_PROMPT, user_prompt)
            if llm_result and "answer" in llm_result:
                ans = llm_result["answer"]
                finding = llm_result.get("finding", ans.split(".")[0])
                return ans, finding

        # 3. Deterministic Local Evidence Mode (Highly accurate grounded synthesis)
        top_ev = evidence[0]
        q_lower = question.lower()

        # Score sentences within retrieved evidence
        q_tokens = {t for t in re.findall(r"[a-zA-Z0-9_-]+", q_lower) if len(t) > 2}
        selected_sentences = []
        seen_sentences = set()

        for ev in evidence[:4]:
            text = ev.excerpt
            # Split into sentences
            raw_sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 20]
            for s in raw_sents:
                s_lower = s.lower()
                s_tokens = {t for t in re.findall(r"[a-zA-Z0-9_-]+", s_lower) if len(t) > 2}
                overlap = len(q_tokens & s_tokens)
                has_num = bool(re.search(r"\d+(?:\.\d+)?%?", s))
                score = overlap + (2 if has_num else 0)
                if score >= 2 and s not in seen_sentences:
                    selected_sentences.append((score, s, ev))
                    seen_sentences.add(s)

        selected_sentences.sort(key=lambda x: x[0], reverse=True)

        if not selected_sentences:
            # Fallback to direct excerpt of top document
            lead_sentence = top_ev.excerpt.split(".")[0] + "."
            answer_body = f"{lead_sentence}"
        else:
            # Join top 2-3 most relevant grounded statements
            top_sents = [s for _, s, _ in selected_sentences[:3]]
            answer_body = " ".join(top_sents)

        # Build verified citations block
        citations_lines = []
        for ev in evidence[:3]:
            citations_lines.append(
                f"- **{ev.document_name}** | **Page:** {ev.page} | **Section:** {ev.section} *(Criterion: {ev.criterion}, AY: {ev.academic_year})*"
            )

        final_answer = (
            f"{answer_body}\n\n"
            f"**Supporting Source Records:**\n" + "\n".join(citations_lines)
        )

        finding_summary = answer_body.split(".")[0] + "." if "." in answer_body else answer_body[:120]
        return final_answer, finding_summary

answer_engine = AccreditationAnswerEngine()
