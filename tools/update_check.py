from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from app.updater import check_for_updates
    state = check_for_updates()
    if state.get("check_failed"):
        print("[UPDATE] GitHub kontrolu basarisiz: " + state.get("error", ""))
        raise SystemExit(2)
    if state.get("available"):
        print("[UPDATE] Yeni surum mevcut: " + str(state.get("latest_version")))
        print("[UPDATE] Uygulamayi acip guncelleme bildiriminden onaylayin.")
    else:
        print("[UPDATE] Uygulama guncel.")
except Exception as exc:
    print("[UPDATE] Kontrol atlandi: " + str(exc))
    raise SystemExit(2)
