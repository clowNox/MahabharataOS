"""
task_repo.py
SQLite persistence for tasks, runs, and delegation chains.
Replaces the in-memory MOCK_DB.
"""

import sqlite3
import json
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "mahabharata.db")

_CREATE_TASKS = """
CREATE TABLE IF NOT EXISTS tasks (
    id          TEXT PRIMARY KEY,
    project_id  TEXT,
    title       TEXT NOT NULL,
    original_prompt TEXT NOT NULL,
    context     TEXT,          -- JSON blob
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS runs (
    id              TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL REFERENCES tasks(id),
    next_action     TEXT,
    ceo_result      TEXT,      -- JSON blob
    delegation_chain TEXT,     -- JSON blob (list of node dicts)
    outputs         TEXT,      -- JSON blob
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_DELEGATIONS = """
CREATE TABLE IF NOT EXISTS delegations (
    task_id     TEXT PRIMARY KEY REFERENCES tasks(id),
    chain       TEXT NOT NULL,  -- JSON blob (latest chain)
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

_CREATE_CAMPAIGNS = """
CREATE TABLE IF NOT EXISTS campaigns (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    plan        TEXT,          -- JSON blob
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_task_db() -> None:
    """Create tasks/runs/delegations/campaigns tables if they don't exist."""
    try:
        with _get_conn() as conn:
            conn.execute(_CREATE_TASKS)
            conn.execute(_CREATE_RUNS)
            conn.execute(_CREATE_DELEGATIONS)
            conn.execute(_CREATE_CAMPAIGNS)
            # Add status column to existing DBs that predate this field
            try:
                conn.execute("ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")
            except Exception:
                pass  # column already exists
            conn.commit()
    except Exception as e:
        raise RuntimeError(f"Task DB init failed: {e}") from e


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def save_task(task_id: str, project_id: str, title: str, prompt: str, context: dict) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO tasks (id, project_id, title, original_prompt, context) VALUES (?,?,?,?,?)",
            (task_id, project_id, title, prompt, json.dumps(context or {})),
        )
        conn.commit()


def get_task(task_id: str) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["context"] = json.loads(d["context"] or "{}")
    return d


def get_all_tasks(skip: int = 0, limit: int = 50) -> list:
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT t.*,
                   r.next_action,
                   r.created_at AS last_run_at
            FROM tasks t
            LEFT JOIN (
                SELECT task_id, next_action, created_at,
                       ROW_NUMBER() OVER (PARTITION BY task_id ORDER BY created_at DESC) AS rn
                FROM runs
            ) r ON r.task_id = t.id AND r.rn = 1
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, skip),
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        d["context"] = json.loads(d.get("context") or "{}")
        # Derive a display status from run state
        if d.get("next_action") == "human_approval":
            d["status"] = "pending_review"
        elif d.get("next_action") == "ready_for_review":
            d["status"] = "in_progress"
        else:
            d["status"] = "pending"
        result.append(d)
    return result


def get_tasks_count() -> int:
    with _get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM tasks").fetchone()
    return row["cnt"] if row else 0


def update_task_status(task_id: str, status: str) -> bool:
    with _get_conn() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (status, task_id),
        )
        conn.commit()
    return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def save_run(run_id: str, task_id: str, next_action: str,
             ceo_result: dict, delegation_chain: list, outputs: dict) -> None:
    with _get_conn() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO runs
               (id, task_id, next_action, ceo_result, delegation_chain, outputs)
               VALUES (?,?,?,?,?,?)""",
            (
                run_id,
                task_id,
                next_action,
                json.dumps(ceo_result, default=str),
                json.dumps(delegation_chain, default=str),
                json.dumps(outputs, default=str),
            ),
        )
        conn.commit()


def get_latest_run(task_id: str) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM runs WHERE task_id = ? ORDER BY created_at DESC LIMIT 1",
            (task_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["ceo_result"] = json.loads(d["ceo_result"] or "{}")
    d["delegation_chain"] = json.loads(d["delegation_chain"] or "[]")
    d["outputs"] = json.loads(d["outputs"] or "{}")
    return d


# ---------------------------------------------------------------------------
# Delegation chains
# ---------------------------------------------------------------------------

def save_delegation(task_id: str, chain: list) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO delegations (task_id, chain) VALUES (?,?)",
            (task_id, json.dumps(chain, default=str)),
        )
        conn.commit()


def get_delegation(task_id: str) -> Optional[list]:
    with _get_conn() as conn:
        row = conn.execute("SELECT chain FROM delegations WHERE task_id = ?", (task_id,)).fetchone()
    return json.loads(row["chain"]) if row else None


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

def save_campaign(campaign_id: str, title: str, description: str, plan: list) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO campaigns (id, title, description, plan) VALUES (?,?,?,?)",
            (campaign_id, title, description, json.dumps(plan, default=str)),
        )
        conn.commit()


def get_campaign(campaign_id: str) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["plan"] = json.loads(d["plan"] or "[]")
    return d
