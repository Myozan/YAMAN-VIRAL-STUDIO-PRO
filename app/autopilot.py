"""Local-first Autopilot schedule storage and due-run claiming."""
from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def init_autopilot(db_path: Path):
    with sqlite3.connect(db_path, timeout=15) as db:
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
        db.commit()

def _next_run(frequency: str, publish_time: str, timezone_name: str, now=None):
    if timezone_name == "Europe/Istanbul":
        from datetime import timezone as dt_timezone
        tz = dt_timezone(timedelta(hours=3), "TRT")
    else:
        try: tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError: raise ValueError("Geçersiz saat dilimi.")
    now = now.astimezone(tz) if now else datetime.now(tz)
    hour, minute = [int(x) for x in publish_time.split(":")]
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now: candidate += timedelta(days=1)
    if frequency == "weekly":
        while candidate.weekday() != 0: candidate += timedelta(days=1)
    return candidate.isoformat()

def create_autopilot(db_path: Path, data: dict):
    now = datetime.now().astimezone().isoformat()
    item_id = uuid.uuid4().hex[:12]
    next_run = _next_run(data["frequency"], data["publish_time"], data["timezone"])
    with sqlite3.connect(db_path, timeout=15) as db:
        db.execute("""INSERT INTO autopilots
        (id,name,niche,language,clips,min_seconds,max_seconds,platforms_json,frequency,publish_time,timezone,enabled,next_run,created_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (item_id,data["name"],data["niche"],data["language"],data["clips"],data["min_seconds"],data["max_seconds"],
         json.dumps(data["platforms"]),data["frequency"],data["publish_time"],data["timezone"],int(data["enabled"]),next_run,now,now))
        db.commit()
    return get_autopilot(db_path,item_id)

def _row(row):
    if not row: return None
    keys=("id","name","niche","language","clips","min_seconds","max_seconds","platforms_json","frequency","publish_time","timezone","enabled","next_run","last_run","last_status","last_message","processed_json","created_at","updated_at")
    d=dict(zip(keys,row)); d["platforms"]=json.loads(d.pop("platforms_json")); d["processed_files"]=json.loads(d.pop("processed_json")); d["enabled"]=bool(d["enabled"]); return d

def list_autopilots(db_path: Path):
    with sqlite3.connect(db_path, timeout=15) as db:
        rows=db.execute("SELECT id,name,niche,language,clips,min_seconds,max_seconds,platforms_json,frequency,publish_time,timezone,enabled,next_run,last_run,last_status,last_message,processed_json,created_at,updated_at FROM autopilots ORDER BY created_at DESC").fetchall()
        items=[_row(r) for r in rows]
        for item in items:
            last=db.execute("SELECT output_json FROM autopilot_runs WHERE autopilot_id=? ORDER BY started_at DESC LIMIT 1",(item["id"],)).fetchone()
            item["last_outputs"]=json.loads(last[0]) if last and last[0] else []
    return items

def get_autopilot(db_path: Path, item_id: str):
    with sqlite3.connect(db_path, timeout=15) as db:
        row=db.execute("SELECT id,name,niche,language,clips,min_seconds,max_seconds,platforms_json,frequency,publish_time,timezone,enabled,next_run,last_run,last_status,last_message,processed_json,created_at,updated_at FROM autopilots WHERE id=?",(item_id,)).fetchone()
    return _row(row)

def update_autopilot(db_path: Path, item_id: str, changes: dict):
    current=get_autopilot(db_path,item_id)
    if not current: return None
    current.update(changes)
    now=datetime.now().astimezone().isoformat()
    next_run=_next_run(current["frequency"],current["publish_time"],current["timezone"])
    with sqlite3.connect(db_path,timeout=15) as db:
        db.execute("""UPDATE autopilots SET name=?,niche=?,language=?,clips=?,min_seconds=?,max_seconds=?,platforms_json=?,frequency=?,publish_time=?,timezone=?,enabled=?,next_run=?,updated_at=? WHERE id=?""",
        (current["name"],current["niche"],current["language"],current["clips"],current["min_seconds"],current["max_seconds"],json.dumps(current["platforms"]),current["frequency"],current["publish_time"],current["timezone"],int(current["enabled"]),next_run,now,item_id)); db.commit()
    return get_autopilot(db_path,item_id)

def delete_autopilot(db_path: Path, item_id: str):
    with sqlite3.connect(db_path,timeout=15) as db:
        cur=db.execute("DELETE FROM autopilots WHERE id=?",(item_id,)); db.commit()
    return cur.rowcount > 0

def claim_due(db_path: Path):
    now=datetime.now().astimezone()
    claimed=[]
    with sqlite3.connect(db_path,timeout=15,isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        rows=db.execute("SELECT id,name,niche,language,clips,min_seconds,max_seconds,platforms_json,frequency,publish_time,timezone,enabled,next_run,last_run,last_status,last_message,processed_json,created_at,updated_at FROM autopilots WHERE enabled=1").fetchall()
        for row in rows:
            item=_row(row)
            try: due=datetime.fromisoformat(item["next_run"])
            except Exception: continue
            if due <= now:
                next_run=_next_run(item["frequency"],item["publish_time"],item["timezone"],now)
                db.execute("UPDATE autopilots SET next_run=?,last_status='running',last_message='Zamanlanmış üretim başlatıldı',updated_at=? WHERE id=?",
                           (next_run,now.isoformat(),item["id"]))
                item["next_run"]=next_run; claimed.append(item)
        db.commit()
    return claimed

def finish_run(db_path: Path, item_id: str, status: str, message: str, task_id=None, job_id=None, outputs=None, processed_file=None):
    now=datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path,timeout=15) as db:
        row=db.execute("SELECT processed_json FROM autopilots WHERE id=?",(item_id,)).fetchone()
        processed=json.loads(row[0]) if row else []
        if processed_file and processed_file not in processed: processed=(processed+[processed_file])[-250:]
        db.execute("UPDATE autopilots SET last_run=?,last_status=?,last_message=?,processed_json=?,updated_at=? WHERE id=?",
                   (now,status,message,json.dumps(processed),now,item_id))
        db.execute("INSERT INTO autopilot_runs(id,autopilot_id,started_at,finished_at,status,message,task_id,job_id,output_json) VALUES(?,?,?,?,?,?,?,?,?)",
                   (uuid.uuid4().hex[:12],item_id,now,now,status,message,task_id,job_id,json.dumps(outputs or [])))
        db.commit()

def claim_manual(db_path: Path, item_id: str):
    now=datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path,timeout=15,isolation_level=None) as db:
        db.execute("BEGIN IMMEDIATE")
        row=db.execute("SELECT last_status FROM autopilots WHERE id=?",(item_id,)).fetchone()
        if not row:
            db.commit()
            return "missing"
        if row[0] == "running":
            db.commit()
            return "running"
        db.execute("UPDATE autopilots SET last_status='running',last_message='Manuel çalıştırma başlatıldı',updated_at=? WHERE id=?",(now,item_id))
        db.commit()
    return "claimed"
