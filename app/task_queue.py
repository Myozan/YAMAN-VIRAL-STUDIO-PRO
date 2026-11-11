"""Durable SQLite task-queue primitives for same-host workers.

The queue uses short BEGIN IMMEDIATE transactions for enqueue/claim/lease changes.
Execution is deliberately kept outside transactions. SQLite WAL must live on a
local filesystem; this module does not claim multi-host coordination.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TERMINAL_STATUSES = ("completed", "failed", "cancelled")
DEFAULT_LEASE_SECONDS = 60


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime | None = None) -> str:
    return (value or utcnow()).isoformat()


def connect(database: str | Path, timeout: float = 20) -> sqlite3.Connection:
    db = sqlite3.connect(str(database), timeout=timeout, isolation_level=None)
    db.execute("PRAGMA busy_timeout=20000")
    return db


def init_schema(db: sqlite3.Connection) -> None:
    db.execute("""
        CREATE TABLE IF NOT EXISTS task_queue (
            task_id TEXT PRIMARY KEY,
            task_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'queued',
            priority INTEGER NOT NULL DEFAULT 100,
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            available_at TEXT NOT NULL,
            owner_id TEXT,
            lease_expires_at TEXT,
            last_error TEXT,
            idempotency_key TEXT UNIQUE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_task_queue_ready ON task_queue(status, available_at, priority, created_at)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_task_queue_lease ON task_queue(status, lease_expires_at)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_task_queue_owner ON task_queue(owner_id, status)")


def enqueue(
    database: str | Path,
    task_type: str,
    payload: dict[str, Any],
    *,
    task_id: str | None = None,
    priority: int = 100,
    max_attempts: int = 3,
    delay_seconds: int = 0,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    if not task_type or len(task_type) > 80:
        raise ValueError("Invalid task type")
    if not isinstance(payload, dict):
        raise ValueError("Task payload must be an object")
    if not 1 <= int(max_attempts) <= 20:
        raise ValueError("max_attempts must be between 1 and 20")
    task_id = task_id or uuid.uuid4().hex
    now = utcnow()
    available = now + timedelta(seconds=max(0, int(delay_seconds)))
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
    with connect(database) as db:
        db.execute("BEGIN IMMEDIATE")
        if idempotency_key:
            existing = db.execute("SELECT task_id FROM task_queue WHERE idempotency_key=?", (idempotency_key,)).fetchone()
            if existing:
                db.commit()
                return get(database, existing[0])  # type: ignore[return-value]
        db.execute(
            """INSERT INTO task_queue(task_id,task_type,payload_json,status,priority,attempts,max_attempts,
               available_at,created_at,updated_at,idempotency_key)
               VALUES(?,?,?,'queued',?,0,?,?,?,?,?)""",
            (task_id, task_type, serialized, int(priority), int(max_attempts), stamp(available),
             stamp(now), stamp(now), idempotency_key),
        )
        db.commit()
    return get(database, task_id)  # type: ignore[return-value]


def get(database: str | Path, task_id: str) -> dict[str, Any] | None:
    with connect(database) as db:
        row = db.execute(
            """SELECT task_id,task_type,payload_json,status,priority,attempts,max_attempts,
               available_at,owner_id,lease_expires_at,last_error,idempotency_key,created_at,updated_at
               FROM task_queue WHERE task_id=?""", (task_id,)
        ).fetchone()
    if not row:
        return None
    keys = ("task_id","task_type","payload_json","status","priority","attempts","max_attempts",
            "available_at","owner_id","lease_expires_at","last_error","idempotency_key","created_at","updated_at")
    result = dict(zip(keys, row))
    result["payload"] = json.loads(result.pop("payload_json"))
    return result


def claim(database: str | Path, worker_id: str, *, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> dict[str, Any] | None:
    now = utcnow()
    lease = stamp(now + timedelta(seconds=max(10, int(lease_seconds))))
    with connect(database) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """SELECT task_id FROM task_queue
               WHERE status='queued' AND available_at<=? AND attempts<max_attempts
               ORDER BY priority ASC, created_at ASC LIMIT 1""", (stamp(now),)
        ).fetchone()
        if not row:
            db.commit()
            return None
        task_id = row[0]
        changed = db.execute(
            """UPDATE task_queue SET status='running',owner_id=?,lease_expires_at=?,
               attempts=attempts+1,updated_at=? WHERE task_id=? AND status='queued'""",
            (worker_id, lease, stamp(now), task_id),
        ).rowcount
        if changed != 1:
            db.rollback()
            return None
        db.commit()
    return get(database, task_id)


def heartbeat(database: str | Path, task_id: str, worker_id: str, *, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> bool:
    now = utcnow()
    with connect(database) as db:
        changed = db.execute(
            """UPDATE task_queue SET lease_expires_at=?,updated_at=?
               WHERE task_id=? AND owner_id=? AND status='running' AND lease_expires_at>=?""",
            (stamp(now + timedelta(seconds=max(10, int(lease_seconds)))), stamp(now), task_id, worker_id, stamp(now)),
        ).rowcount
    return changed == 1


def recover_expired(database: str | Path, *, retry_base_seconds: int = 5, now: datetime | None = None) -> dict[str, int]:
    now = now or utcnow()
    current = stamp(now)
    requeued = failed = 0
    with connect(database) as db:
        db.execute("BEGIN IMMEDIATE")
        rows = db.execute(
            """SELECT task_id,attempts,max_attempts,last_error FROM task_queue
               WHERE status='running' AND lease_expires_at IS NOT NULL AND lease_expires_at<?""",
            (current,),
        ).fetchall()
        for task_id, attempts, max_attempts, last_error in rows:
            if attempts < max_attempts:
                delay = min(300, max(1, int(retry_base_seconds)) * (2 ** max(0, attempts - 1)))
                available = stamp(now + timedelta(seconds=delay))
                db.execute(
                    """UPDATE task_queue SET status='queued',owner_id=NULL,lease_expires_at=NULL,
                       available_at=?,last_error=?,updated_at=? WHERE task_id=? AND status='running'""",
                    (available, last_error or "Worker lease expired", current, task_id),
                )
                requeued += 1
            else:
                db.execute(
                    """UPDATE task_queue SET status='failed',owner_id=NULL,lease_expires_at=NULL,
                       last_error=?,updated_at=? WHERE task_id=? AND status='running'""",
                    ("Worker lease expired; maximum attempts reached", current, task_id),
                )
                failed += 1
        db.commit()
    return {"requeued": requeued, "failed": failed}


def complete(database: str | Path, task_id: str, worker_id: str, *, error: str | None = None) -> bool:
    now = stamp()
    status = "failed" if error else "completed"
    with connect(database) as db:
        changed = db.execute(
            """UPDATE task_queue SET status=?,owner_id=NULL,lease_expires_at=NULL,last_error=?,updated_at=?
               WHERE task_id=? AND owner_id=? AND status='running' AND lease_expires_at>=?""",
            (status, (error or "")[:1000] or None, now, task_id, worker_id, now),
        ).rowcount
    return changed == 1


def cancel(database: str | Path, task_id: str) -> bool:
    """Cancel a queued/running task; the former owner can no longer renew or complete it."""
    now = stamp()
    with connect(database) as db:
        db.execute("BEGIN IMMEDIATE")
        changed = db.execute(
            """UPDATE task_queue SET status='cancelled',owner_id=NULL,lease_expires_at=NULL,
               updated_at=? WHERE task_id=? AND status IN ('queued','running')""",
            (now, task_id),
        ).rowcount
        db.commit()
    return changed == 1

def enqueue_in_transaction(
    db: sqlite3.Connection,
    task_type: str,
    payload: dict[str, Any],
    *,
    task_id: str,
    priority: int = 100,
    max_attempts: int = 3,
    delay_seconds: int = 0,
    idempotency_key: str | None = None,
) -> None:
    """Insert a queue row using a caller-owned transaction."""
    if not task_type or len(task_type) > 80:
        raise ValueError("Invalid task type")
    if not isinstance(payload, dict):
        raise ValueError("Task payload must be an object")
    if not 1 <= int(max_attempts) <= 20:
        raise ValueError("max_attempts must be between 1 and 20")
    now = utcnow()
    db.execute(
        """INSERT INTO task_queue(task_id,task_type,payload_json,status,priority,attempts,max_attempts,
           available_at,created_at,updated_at,idempotency_key)
           VALUES(?,?,?,'queued',?,0,?,?,?,?,?)""",
        (task_id, task_type, json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str),
         int(priority), int(max_attempts), stamp(now + timedelta(seconds=max(0, int(delay_seconds)))),
         stamp(now), stamp(now), idempotency_key),
    )
