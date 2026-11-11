from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from app.secure_http import request_public_https

REPOSITORY = "Myozan/YAMAN-VIRAL-STUDIO-PRO"
UPDATE_BRANCH = "import/v1.8.0-premium-ai-creator-studio"
CURRENT_VERSION = "1.8.0"
APP_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = APP_ROOT / "workspace"
UPDATE_STATE_FILE = WORKSPACE / "update-state.json"
UPDATE_LOCK = WORKSPACE / "update.lock"
GITHUB_API = "https://api.github.com"

# User-owned data must never be replaced by an application update.
PRESERVED_NAMES = {
    ".git", ".venv", "venv", ".env", "workspace",
    "settings.local.json", "platform_profiles.json",
    "auto-editor.exe", "data", "uploads", "downloads",
    "output", "outputs", "media", "user-data",
}
IGNORED_BACKUP = ("__pycache__", "*.pyc", ".git", ".venv", "venv", "workspace")


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "YAMAN-VIRAL-STUDIO-PRO-Updater",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_json(url: str, timeout: int = 15) -> dict[str, Any]:
    response = request_public_https("GET", url, headers=_github_headers(), timeout=timeout, max_redirects=3)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("GitHub yanıtı beklenen biçimde değil.")
    return payload


def _get_branch_version(commit_data: dict[str, Any] | None = None) -> str:
    # The branch is pinned to the expected product version. A matching version.json
    # is validated by the downloaded commit before any application files are touched.
    return CURRENT_VERSION


def get_current_build() -> dict[str, str]:
    marker = APP_ROOT / "version.json"
    if marker.is_file():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            return {
                "version": str(data.get("version", CURRENT_VERSION)),
                "branch": str(data.get("branch", UPDATE_BRANCH)),
                "commit": str(data.get("commit", "unknown")),
            }
        except (OSError, ValueError, TypeError):
            pass
    return {"version": CURRENT_VERSION, "branch": UPDATE_BRANCH, "commit": "unknown"}


def check_for_updates() -> dict[str, Any]:
    current = get_current_build()
    try:
        commit_data = _get_json(f"{GITHUB_API}/repos/{REPOSITORY}/commits/{quote(UPDATE_BRANCH, safe='')}")
        latest_sha = str(commit_data.get("sha", ""))[:40]
        if len(latest_sha) != 40:
            raise ValueError("GitHub dalı geçerli commit SHA döndürmedi.")

        parents = commit_data.get("parents") or []
        parent_sha = str(parents[0].get("sha", "")) if parents else ""
        commit_info = commit_data.get("commit") or {}
        message = str(commit_info.get("message") or "Yeni güncelleme").splitlines()[0][:180]
        published_at = str((commit_info.get("committer") or {}).get("date") or "")
        latest_version = _get_branch_version()

        installed_sha = current.get("commit", "unknown")
        # A ZIP install contains the parent SHA in version.json: that parent
        # identifies the exact release commit that produced the ZIP archive.
        is_exact_archive_build = (
            installed_sha not in ("", "unknown")
            and installed_sha == parent_sha
            and current.get("version") == latest_version
        )
        available = installed_sha != latest_sha and not is_exact_archive_build
        state = {
            "available": available,
            "current_version": current["version"],
            "latest_version": latest_version,
            "current_commit": installed_sha,
            "latest_commit": latest_sha,
            "branch": UPDATE_BRANCH,
            "message": message,
            "release_notes": message,
            "published_at": published_at,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "release_url": f"https://github.com/{REPOSITORY}/releases",
            "compare_url": f"https://github.com/{REPOSITORY}/compare/{installed_sha}...{latest_sha}",
        }
        WORKSPACE.mkdir(parents=True, exist_ok=True)
        UPDATE_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return state
    except Exception as exc:
        return {
            "available": False,
            "check_failed": True,
            "current_version": current["version"],
            "latest_version": current["version"],
            "branch": UPDATE_BRANCH,
            "error": f"GitHub güncellemeleri kontrol edilemedi: {exc}",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }


def _safe_extract(zip_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError("Güncelleme arşivinde güvenli olmayan dosya yolu bulundu.")
        archive.extractall(destination)
    children = list(destination.iterdir())
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return destination


def _is_preserved(relative: Path) -> bool:
    return any(part in PRESERVED_NAMES for part in relative.parts) or relative.name in PRESERVED_NAMES


def schedule_restart(delay_seconds: int = 6) -> bool:
    """Restart the local Windows launcher after the HTTP response has time to return."""
    if os.name != "nt":
        return False
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    server_pid = os.getpid()
    launcher = APP_ROOT / "run_windows.bat"
    if not launcher.is_file():
        return False
    restart_script = WORKSPACE / "restart_after_update.bat"
    delay = max(5, min(int(delay_seconds), 30))
    script = (
        "@echo off\r\n"
        f"timeout /t {delay} /nobreak >nul\r\n"
        f"taskkill /PID {server_pid} /F >nul 2>nul\r\n"
        "timeout /t 2 /nobreak >nul\r\n"
        f'start "" "{launcher}"\r\n'
    )
    restart_script.write_text(script, encoding="utf-8")
    flags = getattr(subprocess, "DETACHED_PROCESS", 0x00000008) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    subprocess.Popen(
        ["cmd.exe", "/d", "/c", str(restart_script)],
        cwd=str(APP_ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=flags,
    )
    return True


def apply_update(expected_commit: str = "") -> dict[str, Any]:
    if os.name != "nt":
        raise RuntimeError("Otomatik dosya güncellemesi şu anda Windows kurulumlarında kullanılabilir.")
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    if UPDATE_LOCK.exists():
        raise RuntimeError("Başka bir güncelleme işlemi zaten çalışıyor.")
    UPDATE_LOCK.write_text(str(os.getpid()), encoding="utf-8")

    temp_root: Path | None = None
    backup: Path | None = None
    touched: list[Path] = []
    try:
        state = check_for_updates()
        if state.get("check_failed"):
            raise RuntimeError(state.get("error", "GitHub güncellemesi kontrol edilemedi."))
        latest_sha = str(state.get("latest_commit", ""))
        if expected_commit and expected_commit != latest_sha:
            raise RuntimeError("GitHub dalı kontrol sırasında değişti. Güncelleme listesini yenileyin.")
        if not state.get("available"):
            return {
                "updated": False,
                "message": "Bu kurulum zaten güncel.",
                "version": state.get("latest_version"),
            }

        temp_root = Path(tempfile.mkdtemp(prefix="yaman-studio-update-"))
        archive_path = temp_root / "update.zip"
        # Pin download to the exact SHA that the user approved, never to a moving branch.
        url = f"https://api.github.com/repos/{REPOSITORY}/zipball/{latest_sha}"
        response = request_public_https("GET", url, headers={
            "User-Agent": "YAMAN-VIRAL-STUDIO-PRO-Updater",
            "Accept": "application/vnd.github+json",
        }, timeout=90, stream=True, max_redirects=3)
        try:
            response.raise_for_status()
            with archive_path.open("wb") as output:
                shutil.copyfileobj(response.raw, output)
        finally:
            response.close()

        extracted = _safe_extract(archive_path, temp_root / "source")
        if not (extracted / "app" / "main.py").is_file() or not (extracted / "web" / "index.html").is_file():
            raise RuntimeError("İndirilen GitHub paketi geçerli YAMAN Studio sürümü değil.")
        remote_marker = extracted / "version.json"
        if not remote_marker.is_file():
            raise RuntimeError("Güncelleme paketi version.json içermiyor; kurulum iptal edildi.")
        remote_version_data = json.loads(remote_marker.read_text(encoding="utf-8"))
        if str(remote_version_data.get("version", "")) != CURRENT_VERSION:
            raise RuntimeError("İndirilen paketin sürümü beklenen v1.8.0 ile eşleşmiyor.")
        remote_branch = str(remote_version_data.get("branch", ""))
        if remote_branch != UPDATE_BRANCH:
            raise RuntimeError("İndirilen paket beklenen GitHub dalından gelmiyor.")

        staged = temp_root / "staged"
        shutil.copytree(
            extracted,
            staged,
            ignore=shutil.ignore_patterns(".git", ".github", "workspace", ".env", ".venv", "venv", "__pycache__", "*.pyc"),
        )

        backup = APP_ROOT.parent / f"{APP_ROOT.name}-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copytree(APP_ROOT, backup, ignore=shutil.ignore_patterns(*IGNORED_BACKUP))

        old_requirements = backup / "requirements.txt"
        new_requirements = staged / "requirements.txt"
        requirements_changed = (
            old_requirements.is_file()
            and new_requirements.is_file()
            and hashlib.sha256(old_requirements.read_bytes()).digest()
            != hashlib.sha256(new_requirements.read_bytes()).digest()
        )

        for source in staged.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(staged)
            if _is_preserved(relative):
                continue
            destination = APP_ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            touched.append(relative)
            shutil.copy2(source, destination)

        marker = {
            "version": state.get("latest_version") or CURRENT_VERSION,
            "branch": UPDATE_BRANCH,
            "commit": latest_sha,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        marker_path = APP_ROOT / "version.json"
        if Path("version.json") not in touched:
            touched.append(Path("version.json"))
        marker_path.write_text(json.dumps(marker, ensure_ascii=False, indent=2), encoding="utf-8")

        if requirements_changed:
            python = APP_ROOT / ".venv" / "Scripts" / "python.exe"
            if python.is_file():
                subprocess.run(
                    [str(python), "-m", "pip", "install", "-r", str(APP_ROOT / "requirements.txt")],
                    cwd=APP_ROOT, check=True, timeout=900,
                )

        return {
            "updated": True,
            "version": marker["version"],
            "commit": latest_sha,
            "backup": str(backup),
            "restart_required": True,
            "message": "Güncelleme kuruldu. Uygulamayı yeniden başlatın.",
        }
    except Exception:
        # Restore only files touched by this update, leaving user data untouched.
        if backup and backup.exists():
            for relative in reversed(touched):
                destination = APP_ROOT / relative
                previous = backup / relative
                try:
                    if previous.is_file():
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(previous, destination)
                    elif destination.is_file():
                        destination.unlink()
                except OSError:
                    pass
        raise
    finally:
        try:
            UPDATE_LOCK.unlink(missing_ok=True)
        except OSError:
            pass
        if temp_root and temp_root.exists():
            shutil.rmtree(temp_root, ignore_errors=True)
