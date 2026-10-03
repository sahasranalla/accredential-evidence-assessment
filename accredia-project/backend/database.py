import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from .config import settings

def get_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investigations (
        investigation_id TEXT PRIMARY KEY,
        question TEXT NOT NULL,
        status TEXT NOT NULL,
        mode TEXT NOT NULL,
        answer TEXT,
        root_cause TEXT,
        confidence REAL,
        confidence_level TEXT,
        investigation_depth INTEGER,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        data_json TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investigation_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        investigation_id TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        description TEXT NOT NULL,
        query TEXT,
        status TEXT NOT NULL,
        findings_count INTEGER DEFAULT 0,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (investigation_id) REFERENCES investigations(investigation_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        investigation_id TEXT NOT NULL,
        action TEXT NOT NULL,
        query TEXT,
        documents_searched INTEGER DEFAULT 0,
        evidence_selected INTEGER DEFAULT 0,
        followup_query TEXT,
        contradictions_detected INTEGER DEFAULT 0,
        final_result TEXT,
        details_json TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS criteria (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        weightage INTEGER NOT NULL,
        description TEXT NOT NULL,
        subcriteria_json TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence_gaps (
        gap_id TEXT PRIMARY KEY,
        criterion TEXT NOT NULL,
        subcriterion TEXT,
        topic TEXT NOT NULL,
        current_evidence_count INTEGER DEFAULT 0,
        suggested_documents_json TEXT NOT NULL,
        priority TEXT NOT NULL,
        reason TEXT
    );
    """)
    
    conn.commit()
    
    # Seed criteria and gaps from metadata if empty
    cursor.execute("SELECT COUNT(*) as count FROM criteria")
    if cursor.fetchone()["count"] == 0:
        crit_file = os.path.join(settings.METADATA_DIR, "criteria.json")
        if os.path.exists(crit_file):
            with open(crit_file, "r", encoding="utf-8") as f:
                for c in json.load(f):
                    cursor.execute("""
                    INSERT OR REPLACE INTO criteria (id, name, weightage, description, subcriteria_json)
                    VALUES (?, ?, ?, ?, ?)
                    """, (c["id"], c["name"], c["weightage"], c["description"], json.dumps(c.get("subcriteria", []))))
            conn.commit()

    cursor.execute("SELECT COUNT(*) as count FROM evidence_gaps")
    if cursor.fetchone()["count"] == 0:
        gap_file = os.path.join(settings.METADATA_DIR, "evidence_gaps.json")
        if os.path.exists(gap_file):
            with open(gap_file, "r", encoding="utf-8") as f:
                for g in json.load(f):
                    cursor.execute("""
                    INSERT OR REPLACE INTO evidence_gaps (gap_id, criterion, subcriterion, topic, current_evidence_count, suggested_documents_json, priority, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (g["gap_id"], g["criterion"], g.get("subcriterion", ""), g["topic"], g.get("current_evidence_count", 0), json.dumps(g.get("suggested_documents", [])), g.get("priority", "MEDIUM"), g.get("reason", "")))
            conn.commit()

    conn.close()

def save_investigation(resp_dict: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO investigations 
    (investigation_id, question, status, mode, answer, root_cause, confidence, confidence_level, investigation_depth, created_at, completed_at, data_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resp_dict["investigation_id"],
        resp_dict["question"],
        resp_dict["status"],
        resp_dict.get("mode", "Local Accreditation Evidence Mode"),
        resp_dict.get("answer", ""),
        resp_dict.get("root_cause") or resp_dict.get("evidence_insight"),
        resp_dict.get("confidence", 0.0),
        resp_dict.get("confidence_level", "Moderate Evidence Support"),
        resp_dict.get("investigation_depth", 1),
        resp_dict["created_at"],
        resp_dict.get("completed_at"),
        json.dumps(resp_dict)
    ))
    
    # Save steps
    for step in resp_dict.get("steps", []):
        cursor.execute("""
        INSERT INTO investigation_steps (investigation_id, step_number, action_type, description, query, status, findings_count, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resp_dict["investigation_id"],
            step["step_number"],
            step["action_type"],
            step["description"],
            step.get("query"),
            step["status"],
            step.get("findings_count", 0),
            step["timestamp"]
        ))
        
    conn.commit()
    conn.close()

def get_investigation_by_id(inv_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_json FROM investigations WHERE investigation_id = ?", (inv_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["data_json"])
    return None

def list_all_investigations() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT investigation_id, question, status, mode, root_cause, confidence, confidence_level, investigation_depth, created_at, completed_at, data_json
    FROM investigations ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        item = json.loads(r["data_json"])
        results.append({
            "investigation_id": r["investigation_id"],
            "question": r["question"],
            "status": r["status"],
            "mode": r["mode"],
            "root_cause": r["root_cause"],
            "evidence_insight": r["root_cause"],
            "confidence": r["confidence"],
            "confidence_level": r["confidence_level"],
            "investigation_depth": r["investigation_depth"],
            "evidence_count": len(item.get("evidence", [])),
            "citations_count": len(item.get("citations", [])),
            "created_at": r["created_at"],
            "completed_at": r["completed_at"]
        })
    return results

def list_criteria() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM criteria ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r["id"],
        "name": r["name"],
        "weightage": r["weightage"],
        "description": r["description"],
        "subcriteria": json.loads(r["subcriteria_json"])
    } for r in rows]

def list_evidence_gaps() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evidence_gaps ORDER BY priority ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{
        "gap_id": r["gap_id"],
        "criterion": r["criterion"],
        "subcriterion": r["subcriterion"],
        "topic": r["topic"],
        "current_evidence_count": r["current_evidence_count"],
        "suggested_documents": json.loads(r["suggested_documents_json"]),
        "priority": r["priority"],
        "reason": r["reason"]
    } for r in rows]

def log_audit(entry: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs 
    (log_id, timestamp, investigation_id, action, query, documents_searched, evidence_selected, followup_query, contradictions_detected, final_result, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry["log_id"],
        entry["timestamp"],
        entry["investigation_id"],
        entry["action"],
        entry.get("query"),
        entry.get("documents_searched", 0),
        entry.get("evidence_selected", 0),
        entry.get("followup_query"),
        entry.get("contradictions_detected", 0),
        entry.get("final_result"),
        json.dumps(entry.get("details", {}))
    ))
    conn.commit()
    conn.close()

def list_all_audits(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "log_id": r["log_id"],
        "timestamp": r["timestamp"],
        "investigation_id": r["investigation_id"],
        "action": r["action"],
        "query": r["query"],
        "documents_searched": r["documents_searched"],
        "evidence_selected": r["evidence_selected"],
        "followup_query": r["followup_query"],
        "contradictions_detected": r["contradictions_detected"],
        "final_result": r["final_result"],
        "details": json.loads(r["details_json"]) if r["details_json"] else {}
    } for r in rows]
