import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "data", "guardprompt.db"
)

def get_connection():
    """Get a SQLite connection."""
    db_file = os.path.normpath(DB_PATH)
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create tables if they don't exist.
    Run this once on startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_hash TEXT NOT NULL,
            decision TEXT NOT NULL,
            final_score INTEGER NOT NULL,
            triggered_layers TEXT NOT NULL,
            reasons TEXT NOT NULL,
            layer1_score INTEGER DEFAULT 0,
            layer2_score INTEGER DEFAULT 0,
            layer3_score INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized")


def save_log(prompt: str, result: dict) -> int:
    """
    Save one analysis result to the database.
    We hash the prompt — raw text is never stored.

    Returns the ID of the inserted row.
    """
    # Hash the prompt for privacy — SHA256, one way, irreversible
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analysis_logs (
            prompt_hash,
            decision,
            final_score,
            triggered_layers,
            reasons,
            layer1_score,
            layer2_score,
            layer3_score,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        prompt_hash,
        result.get("decision", "pass"),
        result.get("final_score", 0),
        ", ".join(result.get("triggered_layers", [])),
        ", ".join(result.get("reasons", [])),
        result.get("layer_scores", {}).get("layer1_rule", 0),
        result.get("layer_scores", {}).get("layer2_semantic", 0),
        result.get("layer_scores", {}).get("layer3_heuristic", 0),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_logs(limit: int = 50) -> list:
    """Get the most recent analysis logs."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM analysis_logs
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_stats() -> dict:
    """Get summary statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM analysis_logs")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as blocked FROM analysis_logs WHERE decision = 'block'")
    blocked = cursor.fetchone()["blocked"]

    cursor.execute("SELECT COUNT(*) as flagged FROM analysis_logs WHERE decision = 'flag'")
    flagged = cursor.fetchone()["flagged"]

    cursor.execute("SELECT COUNT(*) as passed FROM analysis_logs WHERE decision = 'pass'")
    passed = cursor.fetchone()["passed"]

    cursor.execute("SELECT AVG(final_score) as avg_score FROM analysis_logs")
    avg = cursor.fetchone()["avg_score"]

    conn.close()

    return {
        "total_requests": total,
        "blocked": blocked,
        "flagged": flagged,
        "passed": passed,
        "average_score": round(avg or 0, 1)
    }
