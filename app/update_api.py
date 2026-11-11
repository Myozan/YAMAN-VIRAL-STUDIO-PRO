from __future__ import annotations

import threading
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app import updater

router = APIRouter(prefix="/api/update", tags=["updates"])
_update_lock = threading.Lock()


class ApplyUpdateRequest(BaseModel):
    expected_commit: str = Field(min_length=40, max_length=40)


@router.get("/status")
def update_status():
    return updater.check_for_updates()


@router.post("/apply")
def apply_update(req: ApplyUpdateRequest):
    if not _update_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Bir güncelleme işlemi zaten çalışıyor.")
    try:
        result = updater.apply_update(req.expected_commit)
        if result.get("updated"):
            try:
                result["restart_scheduled"] = updater.schedule_restart()
            except Exception as restart_error:
                result["restart_scheduled"] = False
                result["restart_error"] = str(restart_error)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        _update_lock.release()
