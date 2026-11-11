"""Local-first Autopilot schedules with atomic durable-queue handoff."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app import task_queue


_COLUMNS = (
    "id,name,niche,language,clips,min_seconds,max_seconds,platforms_json,frequency,"
    "publish_time,timezone,enabled,next_run,last_run,last_status,last_message,"
    "processed_json,created_at,updated_at"
)


def init_autopilot(db_path: Path):
    with sqlite3.connect(db_path, timeout=20) as db:
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("""CREATE TABLE IF NOT EXISTS autopilots (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, niche TEXT NOT NULL,
            language TEXT NOT NULL, clips INTEGER NOT NULL, min_seconds INTEGER NOT NULL,
            max_seconds INTEGER NOT NULL, platforms_json TEXT NOT NULL,
            frequency TEXT NOT NULL, publish_time TEXT NOT NULL, timezone TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1, next_run TEXT NOT NULL,
            last_run TEXT, last_status TEXT NOT NULL DEFAULT 'ready',
            last_message TEXT NOT NULL DEFAULT '', processed_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS autopilot_runs (
            id TEXT PRIMARY KEY, autopilot_id TEXT NOT NULL, started_at TEXT NOT NULL,
            finished_at TEXT, status TEXT NOT NULL, message TEXT NOT NULL,
            task_id TEXT, job_id TEXT, output_json TEXT NOT NULL DEFAULT '[]'
        )""")
        # Standalone test databases receive the same task journal as the app.
        db.execute("""CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            status TEXT NOT NULL, percent INTEGER NOT NULL, stage TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}', worker_id TEXT
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS task_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
            event_type TEXT NOT NULL, created_at TEXT NOT NULL, payload_json TEXT NOT NULL
        )""")
        task_queue.init_schema(db)
        # Recover legacy process-local runs left behind by an upgrade or crash.
        queue_rows = db.execute(
            "SELECT task_id,status,payload_json FROM task_queue WHERE task_type='autopilot' ORDER BY created_at DESC"
        ).fetchall()
        latest_queue = {}
        for queue_task_id, queue_status, raw_payload in queue_rows:
            try:
                autopilot_id = json.loads(raw_payload or "{}").get("autopilot_id")
            except (TypeError, ValueError):
                autopilot_id = None
            if autopilot_id and autopilot_id not in latest_queue:
                latest_queue[autopilot_id] = (queue_task_id, queue_status)
        stale_items = db.execute(
            "SELECT id FROM autopilots WHERE last_status IN ('queued','running')"
        ).fetchall()
        for (autopilot_id,) in stale_items:
            latest = latest_queue.get(autopilot_id)
            if latest and latest[1] in {"queued", "running"}:
                continue
            if latest and latest[1] == "cancelled":
                recovered_status, message = "cancelled", "Önceki Autopilot görevi iptal edildi."
            elif latest and latest[1] == "failed":
                recovered_status, message = "failed", "Önceki Autopilot görevi worker denemelerini tüketti."
            elif latest and latest[1] == "completed":
                run = db.execute(
                    "SELECT status,message FROM autopilot_runs WHERE task_id=?", (latest[0],)
                ).fetchone()
                recovered_status = run[0] if run else "failed"
                message = run[1] if run else "Tamamlanan kuyruk görevi için Autopilot geçmiş kaydı bulunamadı."
            else:
                recovered_status = "failed"
                message = "Eski süreç içi Autopilot çalışması yükseltme sırasında kesildi."
            db.execute(
                "UPDATE autopilots SET last_status=?,last_message=?,updated_at=? WHERE id=?",
                (recovered_status, message, datetime.now().astimezone().isoformat(), autopilot_id),
            )
        db.commit()


def _next_run(frequency: str, publish_time: str, timezone_name: str, now=None):
    if timezone_name == "Europe/Istanbul":
        from datetime import timezone as dt_timezone
        tz = dt_timezone(timedelta(hours=3), "TRT")
    else:
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Geçersiz saat dilimi.") from exc
    now = now.astimezone(tz) if now else datetime.now(tz)
    hour, minute = [int(x) for x in publish_time.split(":")]
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    if frequency == "weekly":
        while candidate.weekday() != 0:
            candidate += timedelta(days=1)
    return candidate.isoformat()


def _row(row):
    if not row:
        return None
    keys = tuple(_COLUMNS.split(","))
    data = dict(zip(keys, row))
    data["platforms"] = json.loads(data.pop("platforms_json"))
    data["processed_files"] = json.loads(data.pop("processed_json"))
    data["enabled"] = bool(data["enabled"])
    return data


def _select_item(db, item_id: str):
    return _row(db.execute(f"SELECT {_COLUMNS} FROM autopilots WHERE id=?", (item_id,)).fetchone())


def _enqueue_run_tx(db, item: dict, trigger: str, now: datetime, idempotency_key: str | None = None):
    task_id = uuid.uuid4().hex
    created = now.isoformat()
    payload = {"autopilot_id": item["id"], "item": item, "trigger": trigger}
    task_queue.enqueue_in_transaction(
        db, "autopilot", payload, task_id=task_id, priority=40,
        max_attempts=3, idempotency_key=idempotency_key,
    )
    state = {
        "task_id": task_id, "task_type": "autopilot", "autopilot_id": item["id"],
        "trigger": trigger, "percent": 1, "stage": "Autopilot kalıcı kuyruğa alındı",
        "status": "queued", "created_at": created, "updated_at": created,
    }
    serialized = json.dumps(state, ensure_ascii=False)
    db.execute(
        """INSERT INTO tasks(task_id,created_at,updated_at,status,percent,stage,payload_json,worker_id)
           VALUES(?,?,?,?,?,?,?,NULL)""",
        (task_id, created, created, "queued", 1, state["stage"], serialized),
    )
    db.execute(
        "INSERT INTO task_events(task_id,event_type,created_at,payload_json) VALUES(?,?,?,?)",
        (task_id, "queued", created, serialized),
    )
    return task_id


def create_autopilot(db_path: Path, data: dict):
    now = datetime.now().astimezone().isoformat()
    item_id = uuid.uuid4().hex[:12]
    next_run = _next_run(data["frequency"], data["publish_time"], data["timezone"])
    with sqlite3.connect(db_path, timeout=20) as db:
        db.execute("PRAGMA busy_timeout=20000")
        db.execute(
            """INSERT INTO autopilots
            (id,name,niche,language,clips,min_seconds,max_seconds,platforms_json,frequency,
             publish_time,timezone,enabled,next_run,created_at,updated_at)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (item_id, data["name"], data["niche"], data["language"], data["clips"],
             data["min_seconds"], data["max_seconds"], json.dumps(data["platforms"]),
             data["frequency"], data["publish_time"], data["timezone"], int(data["enabled"]),
             next_run, now, now),
        )
        db.commit()
    return get_autopilot(db_path, item_id)


def list_autopilots(db_path: Path):
    with sqlite3.connect(db_path, timeout=20) as db:
        rows = db.execute(f"SELECT {_COLUMNS} FROM autopilots ORDER BY created_at DESC").fetchall()
        items = [_row(row) for row in rows]
        for item in items:
            last = db.execute(
                "SELECT output_json FROM autopilot_runs WHERE autopilot_id=? ORDER BY started_at DESC LIMIT 1",
                (item["id"],),
            ).fetchone()
            item["last_outputs"] = json.loads(last[0]) if last and last[0] else []
    return items


def get_autopilot(db_path: Path, item_id: str):
    with sqlite3.connect(db_path, timeout=20) as db:
        return _select_item(db, item_id)


def update_autopilot(db_path: Path, item_id: str, changes: dict):
    now = datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path, timeout=20, isolation_level=None) as db:
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("BEGIN IMMEDIATE")
        current = _select_item(db, item_id)
        if not current:
            db.commit()
            return None
        if current["last_status"] in {"queued", "running"}:
            db.rollback()
            raise ValueError("Çalışan veya kuyrukta olan Autopilot düzenlenemez.")
        current.update(changes)
        next_run = _next_run(current["frequency"], current["publish_time"], current["timezone"])
        db.execute(
            """UPDATE autopilots SET name=?,niche=?,language=?,clips=?,min_seconds=?,max_seconds=?,
               platforms_json=?,frequency=?,publish_time=?,timezone=?,enabled=?,next_run=?,updated_at=?
               WHERE id=?""",
            (current["name"], current["niche"], current["language"], current["clips"],
             current["min_seconds"], current["max_seconds"], json.dumps(current["platforms"]),
             current["frequency"], current["publish_time"], current["timezone"],
             int(current["enabled"]), next_run, now, item_id),
        )
        db.commit()
    return get_autopilot(db_path, item_id)


def delete_autopilot(db_path: Path, item_id: str):
    with sqlite3.connect(db_path, timeout=20) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT last_status FROM autopilots WHERE id=?", (item_id,)).fetchone()
        if not row or row[0] in {"queued", "running"}:
            db.commit()
            return False
        cur = db.execute("DELETE FROM autopilots WHERE id=?", (item_id,))
        db.commit()
    return cur.rowcount > 0


def claim_due(db_path: Path):
    """Atomically advance due schedules and enqueue each run exactly once."""
    now = datetime.now().astimezone()
    queued = []
    with sqlite3.connect(db_path, timeout=20, isolation_level=None) as db:
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("BEGIN IMMEDIATE")
        rows = db.execute(
            f"SELECT {_COLUMNS} FROM autopilots WHERE enabled=1 ORDER BY next_run"
        ).fetchall()
        for raw in rows:
            item = _row(raw)
            if item["last_status"] in {"queued", "running"}:
                continue
            try:
                due = datetime.fromisoformat(item["next_run"])
            except (TypeError, ValueError):
                continue
            if due > now:
                continue
            next_run = _next_run(item["frequency"], item["publish_time"], item["timezone"], now)
            task_id = _enqueue_run_tx(
                db, item, "scheduled", now,
                idempotency_key=f"autopilot:{item['id']}:{item['next_run']}",
            )
            db.execute(
                """UPDATE autopilots SET next_run=?,last_status='queued',
                   last_message='Zamanlanmış üretim kalıcı kuyruğa alındı',updated_at=? WHERE id=?""",
                (next_run, now.isoformat(), item["id"]),
            )
            item["next_run"] = next_run
            item["last_status"] = "queued"
            item["queue_task_id"] = task_id
            queued.append(item)
        db.commit()
    return queued


def enqueue_manual_run(db_path: Path, item_id: str):
    """Atomically reserve a manual run and persist its public task and queue row."""
    now = datetime.now().astimezone()
    with sqlite3.connect(db_path, timeout=20, isolation_level=None) as db:
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("BEGIN IMMEDIATE")
        item = _select_item(db, item_id)
        if not item:
            db.commit()
            return {"status": "missing"}
        if item["last_status"] in {"queued", "running"}:
            db.commit()
            return {"status": "already_queued" if item["last_status"] == "queued" else "running"}
        task_id = _enqueue_run_tx(db, item, "manual", now)
        db.execute(
            """UPDATE autopilots SET last_status='queued',last_message='Manuel üretim kalıcı kuyruğa alındı',
               updated_at=? WHERE id=?""",
            (now.isoformat(), item_id),
        )
        db.commit()
    return {"status": "queued", "task_id": task_id, "item": item}


def finish_run(db_path: Path, item_id: str, status: str, message: str,
               task_id=None, job_id=None, outputs=None, processed_file=None):
    now = datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path, timeout=20) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT processed_json FROM autopilots WHERE id=?", (item_id,)).fetchone()
        processed = json.loads(row[0]) if row else []
        if processed_file and processed_file not in processed:
            processed = (processed + [processed_file])[-250:]
        db.execute(
            """UPDATE autopilots SET last_run=?,last_status=?,last_message=?,processed_json=?,updated_at=?
               WHERE id=?""",
            (now, status, message, json.dumps(processed), now, item_id),
        )
        serialized_outputs = json.dumps(outputs or [], ensure_ascii=False)
        existing = db.execute(
            "SELECT id FROM autopilot_runs WHERE task_id=? AND task_id IS NOT NULL",
            (task_id,),
        ).fetchone() if task_id else None
        if existing:
            db.execute(
                """UPDATE autopilot_runs SET finished_at=?,status=?,message=?,job_id=?,output_json=?
                   WHERE id=?""",
                (now, status, message, job_id, serialized_outputs, existing[0]),
            )
        else:
            db.execute(
                """INSERT INTO autopilot_runs
                   (id,autopilot_id,started_at,finished_at,status,message,task_id,job_id,output_json)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (uuid.uuid4().hex[:12], item_id, now, now, status, message,
                 task_id, job_id, serialized_outputs),
            )
        db.commit()


def claim_manual(db_path: Path, item_id: str):
    """Legacy state-only claim retained for compatibility; API uses enqueue_manual_run."""
    now = datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path, timeout=20, isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT last_status FROM autopilots WHERE id=?", (item_id,)).fetchone()
        if not row:
            db.commit()
            return "missing"
        if row[0] in {"queued", "running"}:
            db.commit()
            return row[0]
        db.execute(
            "UPDATE autopilots SET last_status='running',last_message='Manuel çalıştırma başlatıldı',updated_at=? WHERE id=?",
            (now, item_id),
        )
        db.commit()
    return "claimed"


def mark_running(db_path: Path, item_id: str):
    now = datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path, timeout=20) as db:
        db.execute(
            """UPDATE autopilots SET last_status='running',last_message='Autopilot worker görevi devraldı',
               updated_at=? WHERE id=? AND last_status IN ('queued','running')""",
            (now, item_id),
        )
        db.commit()


def get_run_by_task(db_path: Path, task_id: str):
    with sqlite3.connect(db_path, timeout=20) as db:
        row = db.execute(
            """SELECT id,autopilot_id,started_at,finished_at,status,message,task_id,job_id,output_json
               FROM autopilot_runs WHERE task_id=? ORDER BY finished_at DESC LIMIT 1""",
            (task_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row[0], "autopilot_id": row[1], "started_at": row[2], "finished_at": row[3],
        "status": row[4], "message": row[5], "task_id": row[6], "job_id": row[7],
        "outputs": json.loads(row[8] or "[]"),
    }
