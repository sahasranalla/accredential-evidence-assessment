import os
import json
from typing import List, Dict, Any, Set
from ..models.investigation import EvidenceGraph, GraphNode, GraphEdge
from ..models.evidence import EvidenceItem
from ..models.contradiction import ContradictionItem

class GraphBuilder:
    """
    Builds an interactive Accreditation Evidence Graph:
    Question -> Criterion -> Subcriterion -> Document -> Page -> Section -> Department -> Finding
    """

    def build_graph(
        self,
        question: str,
        evidence: List[EvidenceItem],
        contradictions: List[ContradictionItem] = None,
        finding: str = ""
    ) -> EvidenceGraph:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        added_nodes: Set[str] = set()

        def add_node(node: GraphNode):
            if node.id not in added_nodes:
                nodes.append(node)
                added_nodes.add(node.id)

        # 1. Question Root Node
        add_node(GraphNode(
            id="NODE-QUESTION",
            type="question",
            label=question[:65] + ("..." if len(question) > 65 else ""),
            data={"question": question, "type": "question", "title": question},
            position={"x": 520, "y": 20}
        ))

        # 2. Search / Verification Process Node
        add_node(GraphNode(
            id="NODE-SEARCH",
            type="process",
            label="Accreditation Retrieval & Verification",
            data={"stage": "search", "status": "completed", "title": "Evidence Verification Pipeline"},
            position={"x": 520, "y": 120}
        ))
        edges.append(GraphEdge(
            id="EDGE-Q-SEARCH",
            source="NODE-QUESTION",
            target="NODE-SEARCH",
            relationship="investigates",
            strength=1.0
        ))

        if not evidence:
            return EvidenceGraph(nodes=nodes, edges=edges)

        # 3. Criteria & Subcriteria Tier
        criteria_set = set()
        for ev in evidence[:8]:
            if ev.criterion:
                criteria_set.add(ev.criterion)
        if not criteria_set:
            criteria_set.add("Criterion 6")

        sorted_criteria = sorted(list(criteria_set))
        crit_x_step = 600 / max(1, len(sorted_criteria))
        for c_idx, crit_name in enumerate(sorted_criteria):
            crit_node_id = f"NODE-{crit_name.replace(' ', '-').upper()}"
            add_node(GraphNode(
                id=crit_node_id,
                type="criterion",
                label=crit_name,
                data={"title": crit_name, "type": "criterion", "criterion": crit_name},
                position={"x": 260 + (c_idx * int(crit_x_step)), "y": 230}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-SEARCH-{crit_node_id}",
                source="NODE-SEARCH",
                target=crit_node_id,
                relationship="classifies",
                strength=0.95
            ))

        # 4. Document Nodes Tier
        top_evidence = evidence[:7]
        doc_x_step = 1000 / max(1, len(top_evidence))
        for d_idx, ev in enumerate(top_evidence):
            doc_id = ev.document_id
            crit_id = f"NODE-{ev.criterion.replace(' ', '-').upper()}" if ev.criterion in criteria_set else "NODE-SEARCH"
            
            ntype = "contradiction" if ev.status == "superseded" else ("finding" if ev.evidence_type == "Direct Evidence" else "document")
            add_node(GraphNode(
                id=doc_id,
                type=ntype,
                label=f"{ev.document_name[:26]}",
                data={
                    "document_id": ev.document_id,
                    "title": ev.document_name,
                    "department": ev.department,
                    "date": ev.academic_year,
                    "status": ev.status,
                    "page": ev.page,
                    "section": ev.section,
                    "excerpt": ev.excerpt,
                    "evidence_type": ev.evidence_type,
                    "relevance": ev.relevance
                },
                position={"x": 80 + int(d_idx * doc_x_step), "y": 380}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-CRIT-{doc_id}",
                source=crit_id if crit_id in added_nodes else "NODE-SEARCH",
                target=doc_id,
                relationship="evidenced_by",
                strength=ev.relevance
            ))

            # 5. Page & Section Sub-nodes
            page_node_id = f"PAGE-{doc_id}-P{ev.page}"
            add_node(GraphNode(
                id=page_node_id,
                type="page",
                label=f"Page {ev.page}: {ev.section[:20]}",
                data={
                    "document_id": ev.document_id,
                    "title": f"Page {ev.page} ({ev.section})",
                    "page": ev.page,
                    "section": ev.section,
                    "department": ev.department,
                    "date": ev.academic_year,
                    "excerpt": ev.excerpt
                },
                position={"x": 80 + int(d_idx * doc_x_step), "y": 520}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-PAGE-{doc_id}-{ev.page}",
                source=doc_id,
                target=page_node_id,
                relationship="located_on",
                strength=0.9
            ))

        # 6. Department Nodes
        dept_set = {ev.department for ev in top_evidence if ev.department}
        for j, dept in enumerate(list(dept_set)[:4]):
            dept_node_id = f"DEPT-{dept.replace(' ', '-').upper()}"
            add_node(GraphNode(
                id=dept_node_id,
                type="department",
                label=dept,
                data={"title": f"Dept of {dept}", "type": "department", "department": dept},
                position={"x": 120 + (j * 260), "y": 660}
            ))
            # Link from matching documents
            for ev in top_evidence:
                if ev.department == dept:
                    edges.append(GraphEdge(
                        id=f"EDGE-DEPT-{ev.document_id}-{dept_node_id}",
                        source=ev.document_id,
                        target=dept_node_id,
                        relationship="authored_by",
                        strength=0.85
                    ))
                    break

        # 7. Contradiction Nodes (if any detected)
        if contradictions:
            for c_idx, c in enumerate(contradictions[:2]):
                c_node_id = f"CONFLICT-{c_idx}"
                add_node(GraphNode(
                    id=c_node_id,
                    type="contradiction",
                    label=f"Conflict: {c.topic[:24]}",
                    data={
                        "title": c.topic,
                        "type": "contradiction",
                        "claim_a": c.claim_a,
                        "claim_b": c.claim_b,
                        "analysis": c.conflict_analysis
                    },
                    position={"x": 1050, "y": 380 + (c_idx * 140)}
                ))
                if c.source_a_id in added_nodes:
                    edges.append(GraphEdge(
                        id=f"EDGE-CONFLICT-A-{c_idx}",
                        source=c.source_a_id,
                        target=c_node_id,
                        relationship="conflicts_with",
                        strength=0.8
                    ))
                if c.source_b_id in added_nodes:
                    edges.append(GraphEdge(
                        id=f"EDGE-CONFLICT-B-{c_idx}",
                        source=c.source_b_id,
                        target=c_node_id,
                        relationship="conflicts_with",
                        strength=0.8
                    ))

        # 8. Finding Conclusion Node
        if finding and finding != "INSUFFICIENT EVIDENCE":
            add_node(GraphNode(
                id="NODE-ROOT-CAUSE",
                type="root_cause",
                label="Accreditation Evidence Finding",
                data={"title": "Verified Evidence Finding", "root_cause": finding, "finding": finding},
                position={"x": 520, "y": 800}
            ))
            for ev in top_evidence[:3]:
                page_node_id = f"PAGE-{ev.document_id}-P{ev.page}"
                src = page_node_id if page_node_id in added_nodes else ev.document_id
                edges.append(GraphEdge(
                    id=f"EDGE-FINDING-{src}",
                    source=src,
                    target="NODE-ROOT-CAUSE",
                    relationship="supports",
                    strength=ev.strength
                ))

        return EvidenceGraph(nodes=nodes, edges=edges)

    def build_master_graph(self) -> EvidenceGraph:
        """
        Builds the Master Institutional Accreditation Graph for Vidyapath Institute of Technology (VITEC).
        Connects Institution -> Criteria 1-7 -> Key Departments -> Verified Repository Documents -> Page Citations.
        """
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        added: Set[str] = set()

        def add_n(n: GraphNode):
            if n.id not in added:
                nodes.append(n)
                added.add(n.id)

        # 1. Institution Central Node
        add_n(GraphNode(
            id="NODE-INSTITUTION",
            type="question",
            label="Vidyapath Institute of Technology",
            data={"title": "VITEC Accreditation Core", "type": "institution", "department": "Hyderabad, Telangana"},
            position={"x": 720, "y": 20}
        ))

        # 2. Seven NAAC Criteria
        criteria_info = [
            ("C1", "Criterion 1", "Curricular Aspects", 100),
            ("C2", "Criterion 2", "Teaching-Learning & Eval", 350),
            ("C3", "Criterion 3", "Research & Innovation", 110),
            ("C4", "Criterion 4", "Infrastructure & Learning", 100),
            ("C5", "Criterion 5", "Student Support", 120),
            ("C6", "Criterion 6", "Governance & Leadership", 100),
            ("C7", "Criterion 7", "Institutional Values", 100),
        ]

        for i, (cid, cname, label, weight) in enumerate(criteria_info):
            cnode_id = f"NODE-{cid}"
            add_n(GraphNode(
                id=cnode_id,
                type="criterion",
                label=f"{cname}: {label}",
                data={"title": f"{cname}: {label}", "criterion": cname, "weightage": weight},
                position={"x": 50 + i * 230, "y": 180}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-INST-{cid}",
                source="NODE-INSTITUTION",
                target=cnode_id,
                relationship="governs",
                strength=1.0
            ))

        # 3. Core Departments
        dept_info = [
            ("ACADEMIC", "Academic Affairs & BoS", "NODE-C1"),
            ("CSE", "Computer Science & Eng", "NODE-C2"),
            ("R&D", "Research & Development Cell", "NODE-C3"),
            ("LIBRARY", "Central Library & ILMS", "NODE-C4"),
            ("PLACEMENT", "Corporate Relations & TPC", "NODE-C5"),
            ("IQAC", "Internal Quality Assurance Cell", "NODE-C6"),
            ("ESTATE", "Green Campus & Operations", "NODE-C7")
        ]

        for i, (did, dname, parent_crit) in enumerate(dept_info):
            dnode_id = f"NODE-DEPT-{did}"
            add_n(GraphNode(
                id=dnode_id,
                type="department",
                label=f"{did} Unit",
                data={"title": dname, "department": did},
                position={"x": 50 + i * 230, "y": 340}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-CRIT-{did}",
                source=parent_crit,
                target=dnode_id,
                relationship="administered_by",
                strength=1.0
            ))

        # 4. Verified Repository Documents
        sample_docs = [
            ("DOC-ACCR-020", "BoS Minutes & CBCS Curriculum", "NODE-DEPT-ACADEMIC", "1"),
            ("DOC-ACCR-001", "Academic Audit Report 2024-25", "NODE-DEPT-CSE", "1"),
            ("DOC-ACCR-007", "Faculty Seed Grant Sanctions", "NODE-DEPT-R&D", "1"),
            ("DOC-ACCR-012", "Library ILMS KOHA Audit", "NODE-DEPT-LIBRARY", "1"),
            ("DOC-ACCR-015", "Campus Placement Report 2024-25", "NODE-DEPT-PLACEMENT", "3"),
            ("DOC-ACCR-004", "IQAC Annual Report & ATR", "NODE-DEPT-IQAC", "2"),
            ("DOC-ACCR-025", "Green Audit & Solar Energy Report", "NODE-DEPT-ESTATE", "2")
        ]

        for i, (doc_id, title, dept_id, pg) in enumerate(sample_docs):
            add_n(GraphNode(
                id=doc_id,
                type="document",
                label=title,
                data={"title": title, "document_id": doc_id, "page": pg},
                position={"x": 50 + i * 230, "y": 500}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-DEPT-DOC-{doc_id}",
                source=dept_id,
                target=doc_id,
                relationship="archives",
                strength=0.9
            ))

            # Page Citation Node
            page_id = f"PAGE-{doc_id}"
            add_n(GraphNode(
                id=page_id,
                type="page",
                label=f"Verified Page {pg}",
                data={"title": f"Verified Page {pg} of {doc_id}", "document_id": doc_id, "page": pg},
                position={"x": 50 + i * 230, "y": 660}
            ))
            edges.append(GraphEdge(
                id=f"EDGE-DOC-PAGE-{doc_id}",
                source=doc_id,
                target=page_id,
                relationship="on_page",
                strength=1.0
            ))

        return EvidenceGraph(nodes=nodes, edges=edges)

graph_builder = GraphBuilder()
