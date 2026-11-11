from __future__ import annotations
import asyncio, ctypes, html, json, math, os, platform, re, secrets, hashlib, base64, shutil, sqlite3, subprocess, sys, time, uuid, threading
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlencode
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from fastapi import Request
from fastapi.responses import HTMLResponse
from cryptography.fernet import Fernet
import yt_dlp
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl
from app.learning import ViralLearningEngine
from app.agents import AGENT_CATALOG, run_agent_team
from app.framing import render_face_tracked
from app import autopilot as autopilot_store
from app import content_factory, visual_factory
from app import updater as update_manager
from app.update_api import router as update_router

# Windows CUDA runtime DLLs are shipped inside this project's isolated venv.
# Keep AddDllDirectory handles alive so CTranslate2 can resolve cuBLAS/cuDNN.
_cuda_dll_handles = []
def configure_cuda_runtime():
    if os.name != "nt":
        return
    nvidia_root = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia"
    for relative in ("cublas/bin", "cudnn/bin", "cuda_nvrtc/bin"):
        dll_dir = nvidia_root / relative
        if dll_dir.is_dir():
            os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ.get("PATH", "")
            try:
                _cuda_dll_handles.append(os.add_dll_directory(str(dll_dir)))
            except (AttributeError, OSError):
                pass
    for dll in ("cublas64_12.dll", "cudnn64_9.dll", "cudnn_ops64_9.dll",
                "cudnn_cnn64_9.dll", "cudnn_adv64_9.dll"):
        try:
            ctypes.WinDLL(dll)
        except OSError:
            pass

configure_cuda_runtime()
from faster_whisper import WhisperModel

BASE = Path(__file__).resolve().parent.parent
WORK = BASE / "workspace"
WORK.mkdir(exist_ok=True)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
MAX_DOWNLOAD_MB = int(os.getenv("MAX_DOWNLOAD_MB", "2048"))
DOWNLOADS_DIR = Path.home() / "Downloads"
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".mpg", ".mpeg"}
_local_settings = BASE / "settings.local.json"
if _local_settings.exists():
    try:
        _cfg = json.loads(_local_settings.read_text(encoding="utf-8"))
        OLLAMA_MODEL = str(_cfg.get("ollama_model", OLLAMA_MODEL))
        WHISPER_MODEL = str(_cfg.get("whisper_model", WHISPER_MODEL))
        WHISPER_DEVICE = str(_cfg.get("whisper_device", WHISPER_DEVICE))
    except Exception:
        pass

PLATFORMS = {
    "youtube": {"label": "YouTube Shorts", "width": 1080, "height": 1920, "margin": 180, "max_seconds": 180},
    "instagram": {"label": "Instagram Reels", "width": 1080, "height": 1920, "margin": 260, "max_seconds": 180},
    "tiktok": {"label": "TikTok", "width": 1080, "height": 1920, "margin": 300, "max_seconds": 180},
}
PLATFORM_PROFILES = {key: dict(value) for key, value in PLATFORMS.items()}
_PROFILE_FILE = BASE / "platform_profiles.json"
if _PROFILE_FILE.exists():
    try:
        for key, value in json.loads(_PROFILE_FILE.read_text(encoding="utf-8")).items():
            if key in PLATFORM_PROFILES and isinstance(value, dict):
                PLATFORM_PROFILES[key].update({k: value[k] for k in ("width", "height", "max_seconds") if k in value})
    except Exception:
        pass
_scheduler_stop = threading.Event()
_scheduler_thread = None

@asynccontextmanager
async def app_lifespan(application):
    """Own process-level background services for the FastAPI application."""
    asyncio.get_running_loop().set_exception_handler(_windows_disconnect_exception_handler)
    _scheduler_stop.clear()
    start_autopilot_scheduler()
    try:
        yield
    finally:
        _scheduler_stop.set()
        thread = _scheduler_thread
        if thread and thread.is_alive():
            thread.join(timeout=2)


app = FastAPI(title="YAMAN VIRAL STUDIO PRO", version="1.8.0", lifespan=app_lifespan)

def _windows_disconnect_exception_handler(loop, context):
    """Ignore only expected Windows Proactor peer-reset events on client disconnect."""
    exc = context.get("exception")
    message = str(context.get("message", ""))
    if (os.name == "nt" and isinstance(exc, ConnectionResetError)
            and getattr(exc, "winerror", None) == 10054
            and "_ProactorBasePipeTransport._call_connection_lost" in message):
        return
    loop.default_exception_handler(context)

app.mount("/assets", StaticFiles(directory=BASE / "web"), name="assets")
app.include_router(update_router)

@app.get("/sw.js", include_in_schema=False)
def pwa_service_worker():
    """Serve the root-scoped service worker with the required scope header."""
    return FileResponse(
        BASE / "web" / "sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
    )
app.mount("/workspace", StaticFiles(directory=WORK), name="workspace")
jobs: dict[str, dict[str, Any]] = {}
task_states: dict[str, dict[str, Any]] = {}
_task_state_lock = threading.RLock()
TASK_DB = WORK / "orchestration.sqlite3"
_cancelled_tasks: set[str] = set()
_cpu_sample = None

def init_task_store():
    with sqlite3.connect(TASK_DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, status TEXT NOT NULL, percent INTEGER NOT NULL, stage TEXT NOT NULL, payload_json TEXT NOT NULL DEFAULT '{}')")
        db.execute("CREATE TABLE IF NOT EXISTS task_events (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, event_type TEXT NOT NULL, created_at TEXT NOT NULL, payload_json TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS oauth_states (state TEXT PRIMARY KEY, platform TEXT NOT NULL, verifier TEXT NOT NULL, redirect_uri TEXT NOT NULL, created_at REAL NOT NULL)")
        rows = db.execute("SELECT task_id,payload_json FROM tasks WHERE status IN ('queued','running')").fetchall()
        for task_id, payload in rows:
            state = json.loads(payload or "{}")
            now = datetime.now(timezone.utc).isoformat()
            state.update({"status":"interrupted","stage":"Application restarted; task can be retried","error":"Process restarted before completion"})
            db.execute("UPDATE tasks SET status='interrupted',updated_at=?,stage=?,payload_json=? WHERE task_id=?",
                (now,state["stage"],json.dumps(state,ensure_ascii=False),task_id))
            db.execute("INSERT INTO task_events(task_id,event_type,created_at,payload_json) VALUES(?,?,?,?)",
                (task_id,"interrupted",now,json.dumps(state,ensure_ascii=False)))
        db.commit()

init_task_store()
learning = ViralLearningEngine(WORK / "viral_learning.sqlite3")
autopilot_store.init_autopilot(TASK_DB)


def load_saved_jobs():
    """Restore completed analysis jobs so clips can still be rendered after an app restart."""
    root = WORK.resolve()
    for meta_file in WORK.glob("*/job.json"):
        try:
            folder = meta_file.parent.resolve()
            if folder.parent != root:
                continue
            data = json.loads(meta_file.read_text(encoding="utf-8-sig"))
            video = Path(data.get("video", "")).resolve()
            if video.parent != folder or not video.is_file():
                continue
            if not isinstance(data.get("clips"), list) or not isinstance(data.get("segments"), list):
                continue
            jobs[folder.name] = {
                "folder": str(folder), "video": str(video),
                "duration": float(data.get("duration", 0)),
                "language": str(data.get("language", "unknown")),
                "segments": data["segments"], "clips": data["clips"],
            }
        except Exception:
            continue


load_saved_jobs()


def save_job(job_id: str, job: dict):
    folder = Path(job["folder"])
    payload = {
        "job_id": job_id, "folder": str(folder), "video": str(job["video"]),
        "duration": job["duration"], "language": job["language"],
        "segments": job["segments"], "clips": job["clips"],
    }
    temp = folder / "job.json.tmp"
    temp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    temp.replace(folder / "job.json")
_whisper = None

class AnalyzeRequest(BaseModel):
    url: HttpUrl | None = None
    clips: int = Field(default=8, ge=1, le=20)
    min_seconds: int = Field(default=20, ge=10, le=60)
    max_seconds: int = Field(default=55, ge=20, le=180)
    language: str = "auto"

class LocalAnalyzeRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    clips: int = Field(default=8, ge=1, le=20)
    min_seconds: int = Field(default=20, ge=10, le=60)
    max_seconds: int = Field(default=55, ge=20, le=180)
    language: str = "auto"

class RenderRequest(BaseModel):
    job_id: str
    clip_id: int
    platforms: list[str] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])
    captions: bool = True

class PlatformProfileRequest(BaseModel):
    platform: str
    aspect_ratio: str = Field(default="9:16", pattern="^(9:16|1:1|16:9)$")
    resolution: int = Field(default=1080, ge=720, le=1080)
    max_seconds: int = Field(default=180, ge=15, le=180)

class PerformanceRequest(BaseModel):
    clip_fingerprint: str = Field(min_length=8, max_length=128)
    platform: str
    views: int = Field(ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    avg_watch_seconds: float = Field(default=0, ge=0)
    video_seconds: float = Field(gt=0)

class SummaryRequest(BaseModel):
    job_id: str
    target_seconds: int = Field(default=90, ge=30, le=180)
    format: str = Field(default="smart", pattern="^(smart|story|documentary|education|product)$")
    transition: str = Field(default="fade", pattern="^(fade|cut)$")
    captions: bool = True
    chapter_titles: bool = True


class AutopilotRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    niche: str = Field(min_length=2, max_length=160)
    language: str = Field(default="auto", pattern="^(auto|tr|en)$")
    clips: int = Field(default=5, ge=1, le=12)
    min_seconds: int = Field(default=20, ge=10, le=60)
    max_seconds: int = Field(default=55, ge=20, le=180)
    platforms: list[str] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])
    frequency: str = Field(default="daily", pattern="^(daily|weekly)$")
    publish_time: str = Field(default="09:00", pattern="^([01]\\d|2[0-3]):[0-5]\\d$")
    timezone: str = Field(default="Europe/Istanbul", min_length=3, max_length=80)
    enabled: bool = True

class TrendResearchRequest(BaseModel):
    niche: str = Field(min_length=2, max_length=160)
    region: str = Field(default="TR", pattern="^(TR|US|GB|DE)$")
    limit: int = Field(default=18, ge=1, le=30)

class ScriptRequest(BaseModel):
    niche: str = Field(min_length=2, max_length=160)
    topic: str = Field(min_length=3, max_length=300)
    language: str = Field(default="tr", pattern="^(tr|en)$")
    duration: int = Field(default=60, ge=15, le=180)

class CompleteVideoRequest(BaseModel):
    niche: str = Field(min_length=2, max_length=160)
    topic: str = Field(default="", max_length=300)
    region: str = Field(default="TR", pattern="^(TR|US|GB|DE)$")
    language: str = Field(default="tr", pattern="^(tr|en)$")
    duration: int = Field(default=60, ge=15, le=90)
    voice: str = Field(default="tr-TR-EmelNeural", max_length=80)
    captions: bool = True
    auto_trend: bool = True
    style: str = Field(default="shorts", pattern="^(shorts|trailer)$")
    visual_provider: str = Field(default="motion", pattern="^(motion|runway|pexels)$")
    shot_count: int = Field(default=5, ge=2, le=8)
    generate_music: bool = False

class VoiceoverRequest(BaseModel):
    text: str = Field(min_length=10, max_length=12000)
    voice: str = Field(default="tr-TR-EmelNeural", max_length=80)

class TeamRequest(BaseModel):
    job_id: str
    clip_id: int
    platforms: list[str] = Field(default_factory=lambda: ['youtube','instagram','tiktok'])

class OAuthAppRequest(BaseModel):
    platform: str
    client_id: str = Field(min_length=5, max_length=300)
    client_secret: str = Field(min_length=5, max_length=500)

class PublishRequest(BaseModel):
    job_id: str
    clip_id: int
    title: str = Field(min_length=1, max_length=2200)
    description: str = Field(default="", max_length=5000)
    privacy: str = Field(default="private", pattern="^(private|unlisted|public|SELF_ONLY|MUTUAL_FOLLOW_FRIENDS|PUBLIC_TO_EVERYONE)$")
    confirm_publish: bool = False
    media_url: str | None = None
    is_aigc: bool = False

class SettingsRequest(BaseModel):
    ollama_model: str = Field(min_length=1, max_length=100)
    whisper_model: str = Field(min_length=1, max_length=30)
    whisper_device: str = Field(default="auto", pattern="^(auto|cpu|cuda)$")

class MetadataRequest(BaseModel):
    job_id: str
    clip_id: int
    platforms: list[str] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])

def command(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-3000:])

def require_binary(name: str):
    if not shutil.which(name):
        raise RuntimeError(f"{name} bulunamadı. Kurup PATH'e ekleyin.")

def get_whisper():
    global _whisper
    if _whisper is None:
        if WHISPER_DEVICE == "cuda":
            # 4 GB GTX 1650: mixed INT8/FP16 keeps VRAM usage controlled.
            _whisper = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="int8_float16")
        elif WHISPER_DEVICE == "auto":
            try:
                _whisper = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="int8_float16")
            except Exception as gpu_error:
                print(f"CUDA unavailable; falling back to CPU: {gpu_error}", flush=True)
                _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        else:
            _whisper = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _whisper

def validate_youtube_url(url: str):
    """Accept only canonical HTTPS YouTube URLs; reject URL parser ambiguity."""
    parsed = urlparse(url)
    allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtube-nocookie.com"}
    host = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError:
        raise ValueError("Geçersiz YouTube bağlantı noktası.")
    if (parsed.scheme.lower() != "https" or host not in allowed
            or parsed.username is not None or parsed.password is not None
            or port not in (None, 443)):
        raise ValueError("Güvenlik nedeniyle yalnızca standart HTTPS YouTube bağlantıları kabul edilir.")
def download_video(url: str, folder: Path, progress_callback=None) -> Path:
    validate_youtube_url(url)
    def download_hook(data):
        if progress_callback and data.get("status") == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                progress_callback(8 + min(14, int(downloaded / total * 14)), "Video indiriliyor")
        elif progress_callback and data.get("status") == "finished":
            progress_callback(22, "Video indirildi, hazırlanıyor")
    opts = {
        "outtmpl": str(folder / "source.%(ext)s"),
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4", "noplaylist": True, "quiet": True,
        "no_warnings": True, "restrictfilenames": True,
        "max_filesize": MAX_DOWNLOAD_MB * 1024 * 1024,
        "progress_hooks": [download_hook],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = folder / "source.mp4"
        if path.exists():
            return path
        prepared = Path(ydl.prepare_filename(info))
        if prepared.exists():
            return prepared
        candidates = [p for p in folder.glob("source.*") if p.is_file()]
        if candidates:
            return candidates[0]
    raise RuntimeError("Video dosyası indirilemedi.")

def probe_media_info(path: Path) -> dict:
    """Inspect a media file and reject corrupt, empty or streamless outputs."""
    if not path.is_file() or path.stat().st_size < 1024:
        raise RuntimeError("Media output is missing or too small to be valid.")
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
         "-of", "json", str(path)],
        capture_output=True, text=True, timeout=30
    )
    if probe.returncode:
        raise RuntimeError("Media output could not be probed: " + probe.stderr[-1000:])
    try:
        data = json.loads(probe.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Media output has invalid duration metadata.") from exc
    streams = data.get("streams", [])
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError("Media output duration must be a finite positive number.")
    if not any(item.get("codec_type") == "video" for item in streams):
        raise RuntimeError("Media output contains no video stream.")
    return {"duration": duration, "streams": streams, "size_bytes": path.stat().st_size}


def probe_duration(path: Path) -> float:
    return float(probe_media_info(path)["duration"])

def transcribe(path: Path, language: str, progress_callback=None, duration: float = 0):
    model = get_whisper()
    lang = None if language == "auto" else language

    def run_transcription(use_vad: bool):
        segments, info = model.transcribe(
            str(path),
            language=lang,
            word_timestamps=False,
            beam_size=1,
            condition_on_previous_text=False,
            vad_filter=use_vad,
        )
        result = []
        for seg in segments:
            words = []
            if seg.words:
                for word in seg.words:
                    words.append({
                        "start": float(word.start),
                        "end": float(word.end),
                        "text": word.word.strip(),
                    })
            text = seg.text.strip()
            if text:
                result.append({
                    "start": float(seg.start),
                    "end": float(seg.end),
                    "text": text,
                    "words": words,
                })
            if progress_callback and duration:
                part = 36 + min(30, int(float(seg.end) / duration * 30))
                progress_callback(part, "Konuşma çözümleniyor · Whisper")
        return result, info.language

    result, detected_language = run_transcription(True)
    recognized_words = sum(len(item["text"].split()) for item in result)

    # VAD çok az konuşma bulursa filtresiz tekrar dene.
    if not result or recognized_words < 8:
        retry_result, retry_language = run_transcription(False)
        retry_words = sum(len(item["text"].split()) for item in retry_result)
        if retry_words > recognized_words:
            result, detected_language = retry_result, retry_language

    return result, detected_language

def heuristic_score(text: str) -> tuple[int, list[str]]:
    t = text.lower()
    score, reasons = 35, []
    hooks = ["ama", "çünkü", "aslında", "inanılmaz", "nasıl", "neden", "sır", "hata", "gerçek", "kimse", "however", "secret", "mistake", "why", "how"]
    hits = [w for w in hooks if w in t]
    score += min(25, len(hits) * 5)
    if hits: reasons.append("Merak uyandıran ifade")
    if "?" in text: score += 8; reasons.append("Soru / merak unsuru")
    if "!" in text: score += 4; reasons.append("Duygu / vurgu")
    n = len(text.split())
    if 35 <= n <= 120: score += 15; reasons.append("Kısa ve anlaşılır anlatım")
    elif n > 170: score -= 8
    if re.search(r"\d", text): score += 4; reasons.append("Somut bilgi veya sayı")
    return max(1, min(95, score)), reasons or ["Editoryal değerlendirme gerekli"]

def llm_json(prompt: str, timeout: int = 180, num_predict: int = 512):
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "think": False, "keep_alive": "5m", "options": {"num_predict": num_predict}},
            timeout=(4, timeout)
        )
        r.raise_for_status()
        return json.loads(r.json().get("response", "{}"))
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(503, f"Ollama servisine bağlanılamıyor ({OLLAMA_URL}). Ayarlar bölümünden bağlantıyı kontrol edin veya Ollama'yı başlatın.") from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(504, "Ollama yanıt süresi doldu. Model boyutunu veya işlem yükünü kontrol edin.") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(502, f"Ollama API hatası: {exc}") from exc

def rank_candidates(candidates: list[dict]) -> list[dict]:
    prompt = (
        "You are an expert short-form video editor. Rank transcript excerpts for standalone short videos. "
        "Score hook in first 2 seconds, clarity without missing context, curiosity/emotion, payoff, pacing. "
        "Do not promise virality. Return JSON object with key clips, array items id, score, hook, reason, title. "
        "Candidates: " + json.dumps([{"id": c["id"], "text": c["text"][:1200]} for c in candidates], ensure_ascii=False)
    )
    try:
        data = llm_json(prompt)
        values = data.get("clips", []) if isinstance(data, dict) else data
        by_id = {int(x["id"]): x for x in values if "id" in x}
        for c in candidates:
            x = by_id.get(c["id"])
            if x:
                c["score"] = max(0, min(100, int(x.get("score", c["score"]))))
                c["hook"] = str(x.get("hook", c["hook"]))
                c["reason"] = str(x.get("reason", c["reason"]))
                c["title"] = str(x.get("title", c["title"]))
    except Exception:
        pass
    return sorted(candidates, key=lambda x: x["score"], reverse=True)

def make_candidates(segments, duration, count, min_s, max_s):
    """Konuşma segmentlerinden esnek, sabit süreli klip adayları üretir."""
    candidates = []
    seen = set()

    if not segments or duration <= 0:
        return candidates

    # Adapt the minimum window to the actual source duration. Short videos
    # should still yield a valid candidate instead of failing before fallback.
    effective_min = min(int(min_s), 12, max(1, int(duration)))
    effective_max = max(int(max_s), effective_min)
    window_seconds = min(effective_max, max(effective_min, int(duration)))

    if window_seconds < effective_min:
        return candidates

    ordered_segments = sorted(
        segments,
        key=lambda item: float(item.get("start", 0.0))
    )

    for seg in ordered_segments:
        start = max(0.0, float(seg["start"]) - 1.0)
        end = min(float(duration), start + window_seconds)

        if end - start < effective_min:
            continue

        chunk = [
            item for item in ordered_segments
            if float(item["start"]) < end and float(item["end"]) > start
        ]
        if not chunk:
            continue

        text = " ".join(
            item.get("text", "").strip()
            for item in chunk
            if item.get("text", "").strip()
        ).strip()

        if len(text.split()) < 3:
            continue

        key = round(start / 8)
        if key in seen:
            continue
        seen.add(key)

        score, reasons = heuristic_score(text)
        candidates.append({
            "id": len(candidates) + 1,
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": round(end - start, 1),
            "text": text,
            "score": score,
            "hook": text[:100],
            "title": text[:65],
            "reason": ", ".join(reasons),
        })

    # Sparse transcript fallback: retain short but genuine speech instead of failing analysis.
    if not candidates:
        usable = [x for x in ordered_segments if len(str(x.get("text", "")).split()) >= 2]
        if usable:
            first = usable[0]
            start = max(0.0, float(first.get("start", 0.0)) - 0.8)
            end = min(float(duration), max(float(first.get("end", start)), start + min(12.0, duration)))
            group = [x for x in usable if float(x.get("start", 0)) < end and float(x.get("end", 0)) > start]
            text = " ".join(str(x.get("text", "")).strip() for x in group).strip()
            if len(text.split()) >= 2 and end > start:
                score, reasons = heuristic_score(text)
                candidates.append({"id": 1, "start": round(start, 2), "end": round(end, 2),
                    "duration": round(end-start, 1), "text": text, "score": score,
                    "hook": text[:100], "title": text[:65],
                    "reason": "K\u0131sa konu\u015fma i\u00e7in otomatik yedek kesit"})
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:max(count * 5, count)]

def ass_time(seconds: float) -> str:
    cs = max(0, int(seconds * 100))
    h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

def ass_escape(s: str) -> str:
    return s.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", " ")

def create_ass(segments: list[dict], clip: dict, out: Path, margin: int):
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Arial,76,&H00FFFFFF,&H0000D7FF,&H0010141D,&H99000000,1,0,1,5,2,2,90,90,{margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    rows = []
    start, end = clip["start"], clip["end"]
    for seg in segments:
        if seg["end"] <= start or seg["start"] >= end:
            continue
        words = [w for w in seg.get("words", []) if w["end"] > start and w["start"] < end]
        if not words:
            text = ass_escape(seg["text"])
        else:
            bits = []
            for w in words:
                duration = max(1, int((min(w["end"], end) - max(w["start"], start)) * 100))
                bits.append(r"{\k" + str(duration) + "}" + ass_escape(w["text"]) + " ")
            text = "".join(bits).strip()
        a = max(0, seg["start"] - start)
        b = min(end, seg["end"]) - start
        if b > a:
            rows.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Viral,,0,0,0,,{text}")
    out.write_text(header + "\n".join(rows) + "\n", encoding="utf-8-sig")

def escape_filter_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")

def render_variant(job: dict, clip: dict, platform: str, captions: bool, face_tracking: bool = False) -> Path:
    profile = PLATFORM_PROFILES[platform]
    folder = Path(job["folder"])
    out = folder / f"clip_{clip['id']}_{platform}.mp4"
    source_video = Path(job["video"])
    render_clip = dict(clip)
    render_clip["duration"] = min(float(clip["duration"]), float(profile.get("max_seconds", 180)))
    render_clip["end"] = float(render_clip.get("start", 0)) + render_clip["duration"]
    if face_tracking:
        tracked = folder / ("clip_" + str(clip["id"]) + "_" + platform + "_tracked.mp4")
        render_face_tracked(source_video, tracked, render_clip["start"], render_clip["duration"], profile["width"], profile["height"])
        source_video = tracked
    vf = f"scale={profile['width']}:{profile['height']}:force_original_aspect_ratio=increase,crop={profile['width']}:{profile['height']},setsar=1"
    if captions:
        ass = folder / f"clip_{clip['id']}_{platform}.ass"
        create_ass(job["segments"], render_clip, ass, profile["margin"])
        vf += f",ass='{escape_filter_path(ass)}'"
    command([
        "ffmpeg", "-y", "-ss", str(render_clip["start"]), "-i", str(source_video), "-t", str(render_clip["duration"]),
        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)
    ])
    probe_media_info(out)
    return out

def fallback_metadata(clip: dict, platform: str):
    title = re.sub(r"\s+", " ", clip.get("title", "İzlemeden geçme!")).strip()[:95]
    tags = ["#shorts", "#reels", "#tiktok", "#keşfet", "#viral"]
    return {"title": title, "description": clip["text"][:400] + "\n\n" + " ".join(tags),
            "hashtags": tags, "platform": platform}

def cpu_hardware_info():
    """Return only the processor model for the compact CPU card."""
    try:
        if os.name == "nt":
            ps = "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)"
            proc = subprocess.run(["powershell","-NoProfile","-NonInteractive","-Command",ps],
                capture_output=True,text=True,timeout=3,
                creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
            if proc.returncode == 0 and proc.stdout.strip():
                return {"cpu_name":proc.stdout.strip().splitlines()[-1]}
    except Exception:
        pass
    return {"cpu_name":platform.processor() or "CPU"}


def system_metrics():
    """Windows sistem CPU ve RAM kullanımını anlık ölçer; harici paket gerektirmez."""
    global _cpu_sample
    try:
        class FILETIME(ctypes.Structure):
            _fields_ = [("low", ctypes.c_ulong), ("high", ctypes.c_ulong)]
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        mem = MEMORYSTATUSEX(); mem.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not kernel.GlobalMemoryStatusEx(ctypes.byref(mem)):
            raise OSError("RAM bilgisi okunamadı")
        idle1, kernel1, user1 = FILETIME(), FILETIME(), FILETIME()
        if not kernel.GetSystemTimes(ctypes.byref(idle1), ctypes.byref(kernel1), ctypes.byref(user1)):
            raise OSError("CPU bilgisi okunamadı")
        def ft(v): return (v.high << 32) | v.low
        first = (ft(idle1), ft(kernel1), ft(user1))
        time.sleep(0.12)
        idle2, kernel2, user2 = FILETIME(), FILETIME(), FILETIME()
        kernel.GetSystemTimes(ctypes.byref(idle2), ctypes.byref(kernel2), ctypes.byref(user2))
        second = (ft(idle2), ft(kernel2), ft(user2))
        total_delta = (second[1] - first[1]) + (second[2] - first[2])
        idle_delta = second[0] - first[0]
        cpu = 0 if total_delta <= 0 else max(0, min(100, round((total_delta - idle_delta) / total_delta * 100, 1)))
        total = mem.ullTotalPhys
        used = total - mem.ullAvailPhys
        result = {"cpu_percent": cpu, **cpu_hardware_info(), "ram_percent": round(used / total * 100, 1) if total else 0,
                  "ram_used_mb": round(used / 1048576), "ram_total_mb": round(total / 1048576)}
        smi = shutil.which("nvidia-smi") or r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
        if Path(smi).is_file():
            try:
                gpu = subprocess.run([smi, "--query-gpu=name,utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if gpu.returncode == 0 and gpu.stdout.strip():
                    parts = [x.strip() for x in gpu.stdout.strip().splitlines()[0].split(",")]
                    result.update({"gpu_available": True, "gpu_name": parts[0],
                        "gpu_percent": float(parts[1]), "vram_used_mb": float(parts[2]),
                        "vram_total_mb": float(parts[3])})
            except Exception:
                result["gpu_available"] = False
        else:
            result["gpu_available"] = False
        return result
    except Exception as exc:
        return {"error": str(exc)}

@app.get("/api/system/metrics")
def get_system_metrics():
    return system_metrics()

def ollama_status():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        response.raise_for_status()
        models = [item.get("name", "") for item in response.json().get("models", [])]
        return {"connected": True, "url": OLLAMA_URL, "model": OLLAMA_MODEL,
                "model_available": any(name == OLLAMA_MODEL or name.startswith(OLLAMA_MODEL + ":") for name in models),
                "models": models, "message": "Ollama bağlantısı hazır."}
    except requests.RequestException:
        return {"connected": False, "url": OLLAMA_URL, "model": OLLAMA_MODEL,
                "model_available": False, "models": [],
                "message": "Ollama çalışmıyor. Ollama uygulamasını Başlat menüsünden açın veya Başlat düğmesini kullanın."}

@app.get("/api/ollama/status")
def get_ollama_status():
    return ollama_status()

@app.post("/api/ollama/start")
def start_ollama():
    status = ollama_status()
    if status["connected"]:
        return {"started": False, **status}
    launch_args = None
    if os.name == "nt":
        gui = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama app.exe"
        if gui.is_file():
            launch_args = [str(gui)]
    cli = shutil.which("ollama")
    if launch_args is None and cli:
        launch_args = [cli, "serve"]
    if launch_args is None:
        raise HTTPException(503, "Ollama bulunamadı. https://ollama.com/download adresinden kurup tekrar deneyin.")
    try:
        subprocess.Popen(launch_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, close_fds=True)
    except OSError as exc:
        raise HTTPException(500, f"Ollama başlatılamadı: {exc}") from exc
    return {"started": True, "message": "Ollama başlatma isteği gönderildi. Birkaç saniye sonra durumu yenileyin."}

@app.get("/api/health")
def health():
    ffmpeg = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
    ollama = ollama_status()
    return {"ok": True, "ffmpeg": ffmpeg, "ollama": ollama["connected"], "ollama_status": ollama,
            "auto_editor": bool(shutil.which("auto-editor") or shutil.which("auto-editor.exe")),
            "model": OLLAMA_MODEL, "whisper_model": WHISPER_MODEL, "platforms": list(PLATFORMS)}

@app.get("/api/auto-editor/status")
def auto_editor_status():
    binary = shutil.which("auto-editor") or shutil.which("auto-editor.exe")
    return {"available": bool(binary), "binary": binary,
            "install_hint": "Resmî Windows auto-editor.exe dosyasını Releases sayfasından indirin ve PATH'e ekleyin."}

class AutoEditorRequest(BaseModel):
    file: str = Field(min_length=1, max_length=1000)
    margin_seconds: float = Field(default=0.3, ge=0.0, le=3.0)
    threshold: int = Field(default=6, ge=1, le=30)

@app.post("/api/auto-editor/silence-remove")
def auto_editor_silence_remove(req: AutoEditorRequest):
    binary = shutil.which("auto-editor") or shutil.which("auto-editor.exe")
    if not binary:
        raise HTTPException(503, "Auto-Editor kurulu değil. Resmî Windows sürümünü indirip PATH'e ekleyin.")
    relative = req.file.replace("\\", "/").lstrip("/")
    if relative.startswith("workspace/"):
        relative = relative[len("workspace/"):]
    source = (WORK / relative).resolve()
    try:
        source.relative_to(WORK.resolve())
    except ValueError:
        raise HTTPException(400, "Dosya yalnızca yerel workspace içinden seçilebilir.")
    if not source.is_file() or source.suffix.lower() != ".mp4":
        raise HTTPException(404, "İşlenecek MP4 dosyası bulunamadı.")
    output = source.with_name(source.stem + "_SILENCE_CUT.mp4")
    if output.exists():
        raise HTTPException(409, "Sessizlik temizlenmiş çıktı zaten var. Önce mevcut çıktıyı yeniden adlandırın.")
    args = [binary, str(source), "-o", str(output), "--margin", f"{req.margin_seconds:g}sec",
            "--edit", f"audio:threshold={req.threshold}%"]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=1800, cwd=str(source.parent))
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(504, "Auto-Editor işlemi 30 dakika sonunda zaman aşımına uğradı.") from exc
    if result.returncode != 0 or not output.is_file() or output.stat().st_size == 0:
        detail = (result.stderr or result.stdout or "Auto-Editor çıktı üretmedi.")[-1800:]
        raise HTTPException(500, f"Auto-Editor işlemi başarısız: {detail}")
    return {"processed": True, "file": f"/workspace/{output.relative_to(WORK).as_posix()}",
            "filename": output.name, "size_mb": round(output.stat().st_size / 1048576, 2)}

OAUTH_PROVIDERS = {
    "youtube":{"client_id_env":"YAMAN_GOOGLE_CLIENT_ID","client_secret_env":"YAMAN_GOOGLE_CLIENT_SECRET"},
    "tiktok":{"client_id_env":"YAMAN_TIKTOK_CLIENT_KEY","client_secret_env":"YAMAN_TIKTOK_CLIENT_SECRET"},
    "instagram":{"client_id_env":"YAMAN_META_APP_ID","client_secret_env":"YAMAN_META_APP_SECRET"},
}
OAUTH_KEY_FILE = BASE / ".oauth.key"
OAUTH_TOKEN_FILE = WORK / "oauth_tokens.enc"
OAUTH_APP_FILE = WORK / "oauth_apps.enc"

def oauth_fernet():
    key=os.getenv("YAMAN_TOKEN_ENCRYPTION_KEY")
    if not key:
        if not OAUTH_KEY_FILE.exists():
            OAUTH_KEY_FILE.write_bytes(Fernet.generate_key())
        key=OAUTH_KEY_FILE.read_text(encoding="ascii").strip()
    return Fernet(key.encode("ascii"))

def oauth_token_data():
    if not OAUTH_TOKEN_FILE.exists():return {}
    try:return json.loads(oauth_fernet().decrypt(OAUTH_TOKEN_FILE.read_bytes()).decode("utf-8"))
    except Exception as exc:raise RuntimeError("OAuth token vault cannot be decrypted") from exc

def save_oauth_tokens(data):
    encrypted=oauth_fernet().encrypt(json.dumps(data,ensure_ascii=False).encode("utf-8"))
    temp=OAUTH_TOKEN_FILE.with_suffix(".tmp");temp.write_bytes(encrypted);temp.replace(OAUTH_TOKEN_FILE)

def oauth_app_config():
    if not OAUTH_APP_FILE.exists():return {}
    try:return json.loads(oauth_fernet().decrypt(OAUTH_APP_FILE.read_bytes()).decode("utf-8"))
    except Exception as exc:raise RuntimeError("OAuth app credential vault cannot be decrypted") from exc

def oauth_client(platform_name):
    cfg=OAUTH_PROVIDERS[platform_name];saved=oauth_app_config().get(platform_name,{})
    client_id=os.getenv(cfg["client_id_env"]) or saved.get("client_id")
    secret=os.getenv(cfg["client_secret_env"]) or saved.get("client_secret")
    if not client_id or not secret:raise HTTPException(503,f"{platform_name} developer app credentials are not configured")
    return client_id,secret

@app.get("/api/oauth/config/status")
def oauth_config_status():
    saved=oauth_app_config()
    return {p:{"configured":bool((os.getenv(cfg["client_id_env"]) and os.getenv(cfg["client_secret_env"])) or
        (saved.get(p,{}).get("client_id") and saved.get(p,{}).get("client_secret"))),
        "client_id":os.getenv(cfg["client_id_env"]) or saved.get(p,{}).get("client_id","")}
        for p,cfg in OAUTH_PROVIDERS.items()}

@app.post("/api/oauth/config")
def save_oauth_app(req: OAuthAppRequest):
    if req.platform not in OAUTH_PROVIDERS:raise HTTPException(400,"Unsupported OAuth provider")
    saved=oauth_app_config()
    saved[req.platform]={"client_id":req.client_id.strip(),"client_secret":req.client_secret.strip(),"updated_at":time.time()}
    encrypted=oauth_fernet().encrypt(json.dumps(saved).encode("utf-8"))
    temp=OAUTH_APP_FILE.with_suffix(".tmp");temp.write_bytes(encrypted);temp.replace(OAUTH_APP_FILE)
    return {"saved":True,"platform":req.platform}

VISUAL_PROVIDER_FILE = WORK / "visual_providers.enc"

def visual_provider_config():
    if not VISUAL_PROVIDER_FILE.exists(): return {}
    try: return json.loads(oauth_fernet().decrypt(VISUAL_PROVIDER_FILE.read_bytes()).decode("utf-8"))
    except Exception as exc: raise RuntimeError("AI visual provider vault cannot be decrypted") from exc

@app.get("/api/visual-providers")
def get_visual_provider_status():
    saved=visual_provider_config()
    return {"runway_configured":bool(os.getenv("RUNWAY_API_KEY") or saved.get("runway_api_key")),
            "pexels_configured":bool(os.getenv("PEXELS_API_KEY") or saved.get("pexels_api_key")),
            "runway_key_source":"environment" if os.getenv("RUNWAY_API_KEY") else ("encrypted vault" if saved.get("runway_api_key") else "not configured"),
            "pexels_key_source":"environment" if os.getenv("PEXELS_API_KEY") else ("encrypted vault" if saved.get("pexels_api_key") else "not configured"),
            "comfyui_url":os.getenv("COMFYUI_URL","http://127.0.0.1:8188"),
            "gpu_note":"Bu bilgisayardaki GTX 1650 4 GB VRAM, modern video diffusion modelleri için sınırlıdır. Gerçek AI video üretimi için Runway bulut motoru önerilir."}

class VisualProviderRequest(BaseModel):
    runway_api_key: str = Field(default="", max_length=500)
    pexels_api_key: str = Field(default="", max_length=500)

@app.post("/api/visual-providers")
def save_visual_provider_config(req: VisualProviderRequest):
    saved=visual_provider_config()
    for key in ("runway_api_key","pexels_api_key"):
        value=getattr(req,key).strip()
        if value: saved[key]=value
    encrypted=oauth_fernet().encrypt(json.dumps(saved).encode("utf-8"))
    temp=VISUAL_PROVIDER_FILE.with_suffix(".tmp");temp.write_bytes(encrypted);temp.replace(VISUAL_PROVIDER_FILE)
    return {"saved":True,"runway_configured":bool(saved.get("runway_api_key") or os.getenv("RUNWAY_API_KEY")),
            "pexels_configured":bool(saved.get("pexels_api_key") or os.getenv("PEXELS_API_KEY"))}

def _visual_provider_keys():
    saved=visual_provider_config()
    return (os.getenv("RUNWAY_API_KEY") or saved.get("runway_api_key",""),
            os.getenv("PEXELS_API_KEY") or saved.get("pexels_api_key",""))

def oauth_redirect_uri(request,platform_name):
    base=os.getenv("YAMAN_PUBLIC_BASE_URL",str(request.base_url).rstrip("/")).rstrip("/")
    return base+f"/api/oauth/callback/{platform_name}"

@app.get("/api/oauth/status")
def oauth_status():
    tokens=oauth_token_data()
    return {p:{"connected":bool(tokens.get(p,{}).get("access_token")),"expires_at":tokens.get(p,{}).get("expires_at"),
        "account":tokens.get(p,{}).get("account_name",""),"scopes":tokens.get(p,{}).get("scope","")}
        for p in OAUTH_PROVIDERS}

@app.get("/api/oauth/start/{platform_name}")
def oauth_start(platform_name: str,request: Request):
    if platform_name not in OAUTH_PROVIDERS:raise HTTPException(404,"Unsupported OAuth provider")
    client_id,_=oauth_client(platform_name);redirect_uri=oauth_redirect_uri(request,platform_name)
    state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(64)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    with sqlite3.connect(TASK_DB) as db:
        db.execute("CREATE TABLE IF NOT EXISTS oauth_states (state TEXT PRIMARY KEY,platform TEXT NOT NULL,verifier TEXT NOT NULL,redirect_uri TEXT NOT NULL,created_at REAL NOT NULL)")
        db.execute("INSERT INTO oauth_states VALUES(?,?,?,?,?)",(state,platform_name,verifier,redirect_uri,time.time()))
        db.execute("DELETE FROM oauth_states WHERE created_at < ?",(time.time()-600,));db.commit()
    if platform_name=="youtube":
        params={"client_id":client_id,"redirect_uri":redirect_uri,"response_type":"code","scope":"https://www.googleapis.com/auth/youtube.upload","access_type":"offline","prompt":"consent","state":state}
        url="https://accounts.google.com/o/oauth2/v2/auth?"+urlencode(params)
    elif platform_name=="tiktok":
        params={"client_key":client_id,"redirect_uri":redirect_uri,"response_type":"code","scope":"user.info.basic,video.publish","state":state,"code_challenge":challenge,"code_challenge_method":"S256"}
        url="https://www.tiktok.com/v2/auth/authorize/?"+urlencode(params)
    else:
        params={"client_id":client_id,"redirect_uri":redirect_uri,"response_type":"code","scope":"instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement","state":state}
        url="https://www.facebook.com/v21.0/dialog/oauth?"+urlencode(params)
    return {"authorization_url":url,"redirect_uri":redirect_uri,"state":state}

@app.get("/api/oauth/callback/{platform_name}")
def oauth_callback(platform_name: str,request: Request,code: str="",state: str="",error: str=""):
    if platform_name not in OAUTH_PROVIDERS:raise HTTPException(404,"Unsupported OAuth provider")
    if error:return HTMLResponse(f"<h2>Authorization cancelled</h2><p>{html.escape(error)}</p>")
    with sqlite3.connect(TASK_DB) as db:
        row=db.execute("SELECT verifier,redirect_uri,created_at FROM oauth_states WHERE state=? AND platform=?",(state,platform_name)).fetchone()
        if row:db.execute("DELETE FROM oauth_states WHERE state=?",(state,));db.commit()
    if not row or time.time()-row[2]>600:raise HTTPException(400,"OAuth state invalid or expired")
    verifier,redirect_uri,_=row;client_id,secret=oauth_client(platform_name)
    if platform_name=="youtube":
        token_url="https://oauth2.googleapis.com/token"
        data={"code":code,"client_id":client_id,"client_secret":secret,"redirect_uri":redirect_uri,"grant_type":"authorization_code"}
    elif platform_name=="tiktok":
        token_url="https://open.tiktokapis.com/v2/oauth/token/"
        data={"client_key":client_id,"client_secret":secret,"code":code,"grant_type":"authorization_code","redirect_uri":redirect_uri,"code_verifier":verifier}
    else:
        token_url="https://graph.facebook.com/v21.0/oauth/access_token"
        data={"client_id":client_id,"client_secret":secret,"redirect_uri":redirect_uri,"code":code}
    response=requests.post(token_url,data=data,timeout=25);raw=response.json()
    payload=raw.get("data",raw) if platform_name=="tiktok" else raw
    provider_error=raw.get("error");provider_code=provider_error.get("code") if isinstance(provider_error,dict) else provider_error
    if not response.ok or (provider_code and provider_code!="ok"):
        raise HTTPException(502,"OAuth token exchange failed: "+str(raw.get("error_description") or provider_error or raw)[:400])
    token=payload.get("access_token")
    if not token:raise HTTPException(502,"OAuth provider returned no access token")
    account_name="";instagram_user_id=None
    if platform_name=="instagram":
        long_lived=requests.get("https://graph.facebook.com/v21.0/oauth/access_token",params={
            "grant_type":"fb_exchange_token","client_id":client_id,"client_secret":secret,"fb_exchange_token":token},timeout=20)
        if long_lived.ok and long_lived.json().get("access_token"):
            payload=long_lived.json();token=payload["access_token"]
        pages=requests.get("https://graph.facebook.com/v21.0/me/accounts",params={
            "fields":"id,name,access_token,instagram_business_account","access_token":token},timeout=20)
        if pages.ok:
            for page in pages.json().get("data",[]):
                ig=page.get("instagram_business_account") or {}
                if ig.get("id") and page.get("access_token"):
                    token=page["access_token"];instagram_user_id=ig["id"];account_name=page.get("name","");break
    tokens=oauth_token_data()
    tokens[platform_name]={"access_token":token,"refresh_token":payload.get("refresh_token"),
        "expires_at":time.time()+int(payload.get("expires_in",0)) if payload.get("expires_in") else None,
        "refresh_expires_at":time.time()+int(payload.get("refresh_expires_in",0)) if payload.get("refresh_expires_in") else None,
        "scope":payload.get("scope",""),"open_id":payload.get("open_id"),"instagram_user_id":instagram_user_id,
        "account_name":account_name,"saved_at":time.time()}
    save_oauth_tokens(tokens)
    return HTMLResponse("<!doctype html><meta charset='utf-8'><title>YAMAN OAuth</title><h2>Hesap ba\u011flant\u0131s\u0131 tamamland\u0131</h2><p>Bu pencereyi kapat\u0131p Platform Profilleri sayfas\u0131n\u0131 yenileyebilirsiniz.</p><script>setTimeout(()=>window.close(),1800)</script>")

@app.delete("/api/oauth/{platform_name}")
def oauth_disconnect(platform_name: str):
    if platform_name not in OAUTH_PROVIDERS:raise HTTPException(404,"Unsupported OAuth provider")
    tokens=oauth_token_data();tokens.pop(platform_name,None);save_oauth_tokens(tokens)
    return {"disconnected":True,"platform":platform_name}

def oauth_access_token(platform_name):
    tokens=oauth_token_data();item=tokens.get(platform_name)
    if not item or not item.get("access_token"):raise HTTPException(409,"Connect the platform account first")
    if item.get("expires_at") and item["expires_at"]<time.time()+60:
        refresh=item.get("refresh_token")
        if not refresh or platform_name=="instagram":raise HTTPException(409,"OAuth token expired; reconnect the account")
        client_id,secret=oauth_client(platform_name)
        if platform_name=="youtube":
            response=requests.post("https://oauth2.googleapis.com/token",data={"client_id":client_id,"client_secret":secret,"refresh_token":refresh,"grant_type":"refresh_token"},timeout=25)
        else:
            response=requests.post("https://open.tiktokapis.com/v2/oauth/token/",data={"client_key":client_id,"client_secret":secret,"grant_type":"refresh_token","refresh_token":refresh},timeout=25)
        raw=response.json();payload=raw.get("data",raw) if platform_name=="tiktok" else raw
        if not response.ok or not payload.get("access_token"):raise HTTPException(409,"OAuth token refresh failed; reconnect the account")
        item["access_token"]=payload["access_token"];item["expires_at"]=time.time()+int(payload.get("expires_in",0))
        item["refresh_token"]=payload.get("refresh_token",refresh);tokens[platform_name]=item;save_oauth_tokens(tokens)
    return item["access_token"]

@app.get("/api/publish/tiktok/creator")
def tiktok_creator_info():
    token=oauth_access_token("tiktok")
    response=requests.post("https://open.tiktokapis.com/v2/post/publish/creator_info/query/",
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},json={},timeout=25)
    payload=response.json()
    if not response.ok or payload.get("error",{}).get("code") not in (None,"ok"):
        raise HTTPException(502,"TikTok creator information unavailable: "+str(payload.get("error"))[:400])
    return payload.get("data",{})

@app.post("/api/publish/{platform_name}")
def publish_video(platform_name: str,req: PublishRequest):
    if platform_name not in OAUTH_PROVIDERS:raise HTTPException(404,"Unsupported publishing provider")
    if not req.confirm_publish:raise HTTPException(400,"Explicit user confirmation is required before publishing")
    job=jobs.get(req.job_id)
    if not job:raise HTTPException(404,"Project not found")
    clip=next((c for c in job["clips"] if c["id"]==req.clip_id),None)
    if not clip:raise HTTPException(404,"Clip not found")
    video=Path(job["folder"])/f"clip_{req.clip_id}_{platform_name}.mp4"
    if not video.is_file():raise HTTPException(404,"Render this platform's MP4 before publishing")
    token=oauth_access_token(platform_name)
    if platform_name=="youtube":
        init=requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
            headers={"Authorization":"Bearer "+token,"Content-Type":"application/json; charset=UTF-8","X-Upload-Content-Type":"video/mp4","X-Upload-Content-Length":str(video.stat().st_size)},
            json={"snippet":{"title":req.title,"description":req.description,"categoryId":"22"},"status":{"privacyStatus":req.privacy if req.privacy in ("private","unlisted","public") else "private","selfDeclaredMadeForKids":False}},timeout=30)
        if not init.ok:raise HTTPException(502,"YouTube upload initialization failed: "+init.text[:500])
        upload_url=init.headers.get("Location")
        if not upload_url:raise HTTPException(502,"YouTube did not return a resumable upload URL")
        with video.open("rb") as f:uploaded=requests.put(upload_url,data=f,headers={"Content-Type":"video/mp4","Content-Length":str(video.stat().st_size)},timeout=900)
        if not uploaded.ok:raise HTTPException(502,"YouTube upload failed: "+uploaded.text[:500])
        return {"published":True,"platform":"youtube","result":uploaded.json()}
    if platform_name=="tiktok":
        creator=requests.post("https://open.tiktokapis.com/v2/post/publish/creator_info/query/",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},json={},timeout=25).json()
        creator_data=creator.get("data",{})
        options=creator_data.get("privacy_level_options",[])
        privacy=req.privacy
        if privacy not in options:
            raise HTTPException(400,"Choose one of the creator's available TikTok privacy levels: "+", ".join(options))
        max_duration=creator_data.get("max_video_post_duration_sec")
        if max_duration:
            probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(video)],
                capture_output=True,text=True,timeout=20)
            try:duration=float(probe.stdout.strip())
            except Exception:duration=0
            if duration and duration>float(max_duration):
                raise HTTPException(400,f"This TikTok account allows up to {max_duration} seconds; the selected video is {duration:.1f} seconds.")
        size=video.stat().st_size;chunk=min(10*1024*1024,size)
        count=max(1,size//chunk)
        init=requests.post("https://open.tiktokapis.com/v2/post/publish/video/init/",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},
            json={"post_info":{"title":req.title[:2200],"privacy_level":privacy, "disable_duet":bool(creator_data.get("duet_disabled",False)),
                "disable_comment":bool(creator_data.get("comment_disabled",False)),
                "disable_stitch":bool(creator_data.get("stitch_disabled",False)),
                "brand_content_toggle":False,"brand_organic_toggle":False,"is_aigc":req.is_aigc},
                  "source_info":{"source":"FILE_UPLOAD","video_size":size,"chunk_size":chunk,"total_chunk_count":count}},timeout=30)
        payload=init.json()
        if not init.ok or payload.get("error",{}).get("code") not in (None,"ok"):raise HTTPException(502,"TikTok publish initialization failed: "+str(payload.get("error"))[:500])
        upload_url=payload.get("data",{}).get("upload_url")
        if not upload_url:raise HTTPException(502,"TikTok did not return an upload URL")
        with video.open("rb") as f:
            offset=0
            for chunk_index in range(count):
                remaining=size-offset
                read_size=chunk if chunk_index<count-1 else remaining
                data=f.read(read_size)
                if not data:raise HTTPException(502,"TikTok upload ended before all bytes were read")
                end=offset+len(data)-1
                put=requests.put(upload_url,data=data,headers={"Content-Type":"video/mp4","Content-Length":str(len(data)),"Content-Range":f"bytes {offset}-{end}/{size}"},timeout=180)
                if put.status_code not in (200,201,206):raise HTTPException(502,"TikTok media transfer failed: "+put.text[:400])
                offset=end+1
        publish_id=payload.get("data",{}).get("publish_id")
        if not publish_id:raise HTTPException(502,"TikTok returned no publish_id")
        latest={}
        for _ in range(15):
            check=requests.post("https://open.tiktokapis.com/v2/post/publish/status/fetch/",
                headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},
                json={"publish_id":publish_id},timeout=20)
            latest=check.json()
            if not check.ok or latest.get("error",{}).get("code") not in (None,"ok"):
                raise HTTPException(502,"TikTok status check failed: "+str(latest.get("error"))[:400])
            status=latest.get("data",{}).get("status")
            if status=="PUBLISH_COMPLETE":
                return {"published":True,"platform":"tiktok","publish_id":publish_id,"status":status}
            if status=="FAILED":
                raise HTTPException(502,"TikTok rejected the post: "+str(latest.get("data",{}).get("fail_reason","Unknown error"))[:400])
            time.sleep(4)
        return {"published":False,"platform":"tiktok","publish_id":publish_id,"status":latest.get("data",{}).get("status","PROCESSING"),
                "note":"TikTok accepted the upload; publishing is still processing. Check the publish status shortly."}
    if not req.media_url or not req.media_url.startswith("https://"):
        raise HTTPException(400,"Instagram Reels needs a publicly reachable HTTPS media_url; localhost files cannot be fetched by Meta.")
    ig_user=os.getenv("YAMAN_INSTAGRAM_USER_ID") or oauth_token_data().get("instagram",{}).get("instagram_user_id")
    if not ig_user:raise HTTPException(503,"Link an Instagram professional account to a Facebook Page with Instagram publishing permissions.")
    graph="https://graph.facebook.com/v21.0"
    container=requests.post(f"{graph}/{ig_user}/media",data={"media_type":"REELS","video_url":req.media_url,"caption":req.title+"\n\n"+req.description,"access_token":token},timeout=30).json()
    if not container.get("id"):raise HTTPException(502,"Instagram container creation failed: "+str(container)[:500])
    media_id=container["id"]
    for _ in range(24):
        status=requests.get(f"{graph}/{media_id}",params={"fields":"status_code","access_token":token},timeout=15).json()
        if status.get("status_code")=="FINISHED":break
        if status.get("status_code")=="ERROR":raise HTTPException(502,"Instagram video processing failed")
        time.sleep(5)
    else:raise HTTPException(504,"Instagram video processing timed out")
    published=requests.post(f"{graph}/{ig_user}/media_publish",data={"creation_id":media_id,"access_token":token},timeout=30).json()
    if not published.get("id"):raise HTTPException(502,"Instagram publish failed: "+str(published)[:500])
    return {"published":True,"platform":"instagram","media_id":published["id"]}

@app.get("/api/platforms")
def platforms():
    return {
        key: {**value, "aspect_ratio": ("9:16" if value["height"] > value["width"] else ("16:9" if value["width"] > value["height"] else "1:1")),
              "resolution": value["width"], "connected": False,
              "connection_mode": "Export profile ready; OAuth not configured"}
        for key, value in PLATFORM_PROFILES.items()
    }

@app.post("/api/platforms/profile")
def update_platform_profile(req: PlatformProfileRequest):
    if req.platform not in PLATFORM_PROFILES:
        raise HTTPException(400, "Unknown platform profile")
    ratios = {"9:16": (9, 16), "1:1": (1, 1), "16:9": (16, 9)}
    rw, rh = ratios[req.aspect_ratio]
    width = req.resolution
    height = int(round(width * rh / rw))
    if height % 2: height += 1
    profile = PLATFORM_PROFILES[req.platform]
    profile.update({"width": width, "height": height, "max_seconds": req.max_seconds})
    _PROFILE_FILE.write_text(json.dumps(PLATFORM_PROFILES, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"saved": True, "platform": req.platform, **profile,
            "aspect_ratio": req.aspect_ratio, "resolution": width}

@app.get("/api/projects")
def projects():
    items = []
    for job_id, job in jobs.items():
        items.append({
            "job_id": job_id,
            "duration": round(job.get("duration", 0), 1),
            "language": job.get("language", "unknown"),
            "clip_count": len(job.get("clips", [])),
            "created_at": Path(job.get("folder", WORK)).stat().st_mtime if Path(job.get("folder", WORK)).exists() else 0
        })
    return {"projects": sorted(items, key=lambda x: x["created_at"], reverse=True)}

@app.get("/api/media/library")
def media_library():
    """List rendered MP4 assets from disk, including outputs from previous app sessions."""
    items = []
    for folder in WORK.iterdir():
        if not folder.is_dir():
            continue
        for path in folder.glob("clip_*_*.mp4"):
            match = re.fullmatch(r"clip_(\d+)_(youtube|instagram|tiktok)\.mp4", path.name, re.IGNORECASE)
            if not match or not path.is_file():
                continue
            clip_id, platform = int(match.group(1)), match.group(2).lower()
            try:
                stat = path.stat()
                items.append({
                    "job_id": folder.name,
                    "clip_id": clip_id,
                    "platform": platform,
                    "label": PLATFORMS[platform]["label"],
                    "filename": path.name,
                    "file": f"/workspace/{folder.name}/{path.name}",
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "modified_at": stat.st_mtime,
                })
            except OSError:
                continue
    for folder in WORK.iterdir():
        if folder.is_dir():
            for filename, clip_id, platform, label in (
                ("summary_video.mp4", "summary", "summary", "Akıllı Video Özeti"),
                ("story_video.mp4", "story", "story", "Hikâye Akışı"),
                ("documentary_video.mp4", "documentary", "documentary", "Belgesel Anlatımı"),
                ("education_video.mp4", "education", "education", "Eğitim Videosu"),
                ("product_video.mp4", "product", "product", "Ürün Tanıtımı"),
            ):
                path = folder / filename
                if path.is_file():
                    try:
                        stat = path.stat()
                        items.append({"job_id": folder.name, "clip_id": clip_id, "platform": platform,
                                      "label": label, "filename": path.name,
                                      "file": f"/workspace/{folder.name}/{path.name}",
                                      "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                      "modified_at": stat.st_mtime})
                    except OSError:
                        pass
    cinematic_root = WORK / "cinematic-content"
    if cinematic_root.is_dir():
        for folder in cinematic_root.iterdir():
            if not folder.is_dir(): continue
            for path in list(folder.glob("cinematic_*.mp4")):
                try:
                    stat=path.stat()
                    items.append({"job_id":folder.name,"clip_id":"cinematic","platform":"youtube",
                                  "label":"AI Fragman / Sinematik Shorts","filename":path.name,
                                  "file":f"/workspace/cinematic-content/{folder.name}/{path.name}",
                                  "size_mb":round(stat.st_size/(1024*1024),2),"modified_at":stat.st_mtime})
                except OSError: pass
    generated_root = WORK / "autopilot-content"
    if generated_root.is_dir():
        for folder in generated_root.iterdir():
            path = folder / "publish_ready_shorts.mp4"
            if folder.is_dir() and path.is_file():
                try:
                    stat = path.stat()
                    items.append({"job_id": folder.name, "clip_id": "generated", "platform": "youtube",
                                  "label": "AI Üretimi Shorts", "filename": path.name,
                                  "file": f"/workspace/autopilot-content/{folder.name}/{path.name}",
                                  "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                  "modified_at": stat.st_mtime})
                except OSError:
                    pass
    items.sort(key=lambda item: item["modified_at"], reverse=True)
    return {"items": items, "count": len(items)}


@app.get("/api/settings")
def get_settings():
    return {"ollama_url": OLLAMA_URL, "ollama_model": OLLAMA_MODEL,
            "whisper_model": WHISPER_MODEL, "whisper_device": WHISPER_DEVICE,
            "available_whisper_models": ["tiny", "base", "small", "medium", "large-v3"],
            "local_only": False, "local_first": True, "optional_cloud_providers": ["Runway", "Pexels", "Edge TTS"]}

@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    global OLLAMA_MODEL, WHISPER_MODEL, WHISPER_DEVICE, _whisper
    if not re.fullmatch(r"[A-Za-z0-9._:-]+", req.ollama_model):
        raise HTTPException(400, "Geçersiz Ollama model adı.")
    OLLAMA_MODEL = req.ollama_model
    WHISPER_MODEL = req.whisper_model
    WHISPER_DEVICE = req.whisper_device
    _whisper = None
    config_path = BASE / "settings.local.json"
    config_path.write_text(json.dumps(req.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return {"saved": True, "settings": req.model_dump()}

def set_task(task_id: str, percent: int, stage: str, status: str = "running", **extra):
    """Serialize in-process task snapshots and their SQLite journal writes."""
    with _task_state_lock:
        state = task_states.setdefault(task_id, {})
        now = datetime.now(timezone.utc).isoformat()
        created = state.get("created_at", now)
        state.update({"task_id": task_id, "percent": max(0, min(100, int(percent))),
                      "stage": stage, "status": status, "created_at": created,
                      "updated_at": now, **extra})
        payload = json.dumps(state, ensure_ascii=False, default=str)
        with sqlite3.connect(TASK_DB, timeout=15) as db:
            db.execute("""INSERT INTO tasks(task_id,created_at,updated_at,status,percent,stage,payload_json)
                VALUES(?,?,?,?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET updated_at=excluded.updated_at,
                status=excluded.status,percent=excluded.percent,stage=excluded.stage,payload_json=excluded.payload_json""",
                (task_id, created, now, status, state["percent"], stage, payload))
            event_type = status if status in ("completed", "failed", "cancelled", "interrupted") else "progress"
            db.execute("INSERT INTO task_events(task_id,event_type,created_at,payload_json) VALUES(?,?,?,?)",
                (task_id, event_type, now, payload))
            db.commit()
        return dict(state)

def task_is_cancelled(task_id: str) -> bool:
    if task_id in _cancelled_tasks:
        return True
    with sqlite3.connect(TASK_DB) as db:
        row=db.execute("SELECT status FROM tasks WHERE task_id=?",(task_id,)).fetchone()
    return bool(row and row[0]=="cancelled")


def run_analyze_task(task_id: str, req: AnalyzeRequest, folder: Path, source_video: Path | None = None):
    try:
        set_task(task_id, 3, "Araçlar kontrol ediliyor")
        require_binary("ffmpeg"); require_binary("ffprobe")
        if source_video is None:
            if not req.url:
                raise RuntimeError("YouTube bağlantısı veya yerel video seçilmelidir.")
            video = download_video(str(req.url), folder,
                lambda value, label: set_task(task_id, value, label))
        else:
            video = source_video
            set_task(task_id, 22, "İndirilen video içe aktarıldı")
        set_task(task_id, 24, "Video bilgileri okunuyor")
        duration = probe_duration(video)
        set_task(task_id, 30, "Whisper modeli hazırlanıyor")
        set_task(task_id, 36, "Konuşma çözümleniyor · Whisper")
        segments, language = transcribe(video, req.language,
            lambda value, label: set_task(task_id, value, label), duration)
        set_task(task_id, 70, "Konuşma analizi tamamlandı · Shorts adayları seçiliyor")
        candidates = make_candidates(segments, duration, req.clips, req.min_seconds, req.max_seconds)
        set_task(task_id, 82, "AI editör adayları değerlendiriyor")
        candidates = rank_candidates(candidates)
        for c in candidates:
            c["learning_adjustment"] = learning.adjustment("youtube")
            c["score"] = max(1, min(100, c["score"] + c["learning_adjustment"]))
        candidates = sorted(candidates, key=lambda x:x["score"], reverse=True)[:req.clips]
        if not candidates:
            recognized = sum(len(str(x.get("text", "")).split()) for x in segments)
            if recognized < 2:
                raise RuntimeError("Whisper bu videoda yeterli konu\u015fma alg\u0131layamad\u0131. Ses d\u00fczeyini, konu\u015fma dilini veya video kayna\u011f\u0131n\u0131 kontrol edin.")
            raise RuntimeError("Konu\u015fma bulundu ancak kesit olu\u015fturulamad\u0131. Daha k\u0131sa klip s\u00fcresi se\u00e7erek yeniden deneyin.")
        jobs[task_id] = {"folder": str(folder), "video": str(video), "duration": duration,
                         "language": language, "segments": segments, "clips": candidates}
        save_job(task_id, jobs[task_id])
        result = {"job_id": task_id, "duration": duration, "language": language, "clips": candidates,
                  "transcript": segments,
                  "ai_mode": "local Ollama (fallback: heuristic)", "platforms": list(PLATFORMS)}
        set_task(task_id, 100, "Analiz tamamlandı · Shorts listesi hazır", "completed", result=result)
    except Exception as exc:
        shutil.rmtree(folder, ignore_errors=True)
        set_task(task_id, 100, "İşlem başarısız", "failed", error=str(exc))



def segment_importance_score(segment: dict) -> float:
    """Deterministic transcript-only salience score used when local LLM output is unavailable."""
    text = str(segment.get("text", "")).strip().lower()
    words = [word.strip(".,!?;:()[]{}\\\"'") for word in text.split()]
    if not words:
        return 0.0
    cues = (
        "??nk?", "sonu?", "?nemli", "ancak", "ilk kez", "en b?y?k", "ke?if", "kan?t",
        "sebep", "??z?m", "sorun", "ba?ar?", "hata", "kritik", "ama?", "veri",
        "y?zde", "milyon", "neden", "nas?l", "dikkat", "ger?ek", "sonunda",
        "asl?nda", "?zellikle", "fakat", "b?ylece", "dolay?s?yla", "risk", "fark",
    )
    cue_hits = sum(1 for cue in cues if cue in text)
    unique_ratio = len(set(words)) / max(1, len(words))
    numeric_hits = sum(1 for word in words if any(char.isdigit() for char in word))
    punctuation = sum(text.count(mark) for mark in ("?", "!", ":"))
    length_score = min(len(words), 32) / 32
    return length_score * 3.0 + unique_ratio * 1.2 + cue_hits * 1.35 + numeric_hits * 0.35 + min(punctuation, 3) * 0.2


def fallback_summary_moments(segments: list[dict], duration: float, target_seconds: int) -> list[dict]:
    """Choose a spread of spoken moments when the local model cannot return valid JSON."""
    usable = [x for x in segments if str(x.get("text", "")).strip()]
    if not usable or duration <= 0:
        raise RuntimeError("\u00d6zet video i\u00e7in konu\u015fma i\u00e7eren transkript bulunamad\u0131.")
    count = min(7, max(2, round(target_seconds / 16)))
    per_moment = max(7.0, min(22.0, target_seconds / count))
    chosen = []
    for i in range(count):
        target = (i + 0.5) / count * duration
        left, right = i / count * duration, (i + 1) / count * duration
        candidates = [x for x in usable if left <= (float(x.get("start", 0)) + float(x.get("end", 0))) / 2 < right]
        pool = candidates or usable
        seg = max(pool, key=lambda x: (
            segment_importance_score(x),
            -abs((float(x.get("start", 0)) + float(x.get("end", 0))) / 2 - target),
        ))
        start = max(0.0, min(float(seg["start"]), duration - 1))
        end = min(duration, max(float(seg["end"]), start + per_moment))
        if end - start < 4:
            end = min(duration, start + min(per_moment, duration - start))
        if end - start >= 4 and all(abs(start - old["start"]) > 5 for old in chosen):
            chosen.append({"start": round(start, 2), "end": round(end, 2),
                           "reason": "\u00d6nemli konu\u015fma b\u00f6l\u00fcm\u00fc"})
    chosen.sort(key=lambda x: x["start"])
    remaining, output = float(target_seconds), []
    for item in chosen:
        if remaining < 4:
            break
        length = min(item["end"] - item["start"], remaining)
        if length >= 4:
            item["end"] = round(item["start"] + length, 2)
            output.append(item)
            remaining -= length
    if not output:
        first = usable[0]
        start = max(0.0, float(first["start"]))
        output = [{"start": start, "end": min(duration, start + min(15, target_seconds)),
                   "reason": "Transkript ba\u015flang\u0131c\u0131ndan se\u00e7ilen b\u00f6l\u00fcm"}]
    return output


def fallback_story_moments(segments: list[dict], duration: float, target_seconds: int) -> list[dict]:
    """Build five chronological story beats from transcript timestamps without inventing content."""
    usable = [x for x in segments if str(x.get("text", "")).strip()]
    if not usable or duration < 20:
        return fallback_summary_moments(segments, duration, target_seconds)
    labels = ["Konu", "Giriş", "Gelişme", "Sonuç", "Kapanış"]
    beat_window = duration / len(labels)
    target_length = min(12.0, max(4.0, target_seconds / len(labels)))
    output = []
    for index, label in enumerate(labels):
        left, right = index * beat_window, (index + 1) * beat_window
        in_window = [x for x in usable if left <= (float(x.get("start", 0)) + float(x.get("end", 0))) / 2 < right]
        pool = in_window or usable
        seg = max(pool, key=lambda x: (
            segment_importance_score(x),
            -abs((float(x.get("start", 0)) + float(x.get("end", 0))) / 2 - (left + right) / 2),
        ))
        start = max(left, min(float(seg.get("start", left)), right - 4.0))
        end = min(right, max(float(seg.get("end", start)), start + min(target_length, beat_window)))
        if end - start < 4:
            end = min(right, start + 4)
        if end - start >= 4:
            output.append({"start": round(start, 2), "end": round(end, 2), "section": label,
                           "reason": str(seg.get("text", label)).strip()[:200]})
    return output if len(output) >= 4 else fallback_summary_moments(segments, duration, target_seconds)


def fallback_documentary_moments(segments: list[dict], duration: float, target_seconds: int) -> list[dict]:
    """Build a seven-chapter documentary timeline from source transcript timestamps."""
    usable = [x for x in segments if str(x.get("text", "")).strip()]
    if not usable or duration < 28:
        return fallback_story_moments(segments, duration, target_seconds)
    labels = ["Konu", "Güçlü Açılış", "Arka Plan", "Kronolojik Gelişme", "Bulgular", "Sonuç", "Kapanış"]
    beat_window = duration / len(labels)
    target_length = min(12.0, max(4.0, target_seconds / len(labels)))
    output = []
    for index, label in enumerate(labels):
        left, right = index * beat_window, (index + 1) * beat_window
        in_window = [x for x in usable if left <= (float(x.get("start", 0)) + float(x.get("end", 0))) / 2 < right]
        pool = in_window or usable
        seg = max(pool, key=lambda x: (
            segment_importance_score(x),
            -abs((float(x.get("start", 0)) + float(x.get("end", 0))) / 2 - (left + right) / 2),
        ))
        start = max(left, min(float(seg.get("start", left)), right - 4.0))
        end = min(right, max(float(seg.get("end", start)), start + min(target_length, beat_window)))
        if end - start < 4:
            end = min(right, start + 4)
        if end - start >= 4:
            output.append({"start": round(start, 2), "end": round(end, 2), "section": label,
                           "reason": str(seg.get("text", label)).strip()[:200]})
    return output if len(output) == len(labels) else fallback_story_moments(segments, duration, target_seconds)


def fallback_structured_moments(segments: list[dict], duration: float, target_seconds: int, labels: list[str]) -> list[dict]:
    """Create chronological, transcript-grounded chapters for structured video formats."""
    usable = [x for x in segments if str(x.get("text", "")).strip()]
    if not usable:
        return fallback_summary_moments(segments, duration, target_seconds)
    count = len(labels)
    window = duration / count
    if window < 4:
        return fallback_story_moments(segments, duration, target_seconds)
    desired = min(22.0, max(4.0, target_seconds / count))
    output = []
    for index, label in enumerate(labels):
        left, right = index * window, (index + 1) * window
        candidates = [x for x in usable if left <= (float(x.get("start", 0)) + float(x.get("end", 0))) / 2 < right]
        pool = candidates or usable
        segment = max(pool, key=lambda x: (
            segment_importance_score(x),
            -abs((float(x.get("start", 0)) + float(x.get("end", 0))) / 2 - (left + right) / 2),
        ))
        start = max(left, min(float(segment.get("start", left)), right - 4))
        end = min(right, max(float(segment.get("end", start)), start + min(desired, window)))
        if end - start >= 4:
            output.append({"start": round(start, 2), "end": round(end, 2), "section": label,
                           "reason": str(segment.get("text", label)).strip()[:200]})
    return output if len(output) == count else fallback_story_moments(segments, duration, target_seconds)


def build_summary_moments(job: dict, target_seconds: int, format: str = "smart") -> dict:
    """Build either a highlight recap or a structured topic-to-conclusion story."""
    segments = job.get("segments", [])
    duration = float(job.get("duration", 0))
    transcript = "\n".join(
        f"{float(x.get('start', 0)):.1f}-{float(x.get('end', 0)):.1f}s: {str(x.get('text', '')).strip()}"
        for x in segments if str(x.get("text", "")).strip()
    )
    if len(transcript) > 8500:
        lines = transcript.splitlines()
        stride = max(1, len(lines) // 90)
        transcript = "\n".join(lines[::stride])[:8500]
    format_sections = {
        "story": ["Konu", "Giriş", "Gelişme", "Sonuç", "Kapanış"],
        "documentary": ["Konu", "Güçlü Açılış", "Arka Plan", "Kronolojik Gelişme", "Bulgular", "Sonuç", "Kapanış"],
        "education": ["Öğrenme Hedefi", "Konuya Giriş", "Temel Kavramlar", "Adım Adım Anlatım", "Uygulama Örneği", "Özet", "Mini Test ve Kapanış"],
        "product": ["İhtiyaç", "Ürün Tanıtımı", "Temel Özellikler", "Fayda ve Kullanım", "Fark Yaratan Detay", "Güven ve Kanıt", "Çağrı / CTA"],
    }
    is_story = format in format_sections
    is_documentary = format == "documentary"
    is_education = format == "education"
    is_product = format == "product"
    narrative_sections = format_sections.get(format, [])
    format_labels = {"smart": "Akıllı Özet", "story": "Hikâye Akışı", "documentary": "Belgesel Anlatımı", "education": "Eğitim Videosu", "product": "Ürün Tanıtımı"}
    if is_documentary:
        fallback = fallback_documentary_moments(segments, duration, target_seconds)
        instruction = (
            "Create a factual Turkish mini-documentary with exactly these ordered chapters: "
            "Konu, Güçlü Açılış, Arka Plan, Kronolojik Gelişme, Bulgular, Sonuç, Kapanış. "
            "Ground every chapter in the source, keep chronology, and never invent dates, quotes or causal links. "
            "Return story_beats with the exact Turkish section names and source timestamps."
        )
    elif is_education:
        fallback = fallback_structured_moments(segments, duration, target_seconds, narrative_sections)
        instruction = (
            f"Create a clear Turkish educational lesson for a general learner. Follow exactly these ordered chapters: {', '.join(narrative_sections)}. "
            "Explain concepts progressively, retain source examples, make the practical example concrete, and end with one short comprehension question. "
            "Do not invent facts or claim a demonstration exists unless visible or stated in the source. "
            "Return story_beats with section names matching the Turkish chapter labels, source timestamps and concise reasons."
        )
    elif is_product:
        fallback = fallback_structured_moments(segments, duration, target_seconds, narrative_sections)
        instruction = (
            f"Create a persuasive but honest Turkish product presentation. Follow exactly these ordered chapters: {', '.join(narrative_sections)}. "
            "Use only features, specifications, prices, guarantees and evidence explicitly present in the source. "
            "Never invent performance claims, customer reviews, certifications, prices or warranties. "
            "Connect each feature to a practical user benefit and end with a natural call to action. "
            "Return story_beats with section names matching the Turkish chapter labels, source timestamps and concise reasons."
        )
    elif is_story:
        fallback = fallback_story_moments(segments, duration, target_seconds)
        instruction = (
            f"Create a coherent Turkish mini-story with exactly these ordered beats: {', '.join(narrative_sections)}. Choose source timestamps, keep chronology, do not fabricate speech. "
            "Return story_beats with exact Turkish section names, timestamps and concise reasons."
        )
    else:
        fallback = fallback_summary_moments(segments, duration, target_seconds)
        instruction = (
            "Summarize the main idea and 3-5 key points. Choose up to 5 moments, each 6-22 seconds, "
            "in chronological order, preserving context. Return JSON only with title, summary, key_points, "
            "intro, outro and moments:[{start:1,end:12,reason:'...'}]."
        )
    data = {}
    try:
        prompt = (
            "You are an expert Turkish video editor and story producer. Answer in Turkish. "
            "Use only the timestamped transcript; do not invent facts or quotes. "
            + instruction + f" Keep total selected duration close to {target_seconds} seconds without exceeding it. "
            + "Transcript:\n" + transcript
        )
        data = llm_json(prompt, timeout=180, num_predict=1280 if is_story else 768)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}

    moments = []
    if is_story:
        raw = data.get("story_beats", []) if isinstance(data, dict) else []
        allowed = set(narrative_sections)
        for item in raw[:len(narrative_sections)] if isinstance(raw, list) else []:
            try:
                start = max(0.0, float(item.get("start", 0)))
                end = min(duration, float(item.get("end", 0)))
                section = str(item.get("section", "")).strip()
                if section not in allowed or end - start < 4:
                    continue
                if moments and start < moments[-1]["end"]:
                    start = float(moments[-1]["end"])
                if end - start < 4:
                    continue
                moments.append({"start": round(start, 2), "end": round(min(end, start + 22), 2),
                                "section": section, "reason": str(item.get("reason", section))[:200]})
            except (TypeError, ValueError, AttributeError):
                continue
        moments.sort(key=lambda x: x["start"])
        # A weak, incomplete or misordered model response must not produce a broken narrative.
        expected_order = {label: index for index, label in enumerate(narrative_sections)}
        actual_order = [expected_order[x["section"]] for x in moments]
        if len(moments) != len(narrative_sections) or actual_order != sorted(actual_order) or len(set(actual_order)) != len(narrative_sections):
            moments = fallback[:len(narrative_sections)]
    else:
        raw = data.get("moments", []) if isinstance(data, dict) else []
        for item in raw[:8] if isinstance(raw, list) else []:
            try:
                start = max(0.0, float(item.get("start", 0)))
                end = min(duration, float(item.get("end", 0)))
                if end - start < 4 or any(abs(start - old["start"]) < 4 for old in moments):
                    continue
                moments.append({"start": round(start, 2), "end": round(min(end, start + 22), 2),
                                "reason": str(item.get("reason", "Önemli içerik bölümü"))[:200]})
            except (TypeError, ValueError, AttributeError):
                continue
        moments.sort(key=lambda x: x["start"])
        selected, remaining = [], float(target_seconds)
        for item in moments:
            if remaining < 4:
                break
            length = min(item["end"] - item["start"], remaining)
            if length >= 4:
                item["end"] = round(item["start"] + length, 2)
                selected.append(item)
                remaining -= length
        moments = selected
        selected_duration = sum(x["end"] - x["start"] for x in moments)
        if selected_duration < target_seconds * 0.65:
            for extra in fallback:
                if selected_duration >= target_seconds:
                    break
                if any(abs(extra["start"] - item["start"]) < 10 for item in moments):
                    continue
                length = min(extra["end"] - extra["start"], target_seconds - selected_duration)
                if length >= 4:
                    moments.append({"start": extra["start"], "end": round(extra["start"] + length, 2),
                                    "reason": extra.get("reason", "Önemli içerik bölümü")})
                    selected_duration += length
            moments.sort(key=lambda x: x["start"])
        if not moments:
            moments = fallback

    # Cap the final timeline and preserve chronological order for both formats.
    selected, remaining = [], float(target_seconds)
    for item in moments:
        if remaining < 4:
            break
        length = min(float(item["end"]) - float(item["start"]), remaining)
        if length >= 4:
            selected.append({**item, "end": round(float(item["start"]) + length, 2)})
            remaining -= length
    moments = selected or fallback[:1]
    selected_duration = sum(x["end"] - x["start"] for x in moments)
    title = str(data.get("title") or format_labels.get(format, "Video"))[:100]
    summary = str(data.get("summary") or "Video içindeki önemli konuşma bölümleri seçilerek kısa bir akış oluşturuldu.")[:1500]
    key_points = data.get("key_points")
    if not isinstance(key_points, list) or not key_points:
        key_points = [str(x.get("reason", "Önemli bölüm")) for x in moments[:5]]
    story_beats = ([{"section": x.get("section", "Gelişme"), "start": x["start"], "end": x["end"],
                     "reason": x.get("reason", "")} for x in moments] if is_story else [])
    default_outros = {"education": "Review the mini-quiz to reinforce what you learned.", "product": "Explore the product details to learn more.", "documentary": "Follow for more source-grounded stories.", "story": "Follow for the next chapter."}
    return {"title": title, "summary": summary, "key_points": [str(x)[:220] for x in key_points[:6]],
            "intro": str(data.get("intro") or title)[:150],
            "outro": str(data.get("outro") or default_outros.get(format, "Thanks for watching."))[:150],
            "format": format, "format_label": format_labels.get(format, "Akıllı özet"),
            "story_beats": story_beats, "moments": moments,
            "method": "local Ollama" if data else "transcript fallback"}


def render_summary_video(job: dict, summary: dict, task_id: str) -> Path:
    """Render selected moments as one portrait MP4 with timed captions and intro/outro."""
    require_binary("ffmpeg")
    folder, source = Path(job["folder"]), Path(job["video"])
    if not source.is_file():
        raise RuntimeError("\u00d6zet video kaynak dosyas\u0131 bulunamad\u0131.")
    moments, parts, mapped = summary["moments"], [], []
    prefix = {"documentary": "documentary", "story": "story", "education": "education", "product": "product"}.get(summary.get("format"), "summary")
    timeline = 0.0
    for index, moment in enumerate(moments, 1):
        start, length = float(moment["start"]), float(moment["end"]) - float(moment["start"])
        if length < 3:
            continue
        part = folder / f"{prefix}_part_{index:02d}.mp4"
        video_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
        audio_filter = "aresample=44100,aformat=channel_layouts=stereo"
        if summary.get("transition", "fade") == "fade":
            fade_duration = min(0.28, max(0.12, length / 10))
            fade_out_start = max(0.0, length - fade_duration)
            video_filter += f",fade=t=in:st=0:d={fade_duration:.3f},fade=t=out:st={fade_out_start:.3f}:d={fade_duration:.3f}"
            audio_filter += f",afade=t=in:st=0:d={fade_duration:.3f},afade=t=out:st={fade_out_start:.3f}:d={fade_duration:.3f}"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start), "-i", str(source),
               "-t", str(length), "-map", "0:v:0", "-map", "0:a?",
               "-vf", video_filter, "-af", audio_filter,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2",
               "-avoid_negative_ts", "make_zero", "-movflags", "+faststart", str(part)]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode or not part.is_file() or part.stat().st_size == 0:
            raise RuntimeError("Ozet bolum render hatasi: " + (result.stderr or "FFmpeg failed")[-1200:])
        parts.append(part)
        for seg in job.get("segments", []):
            a, b = max(float(seg.get("start", 0)), start), min(float(seg.get("end", 0)), start + length)
            if b > a and str(seg.get("text", "")).strip():
                mapped.append({"start": timeline + a - start, "end": timeline + b - start,
                               "text": seg.get("text", ""), "words": []})
        timeline += length
        set_task(task_id, min(82, 42 + int(index / len(moments) * 35)),
                 f"Ozet video bolumu {index}/{len(moments)} hazir",
                 completed_moments=index, total_moments=len(moments))
    if not parts:
        raise RuntimeError("FFmpeg gecerli ozet bolumu uretemedi.")
    concat_file, joined = folder / f"{prefix}_concat.txt", folder / f"{prefix}_joined.mp4"
    concat_file.write_text("".join(f"file '{x.name}'\n" for x in parts), encoding="utf-8")
    command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
             "-safe", "0", "-i", str(concat_file), "-c", "copy", "-movflags", "+faststart", str(joined)])
    ass = folder / f"{prefix}_video.ass"
    create_ass(mapped if summary.get("captions", True) else [],
               {"start": 0.0, "end": timeline, "duration": timeline}, ass, 280)
    with ass.open("a", encoding="utf-8") as handle:
        if summary.get("chapter_titles", True) and summary.get("format") in ("story", "documentary", "education", "product"):
            cursor = 0.0
            for moment in moments:
                label = str(moment.get("section", "Gelişme"))
                handle.write(f"Dialogue: 0,{ass_time(cursor)},{ass_time(min(timeline,cursor+2.8))},Viral,,0,0,300,,{{\\an8\\fs62\\bord5}}{ass_escape(label.upper())}\n")
                cursor += float(moment["end"]) - float(moment["start"])
        if summary.get("chapter_titles", True) and summary.get("format") == "smart":
            handle.write(f"Dialogue: 1,0:00:00.00,{ass_time(min(4.0,timeline))},Viral,,0,0,300,,{{\\an8\\fs76\\bord5}}{ass_escape(summary['title'])}\n")
        if summary.get("chapter_titles", True) and timeline > 5:
            handle.write(f"Dialogue: 1,{ass_time(max(0,timeline-4))},{ass_time(timeline)},Viral,,0,0,300,,{{\\an8\\fs64\\bord5}}{ass_escape(summary['outro'])}\n")
    output = folder / {"documentary": "documentary_video.mp4", "story": "story_video.mp4", "education": "education_video.mp4", "product": "product_video.mp4"}.get(summary.get("format"), "summary_video.mp4")
    command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(joined),
             "-vf", f"ass='{escape_filter_path(ass)}'", "-map", "0:v:0", "-map", "0:a?",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output)])
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Ozet video dosyasi olusturulamadi.")
    for part in parts:
        part.unlink(missing_ok=True)
    concat_file.unlink(missing_ok=True)
    joined.unlink(missing_ok=True)
    return output


def run_summary_task(task_id: str, job_id: str, job: dict, target_seconds: int, format: str = "smart",
                     transition: str = "fade", captions: bool = True, chapter_titles: bool = True):
    try:
        set_task(task_id, 5, f"{ {'documentary': 'Belgesel anlatimi', 'education': 'Egitim videosu', 'product': 'Urun tanitimi', 'story': 'Hikaye akisi'}.get(format, 'Video ozeti')} hazirlaniyor - Yerel AI")
        summary = build_summary_moments(job, target_seconds, format)
        summary.update({"transition": transition, "captions": captions, "chapter_titles": chapter_titles})
        set_task(task_id, 38, f"{ {'documentary': 'Belgesel bolumleri', 'education': 'Egitim bolumleri', 'product': 'Urun tanitim bolumleri', 'story': 'Hikaye bolumleri'}.get(format, 'Onemli anlar')} siralandi - Video hazirlaniyor",
                 summary=summary, total_moments=len(summary["moments"]))
        output = render_summary_video(job, summary, task_id)
        summary["output"] = {"file": f"/workspace/{job_id}/{output.name}", "filename": output.name,
                             "size_mb": round(output.stat().st_size/(1024*1024),2),
                             "duration_seconds": round(sum(float(x["end"])-float(x["start"]) for x in summary["moments"]),1)}
        (Path(job["folder"])/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
        set_task(task_id,100,f"{ {'documentary': 'Belgesel anlatimi', 'education': 'Egitim videosu', 'product': 'Urun tanitimi', 'story': 'Hikaye akisi'}.get(format, 'Akilli ozet')} videosu hazir","completed",result=summary)
    except Exception as exc:
        set_task(task_id,100,"Ozet video olusturulamadi","failed",error=str(exc)[:1000])


def run_render_task(task_id: str, req: RenderRequest, job: dict, clip: dict, platforms: list[str]):
    try:
        outputs = []
        total = len(platforms)
        for index, platform in enumerate(platforms):
            label = PLATFORMS[platform]["label"]
            start_percent = 5 + int(index / total * 90)
            set_task(task_id, start_percent, f"{label} · Dikey kadraj ve altyazı hazırlanıyor")
            path = render_variant(job, clip, platform, req.captions, face_tracking=False)
            if not path.is_file() or path.stat().st_size <= 0:
                raise RuntimeError(f"{label} çıktısı oluşturulamadı veya boş dosya döndü.")
            outputs.append({"platform": platform, "label": label,
                            "file": f"/workspace/{req.job_id}/{path.name}",
                            "filename": path.name,
                            "size_mb": round(path.stat().st_size / (1024 * 1024), 2)})
            set_task(task_id, 5 + int((index + 1) / total * 90), f"{label} · Tamamlandı",
                     outputs=list(outputs))
        set_task(task_id, 100, "Tüm platform çıktıları hazır", "completed",
                 outputs=list(outputs),
                 result={"outputs": outputs, "message": "Dışa aktarma tamamlandı."})
    except Exception as exc:
        set_task(task_id, 100, "Render başarısız", "failed", error=f"Render hatası: {exc}")

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    task_id = uuid.uuid4().hex[:10]
    folder = WORK / task_id
    folder.mkdir(parents=True, exist_ok=True)
    set_task(task_id, 1, "Analiz kuyruğa alındı")
    background_tasks.add_task(run_analyze_task, task_id, req, folder)
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/local/videos")
def local_videos():
    """List supported videos from the current user's Downloads folder."""
    if not DOWNLOADS_DIR.is_dir():
        return {"items": [], "count": 0, "folder": str(DOWNLOADS_DIR)}
    items = []
    for path in DOWNLOADS_DIR.iterdir():
        try:
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
                stat = path.stat()
                items.append({"filename": path.name, "size_mb": round(stat.st_size / (1024 * 1024), 1),
                              "modified_at": stat.st_mtime})
        except OSError:
            continue
    items.sort(key=lambda item: item["modified_at"], reverse=True)
    return {"items": items[:100], "count": len(items), "folder": str(DOWNLOADS_DIR)}

@app.post("/api/analyze/local")
def analyze_local(req: LocalAnalyzeRequest, background_tasks: BackgroundTasks):
    if Path(req.filename).name != req.filename or req.filename in {".", ".."}:
        raise HTTPException(400, "Geçersiz dosya adı.")
    source = (DOWNLOADS_DIR / req.filename).resolve()
    if source.parent != DOWNLOADS_DIR.resolve() or not source.is_file():
        raise HTTPException(404, "Dosya İndirilenler klasöründe bulunamadı.")
    if source.suffix.lower() not in VIDEO_EXTENSIONS:
        raise HTTPException(415, "Desteklenmeyen video biçimi.")
    if source.stat().st_size > MAX_DOWNLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"Video {MAX_DOWNLOAD_MB} MB sınırını aşıyor.")
    task_id = uuid.uuid4().hex[:10]
    folder = WORK / task_id
    folder.mkdir(parents=True, exist_ok=True)
    local_copy = folder / ("source" + source.suffix.lower())
    try:
        shutil.copy2(source, local_copy)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    req_data = AnalyzeRequest(url=None, clips=req.clips, min_seconds=req.min_seconds,
                              max_seconds=req.max_seconds, language=req.language)
    set_task(task_id, 1, "İndirilen video analiz kuyruğuna alındı")
    background_tasks.add_task(run_analyze_task, task_id, req_data, folder, local_copy)
    return {"task_id": task_id, "status": "queued", "filename": source.name}

@app.get("/api/summary/{job_id}")
def get_saved_summary(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Proje bulunamad\u0131.")
    path = Path(job["folder"]) / "summary.json"
    if not path.is_file():
        raise HTTPException(404, "Bu proje i\u00e7in hen\u00fcz \u00f6zet video olu\u015fturulmad\u0131.")
    return json.loads(path.read_text(encoding="utf-8"))


@app.post("/api/summary/run")
def generate_summary(req: SummaryRequest, background_tasks: BackgroundTasks):
    job = jobs.get(req.job_id)
    if not job:
        raise HTTPException(404, "Proje bulunamad\u0131. \u00d6nce videoyu analiz et.")
    if not job.get("segments"):
        raise HTTPException(400, "\u00d6zet i\u00e7in transkript bulunamad\u0131.")
    task_id = uuid.uuid4().hex[:10]
    set_task(task_id, 1, "\u00d6zet video g\u00f6revi kuyru\u011fa al\u0131nd\u0131")
    background_tasks.add_task(run_summary_task, task_id, req.job_id, job, req.target_seconds, req.format,
                              req.transition, req.captions, req.chapter_titles)
    return {"task_id": task_id, "status": "queued", "job_id": req.job_id}


@app.post("/api/render")
def render(req: RenderRequest, background_tasks: BackgroundTasks):
    job = jobs.get(req.job_id)
    if not job: raise HTTPException(404, "İş bulunamadı. Videoyu yeniden analiz edin.")
    clip = next((c for c in job["clips"] if c["id"] == req.clip_id), None)
    if not clip: raise HTTPException(404, "Klip bulunamadı.")
    platforms = list(dict.fromkeys(req.platforms))
    if not platforms or any(p not in PLATFORMS for p in platforms):
        raise HTTPException(400, "Geçersiz platform seçimi.")
    task_id = uuid.uuid4().hex[:10]
    set_task(task_id, 1, "Render kuyruğa alındı", outputs=[])
    background_tasks.add_task(run_render_task, task_id, req, job, clip, platforms)
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/tasks/history")
def task_history(limit: int = 50):
    limit=max(1,min(200,limit))
    with sqlite3.connect(TASK_DB) as db:
        rows=db.execute("SELECT payload_json FROM tasks ORDER BY updated_at DESC LIMIT ?",(limit,)).fetchall()
    return {"tasks":[json.loads(r[0]) for r in rows]}

@app.get("/api/tasks/{task_id}/events")
def task_events(task_id: str):
    with sqlite3.connect(TASK_DB) as db:
        rows=db.execute("SELECT event_type,created_at,payload_json FROM task_events WHERE task_id=? ORDER BY id",(task_id,)).fetchall()
    if not rows:raise HTTPException(404,"Task history not found")
    return {"events":[{"event":r[0],"created_at":r[1],"state":json.loads(r[2])} for r in rows]}

@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    state=task_states.get(task_id)
    if state:return dict(state)
    with sqlite3.connect(TASK_DB) as db:
        row=db.execute("SELECT payload_json FROM tasks WHERE task_id=?",(task_id,)).fetchone()
    if not row:raise HTTPException(404,"Task not found")
    state=json.loads(row[0]);task_states[task_id]=state
    return state

@app.post("/api/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    with sqlite3.connect(TASK_DB) as db:
        row=db.execute("SELECT payload_json,status FROM tasks WHERE task_id=?",(task_id,)).fetchone()
    if not row:raise HTTPException(404,"Task not found")
    if row[1] in ("completed","failed","cancelled","interrupted"):return {"cancelled":False,"status":row[1]}
    _cancelled_tasks.add(task_id);state=json.loads(row[0])
    extra={k:v for k,v in state.items() if k not in ("task_id","percent","stage","status","created_at","updated_at")}
    set_task(task_id,state.get("percent",0),"Cancelled by user","cancelled",**extra)
    return {"cancelled":True,"status":"cancelled"}

@app.post("/api/tasks/{task_id}/retry")
def retry_task(task_id: str,background_tasks: BackgroundTasks):
    with sqlite3.connect(TASK_DB, timeout=10) as db:
        row=db.execute("SELECT payload_json,status FROM tasks WHERE task_id=?",(task_id,)).fetchone()
    if not row:raise HTTPException(404,"Task not found")
    old=json.loads(row[0]);data=old.get("request")
    if old.get("task_type")!="agents" or not data:raise HTTPException(400,"This task type cannot be retried automatically")
    if row[1] not in ("failed","interrupted","cancelled"):raise HTTPException(409,"Only failed, interrupted or cancelled agent tasks can be retried")
    req=TeamRequest(**data);job=jobs.get(req.job_id)
    if not job:raise HTTPException(409,"Reopen the source project before retrying")
    clip=next((c for c in job["clips"] if c["id"]==req.clip_id),None)
    if not clip:raise HTTPException(404,"Clip not found")
    new_id=uuid.uuid4().hex[:10]
    set_task(new_id,1,"Agent task queued for retry",task_type="agents",request=data,retry_of=task_id,outputs=[])
    background_tasks.add_task(run_agents_task,new_id,req,job,clip,list(req.platforms))
    return {"task_id":new_id,"status":"queued","retry_of":task_id}

@app.post("/api/metadata")
def metadata(req: MetadataRequest):
    job = jobs.get(req.job_id)
    if not job: raise HTTPException(404, "İş bulunamadı.")
    clip = next((c for c in job["clips"] if c["id"] == req.clip_id), None)
    if not clip: raise HTTPException(404, "Klip bulunamadı.")
    results = {}
    for platform in req.platforms:
        if platform not in PLATFORMS: continue
        fallback = fallback_metadata(clip, platform)
        prompt = (
            "Create social video metadata in the same language as the transcript. "
            "Return strict JSON with title, description, hashtags array. "
            "Do not claim facts not present in transcript. Use a compelling but honest hook. "
            f"Platform: {platform}. Transcript: {clip['text'][:1800]}"
        )
        try:
            data = llm_json(prompt, timeout=120)
            results[platform] = {
                "title": str(data.get("title", fallback["title"]))[:100],
                "description": str(data.get("description", fallback["description"]))[:2200],
                "hashtags": data.get("hashtags", fallback["hashtags"]),
                "platform": platform
            }
        except Exception:
            results[platform] = fallback
    return {"metadata": results}

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job: raise HTTPException(404, "İş bulunamadı.")
    return {"job_id": job_id, "duration": job["duration"], "language": job["language"], "clips": job["clips"]}

@app.get("/")
def home():
    return FileResponse(BASE / "web" / "index.html")

@app.get("/api/learning")
def learning_insights():
    return learning.insights()

@app.post("/api/learning/record")
def record_performance(req: PerformanceRequest):
    if req.platform not in PLATFORMS: raise HTTPException(400,"Geçersiz platform.")
    return learning.record(req.model_dump())


def render_generated_content_video(folder: Path, title: str, scenes: list[dict], audio: Path, captions: bool=True) -> Path:
    """Build a complete 9:16 narrated short from generated scene cards and neural narration."""
    require_binary("ffmpeg"); require_binary("ffprobe")
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Görsel sahne üretimi için Pillow eksik. requirements.txt bağımlılıklarını yükleyin.") from exc
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],capture_output=True,text=True)
    if probe.returncode: raise RuntimeError("Ses süresi okunamadı: "+probe.stderr[-500:])
    total=max(5.0,float(probe.stdout.strip()))
    clean_scenes=[x for x in scenes if isinstance(x,dict)]
    if not clean_scenes: clean_scenes=[{"narration":title,"visual_direction":title}]
    clean_scenes=clean_scenes[:8]
    weights=[max(1,len(str(x.get("narration","")).split())) for x in clean_scenes]
    total_weight=sum(weights);durations=[total*w/total_weight for w in weights]
    font_paths=[Path(r"C:\Windows\Fonts\arial.ttf"),Path(r"C:\Windows\Fonts\segoeui.ttf")]
    font_path=next((x for x in font_paths if x.exists()),None)
    def font(size):
        return ImageFont.truetype(str(font_path),size) if font_path else ImageFont.load_default()
    palette=[(18,29,57),(29,24,63),(10,55,66),(42,31,68),(20,43,70),(53,35,58),(12,54,59),(29,37,76)]
    clips=[]
    for idx,scene in enumerate(clean_scenes):
        bg=Image.new("RGB",(1080,1920),palette[idx%len(palette)])
        draw=ImageDraw.Draw(bg)
        for radius,outline in [(760,(67,221,204,70)),(590,(108,119,244,80)),(410,(255,255,255,30))]:
            draw.ellipse((540-radius,650-radius,540+radius,650+radius),outline=outline,width=5)
        draw.rounded_rectangle((72,110,1008,1810),radius=42,outline=(255,255,255),width=3)
        draw.rounded_rectangle((100,145,350,205),radius=24,fill=(73,205,185))
        draw.text((125,160),"YAMAN  /  SHORTS",font=font(25),fill=(7,22,33))
        draw.text((105,300),f"{idx+1:02d}  /  {len(clean_scenes):02d}",font=font(34),fill=(108,232,214))
        def wrap(text_value, fnt, max_width):
            words=str(text_value or "").split();lines=[];line=""
            for word in words:
                test=(line+" "+word).strip()
                if draw.textbbox((0,0),test,font=fnt)[2] <= max_width: line=test
                else:
                    if line: lines.append(line)
                    line=word
            if line: lines.append(line)
            return lines
        visual=str(scene.get("visual_direction") or scene.get("narration") or title).strip()
        lines=wrap(visual[:180],font(66),820)[:6];y=520
        for line in lines:
            draw.text((105,y),line,font=font(66),fill=(248,250,255),stroke_width=1,stroke_fill=(20,25,45));y+=92
        narration=str(scene.get("narration","")).strip()
        if captions and narration:
            cap_lines=wrap(narration[:260],font(36),820)[:5];cy=1260
            draw.rounded_rectangle((85,cy-28,995,cy+len(cap_lines)*54+30),radius=25,fill=(4,9,22))
            for line in cap_lines:
                draw.text((120,cy),line,font=font(36),fill=(255,255,255));cy+=54
        draw.text((105,1690),title[:54],font=font(27),fill=(178,202,226))
        png=folder/f"visual_scene_{idx+1:02d}.png";bg.save(png);bg.close()
        clip=folder/f"visual_scene_{idx+1:02d}.mp4";frames=max(1,int(round(durations[idx]*30)))
        vf=f"scale=1080:1920,zoompan=z='min(zoom+0.00035,1.045)':d={frames}:s=1080x1920:fps=30,format=yuv420p"
        run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-i",str(png),"-t",f"{durations[idx]:.3f}","-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(clip)],capture_output=True,text=True,encoding="utf-8",errors="replace")
        if run.returncode or not clip.is_file(): raise RuntimeError("Sahne render hatası: "+run.stderr[-900:])
        clips.append(clip)
    concat=folder/"visual_scenes.txt"
    concat.write_text("".join("file '"+x.name.replace("'","")+"'\n" for x in clips),encoding="utf-8")
    joined=folder/"visuals_joined.mp4"
    run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(joined)],capture_output=True,text=True)
    if run.returncode: raise RuntimeError("Sahneler birleştirilemedi: "+run.stderr[-900:])
    output=folder/"publish_ready_shorts.mp4"
    run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(joined),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-t",f"{total:.3f}","-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","21","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(output)],capture_output=True,text=True)
    if run.returncode or not output.is_file() or output.stat().st_size<1024: raise RuntimeError("Final MP4 render hatası: "+run.stderr[-1200:])
    return output



def render_cinematic_video(folder: Path, title: str, scenes: list[dict], voice: Path,
                           clips: list[Path], music: Path | None = None, trailer: bool = False) -> Path:
    """Normalize AI/stock B-roll, add cinematic title cards, narration and optional score."""
    require_binary("ffmpeg"); require_binary("ffprobe")
    from PIL import Image, ImageDraw, ImageFont
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(voice)],capture_output=True,text=True)
    if probe.returncode: raise RuntimeError("Ses süresi okunamadı: "+probe.stderr[-400:])
    total=max(5.0,float(probe.stdout.strip()))
    if not clips: raise RuntimeError("Sahne B-roll klipleri bulunamadı.")
    normalized=[];per_clip=total/len(clips)
    for idx,source in enumerate(clips):
        target=folder/f"normalized_{idx+1:02d}.mp4"
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-stream_loop","-1","-i",str(source),"-t",f"{per_clip:.3f}","-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20","-movflags","+faststart",str(target)]
        run=subprocess.run(cmd,capture_output=True,text=True)
        if run.returncode: raise RuntimeError("B-roll dikey render hatası: "+run.stderr[-700:])
        normalized.append(target)
    concat=folder/"cinematic_scenes.txt"
    concat.write_text("".join("file '"+x.name+"'\n" for x in normalized),encoding="utf-8")
    joined=folder/"cinematic_broll.mp4"
    run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(joined)],capture_output=True,text=True)
    if run.returncode: raise RuntimeError("Sahne montajı başarısız: "+run.stderr[-800:])
    font_path=Path(r"C:\Windows\Fonts\arial.ttf")
    def f(size): return ImageFont.truetype(str(font_path),size) if font_path.exists() else ImageFont.load_default()
    cards=[]
    labels=[("YAMAN ORIGINAL",title[:80]),("","COMING SOON" if trailer else "WATCH NOW")]
    for idx,(eyebrow,headline) in enumerate(labels):
        im=Image.new("RGB",(1080,1920),(7,10,20));d=ImageDraw.Draw(im)
        for radius in (360,560,780):
            d.ellipse((540-radius,700-radius,540+radius,700+radius),outline=(44,90+idx*25,112+idx*25),width=4)
        d.rectangle((80,130,1000,1790),outline=(170,195,220),width=2)
        d.text((120,240),eyebrow,font=f(30),fill=(110,224,207))
        words=headline.split();lines=[];line=""
        for word in words:
            candidate=(line+" "+word).strip()
            if d.textbbox((0,0),candidate,font=f(76))[2] < 820: line=candidate
            else:
                if line: lines.append(line)
                line=word
        if line: lines.append(line)
        y=790 if idx==0 else 900
        for text_line in lines[:5]:
            d.text((120,y),text_line,font=f(76),fill=(248,250,255));y+=105
        d.text((120,1650),"YAMAN VIRAL STUDIO PRO",font=f(24),fill=(130,150,180))
        image=folder/f"cinematic_card_{idx+1}.png";im.save(image);im.close()
        video=folder/f"cinematic_card_{idx+1}.mp4";seconds=2.2 if idx==0 else 2.8
        run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-i",str(image),"-t",str(seconds),"-vf",f"zoompan=z='min(zoom+0.0004,1.04)':d={int(seconds*30)}:s=1080x1920:fps=30,format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","22",str(video)],capture_output=True,text=True)
        if run.returncode: raise RuntimeError("Fragman başlık kartı oluşturulamadı: "+run.stderr[-500:])
        cards.append(video)
    final_parts=[cards[0],joined,cards[1]]
    listfile=folder/"final_cinematic_list.txt"
    listfile.write_text("".join("file '"+x.name+"'\n" for x in final_parts),encoding="utf-8")
    video_only=folder/"cinematic_video_only.mp4"
    run=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(listfile),"-c","copy",str(video_only)],capture_output=True,text=True)
    if run.returncode: raise RuntimeError("Final fragman birleştirilemedi: "+run.stderr[-500:])
    output=folder/"cinematic_trailer.mp4" if trailer else folder/"cinematic_shorts.mp4"
    if music and music.is_file():
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(video_only),"-i",str(voice),"-stream_loop","-1","-i",str(music),"-filter_complex","[1:a]volume=1.0,apad=pad_dur=5[voice];[2:a]volume=0.16,afade=t=in:st=0:d=1.2,afade=t=out:st="+str(max(1,total-2))+":d=2[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[a]","-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(output)]
    else:
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(video_only),"-i",str(voice),"-filter:a","apad=pad_dur=5","-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(output)]
    run=subprocess.run(cmd,capture_output=True,text=True)
    if run.returncode or not output.is_file(): raise RuntimeError("Final video ses miksajı başarısız: "+run.stderr[-900:])
    return output


@app.get("/api/content/voices")
def content_voice_catalog():
    return {"voices": content_factory.VOICE_CATALOG, "engine":"edge-tts", "mode":"online-neural"}

@app.post("/api/content/trends")
def content_trends(req: TrendResearchRequest):
    try:
        return content_factory.research_trends(req.niche, req.region, req.limit)
    except Exception as exc:
        raise HTTPException(502, f"Trend kaynaklarına erişilemedi: {str(exc)[:240]}")

@app.post("/api/content/script")
def content_script(req: ScriptRequest):
    try:
        result=content_factory.generate_script(OLLAMA_URL, OLLAMA_MODEL, req.niche, req.topic, req.language, req.duration)
        folder=WORK / "autopilot-content"
        folder.mkdir(parents=True,exist_ok=True)
        item_id=uuid.uuid4().hex[:12]
        payload={"id":item_id,"niche":req.niche,"topic":req.topic,"language":req.language,"duration":req.duration,**result}
        (folder / f"{item_id}.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        (folder / f"{item_id}.md").write_text(f"# {payload['title']}\n\n{payload['script']}\n",encoding="utf-8")
        payload["script_url"]=f"/workspace/autopilot-content/{item_id}.md"
        return payload
    except requests.RequestException as exc:
        raise HTTPException(502, f"Ollama servisine erişilemedi: {str(exc)[:220]}")
    except Exception as exc:
        raise HTTPException(500, f"Senaryo üretilemedi: {str(exc)[:220]}")

@app.post("/api/content/voiceover")
def content_voiceover(req: VoiceoverRequest):
    folder=WORK / "autopilot-content"
    folder.mkdir(parents=True,exist_ok=True)
    item_id=uuid.uuid4().hex[:12]
    output=folder / f"{item_id}.mp3"
    try:
        content_factory.create_voiceover(req.text,req.voice,output)
        return {"id":item_id,"voice":req.voice,"engine":"Microsoft Edge neural voices (edge-tts)","mode":"online","audio_url":f"/workspace/autopilot-content/{item_id}.mp3","bytes":output.stat().st_size,
                "notice":"Seslendirme internet bağlantısı üzerinden oluşturuldu. Metin üçüncü taraf TTS servisine gönderilir."}
    except Exception as exc:
        output.unlink(missing_ok=True)
        raise HTTPException(502, f"Seslendirme oluşturulamadı: {str(exc)[:240]}")



@app.post("/api/content/create-cinematic")
def content_create_cinematic(req: CompleteVideoRequest):
    folder=WORK/"cinematic-content";folder.mkdir(parents=True,exist_ok=True)
    item_id=uuid.uuid4().hex[:12];work=folder/item_id;work.mkdir(parents=True,exist_ok=True)
    runway_key,pexels_key=_visual_provider_keys()
    if req.visual_provider=="runway" and not runway_key:
        raise HTTPException(400,"Gerçek AI sahne üretimi için Ayarlar > AI Görsel Motorları bölümüne Runway API anahtarını kaydedin.")
    if req.visual_provider=="pexels" and not pexels_key:
        raise HTTPException(400,"Sahne B-roll için Pexels API anahtarını Ayarlar > AI Görsel Motorları bölümüne kaydedin.")
    if req.generate_music and req.visual_provider!="runway":
        raise HTTPException(400,"AI müzik üretimi için Runway görsel motorunu seçin.")
    topic=req.topic.strip();trend_data=None
    try:
        if not topic and req.auto_trend:
            trend_data=content_factory.research_trends(req.niche,req.region,12)
            if trend_data.get("topics"): topic=trend_data["topics"][0]["title"]
        if not topic: raise HTTPException(400,"Konu girin veya otomatik trend araştırmasını açın.")
        style=req.style
        script=content_factory.generate_script(OLLAMA_URL,OLLAMA_MODEL,req.niche,topic,req.language,req.duration,style,req.shot_count)
        scenes=script.get("scenes",[])[:req.shot_count]
        if len(scenes)<2: raise RuntimeError("AI yönetmen yeterli sahne planı oluşturamadı.")
        voice=work/"narration.mp3";content_factory.create_voiceover(script["script"],req.voice,voice)
        clips=[];pexels_credits=[];provider=req.visual_provider
        if provider=="runway":
            if not runway_key: raise HTTPException(400,"Gerçek AI sahne üretimi için Ayarlar > AI Görsel Motorları bölümüne Runway API anahtarını kaydedin.")
            client=visual_factory.RunwayClient(runway_key)
            for index,scene in enumerate(scenes):
                prompt=str(scene.get("visual_direction") or scene.get("narration") or topic)
                shot_prompt=("Cinematic vertical 9:16 film still, photorealistic, high production value, no text, no logos, no watermark. "+prompt+". Consistent visual identity, realistic materials, intentional composition, dramatic lighting.")
                image=client.generate_image(shot_prompt,work/f"ai_scene_{index+1:02d}.png")
                motion=str(scene.get("camera_motion") or "slow cinematic dolly movement, subtle environmental motion")
                video_prompt=(prompt+". "+motion+". Cinematic natural movement, coherent subject motion, no cuts, no text or logos.")
                clips.append(client.animate_image(image,video_prompt,work/f"ai_broll_{index+1:02d}.mp4",seconds=5))
        elif provider=="pexels":
            if not pexels_key: raise HTTPException(400,"Sahne B-roll için Pexels API anahtarını Ayarlar > AI Görsel Motorları bölümüne kaydedin.")
            for index,scene in enumerate(scenes):
                query=str(scene.get("visual_direction") or scene.get("narration") or topic)
                found=visual_factory.search_pexels_video(pexels_key,query,work/f"pexels_broll_{index+1:02d}.mp4")
                clips.append(found["path"])
                pexels_credits.append({"photographer":found.get("photographer","Pexels contributor"),"page":found.get("page","")})
            (work/"pexels-attribution.json").write_text(json.dumps({"provider":"Pexels","credits":pexels_credits},ensure_ascii=False,indent=2),encoding="utf-8")
        else:
            result=render_generated_content_video(work,script["title"],scenes,voice,req.captions)
            clips=[result]
        music=None
        if req.generate_music and provider=="runway":
            music=work/"cinematic_score.mp3"
            mood=("Dark cinematic trailer score, deep orchestral drones, pulsing low strings, rising brass, massive impacts and emotional crescendo, instrumental no vocals" if style=="trailer" else "Modern energetic electronic instrumental background score, uplifting build")
            client.generate_music(mood,req.duration,music)
        final_video=render_cinematic_video(work,script["title"],scenes,voice,clips,music,style=="trailer")
        (work/"script.json").write_text(json.dumps({"id":item_id,"style":style,"topic":topic,**script},ensure_ascii=False,indent=2),encoding="utf-8")
        (work/"script.md").write_text("# "+script["title"]+"\n\n"+script["script"]+"\n",encoding="utf-8")
        if trend_data: (work/"trend-report.json").write_text(json.dumps(trend_data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"id":item_id,"title":script["title"],"style":style,"video_url":f"/workspace/cinematic-content/{item_id}/{final_video.name}",
            "audio_url":f"/workspace/cinematic-content/{item_id}/narration.mp3","script_url":f"/workspace/cinematic-content/{item_id}/script.md",
            "filename":final_video.name,"duration_seconds":round(probe_duration(final_video),1),
            "size_mb":round(final_video.stat().st_size/(1024*1024),2),"visual_provider":provider,
            "visuals":[f"/workspace/cinematic-content/{item_id}/{x.name}" for x in clips],"pexels_credits":pexels_credits,
            "notice":"Runway AI görsel/video/müzik üretimi ücretli sağlayıcı kredisi tüketir. Pexels klipleri stok B-roll'dur, AI üretimi değildir. Motion yerel grafik yedeğidir. Yayın öncesi içerik ve kullanım haklarını kontrol edin."}
    except HTTPException: raise
    except visual_factory.VisualProviderError as exc: raise HTTPException(502,str(exc)[:900])
    except requests.RequestException as exc: raise HTTPException(502,"Görsel üretim servisi bağlantı hatası: "+str(exc)[:500])
    except Exception as exc: raise HTTPException(500,"Sinematik video üretim hatası: "+str(exc)[:700])


@app.post("/api/content/create-video")
def content_create_video(req: CompleteVideoRequest):
    folder=WORK/"autopilot-content";folder.mkdir(parents=True,exist_ok=True)
    item_id=uuid.uuid4().hex[:12];work=folder/item_id;work.mkdir(parents=True,exist_ok=True)
    trend_data=None;topic=req.topic.strip()
    try:
        if not topic and req.auto_trend:
            trend_data=content_factory.research_trends(req.niche,req.region,12)
            if trend_data.get("topics"): topic=trend_data["topics"][0]["title"]
        if not topic: raise HTTPException(400,"Bir konu girin veya otomatik trend araştırmasını açın.")
        script=content_factory.generate_script(OLLAMA_URL,OLLAMA_MODEL,req.niche,topic,req.language,req.duration)
        audio=work/"narration.mp3";content_factory.create_voiceover(script["script"],req.voice,audio)
        video=render_generated_content_video(work,script["title"],script.get("scenes",[]),audio,req.captions)
        script_payload={"id":item_id,"niche":req.niche,"topic":topic,"language":req.language,**script}
        script_path=work/"script.md";script_path.write_text("# "+script_payload["title"]+"\n\n"+script_payload["script"]+"\n",encoding="utf-8")
        (work/"script.json").write_text(json.dumps(script_payload,ensure_ascii=False,indent=2),encoding="utf-8")
        if trend_data: (work/"trend-report.json").write_text(json.dumps(trend_data,ensure_ascii=False,indent=2),encoding="utf-8")
        return {"id":item_id,"title":script_payload["title"],"topic":topic,"video_url":f"/workspace/autopilot-content/{item_id}/publish_ready_shorts.mp4",
            "audio_url":f"/workspace/autopilot-content/{item_id}/narration.mp3","script_url":f"/workspace/autopilot-content/{item_id}/script.md",
            "filename":"YAMAN_"+item_id+"_SHORTS.mp4","duration_seconds":round(probe_duration(video),1),"size_mb":round(video.stat().st_size/(1024*1024),2),
            "visual_mode":"Yerel AI sahne kartları · hareketli tipografik motion graphics","trend_sources":trend_data.get("sources",[]) if trend_data else [],
            "notice":"Video, senaryoya göre otomatik tasarlanmış hareketli grafik sahneleri ve AI seslendirme ile üretildi. Fotogerçekçi AI görsel/video üretimi veya stok görüntü bu sürümde kullanılmıyor. Edge TTS çevrimiçidir; ses metni Microsoft hizmetine gönderilir."}
    except HTTPException: raise
    except requests.RequestException as exc: raise HTTPException(502,"Yerel Ollama veya trend servisi hatası: "+str(exc)[:240])
    except Exception as exc: raise HTTPException(500,"Video üretim hatası: "+str(exc)[:500])

@app.get("/api/autopilot")
def list_autopilots():
    return {"autopilots": autopilot_store.list_autopilots(TASK_DB),
            "source_folder": str(DOWNLOADS_DIR), "mode": "local-folder-watch",
            "publishing": "manual-approval-required"}

@app.post("/api/autopilot")
def create_autopilot(req: AutopilotRequest):
    if req.min_seconds >= req.max_seconds:
        raise HTTPException(422, "Minimum klip süresi maksimum süreden küçük olmalı.")
    platforms = list(dict.fromkeys(req.platforms))
    if not platforms or any(p not in PLATFORMS for p in platforms):
        raise HTTPException(422, "YouTube, Instagram veya TikTok seçin.")
    data = req.model_dump()
    data["platforms"] = platforms
    try: item = autopilot_store.create_autopilot(TASK_DB, data)
    except ValueError as exc: raise HTTPException(422, str(exc))
    return {"autopilot": item}

@app.patch("/api/autopilot/{autopilot_id}")
def patch_autopilot(autopilot_id: str, req: AutopilotRequest):
    if req.min_seconds >= req.max_seconds:
        raise HTTPException(422, "Minimum klip süresi maksimum süreden küçük olmalı.")
    platforms = list(dict.fromkeys(req.platforms))
    if not platforms or any(p not in PLATFORMS for p in platforms):
        raise HTTPException(422, "Geçersiz platform seçimi.")
    try: item = autopilot_store.update_autopilot(TASK_DB, autopilot_id, {**req.model_dump(), "platforms": platforms})
    except ValueError as exc: raise HTTPException(422, str(exc))
    if not item: raise HTTPException(404, "Autopilot bulunamadı.")
    return {"autopilot": item}

@app.delete("/api/autopilot/{autopilot_id}")
def remove_autopilot(autopilot_id: str):
    if not autopilot_store.delete_autopilot(TASK_DB, autopilot_id):
        raise HTTPException(404, "Autopilot bulunamadı.")
    return {"deleted": True}

@app.post("/api/autopilot/{autopilot_id}/run")
def run_autopilot_now(autopilot_id: str, background_tasks: BackgroundTasks):
    item = autopilot_store.get_autopilot(TASK_DB, autopilot_id)
    if not item: raise HTTPException(404, "Autopilot bulunamadı.")
    claim = autopilot_store.claim_manual(TASK_DB, autopilot_id)
    if claim == "running": raise HTTPException(409, "Bu Autopilot zaten çalışıyor.")
    if claim == "missing": raise HTTPException(404, "Autopilot bulunamadı.")
    background_tasks.add_task(run_autopilot_cycle, item)
    return {"queued": True, "message": "Autopilot çalıştırma kuyruğa alındı."}

def run_autopilot_cycle(item: dict):
    """Watch Downloads, analyze the newest unseen source, render top clips, and leave them for approval."""
    source = None
    task_id = uuid.uuid4().hex[:10]
    outputs = []
    notes = []
    try:
        # Every scheduled cycle first discovers a timely topic and creates a ready-to-narrate script.
        content_folder = WORK / "autopilot-content" / task_id
        content_folder.mkdir(parents=True, exist_ok=True)
        chosen_topic = item["niche"] + " için güncel gelişmeler"
        try:
            trends = content_factory.research_trends(item["niche"], "TR", 12)
            if trends.get("topics"):
                chosen_topic = trends["topics"][0]["title"]
                (content_folder / "trends.json").write_text(json.dumps(trends, ensure_ascii=False, indent=2), encoding="utf-8")
                outputs.append({"type":"trend_research","title":chosen_topic,"url":f"/workspace/autopilot-content/{task_id}/trends.json"})
        except Exception as trend_error:
            notes.append("Trend araştırması: " + str(trend_error)[:140])
        script_language = "en" if item.get("language") == "en" else "tr"
        try:
            script = content_factory.generate_script(OLLAMA_URL, OLLAMA_MODEL, item["niche"], chosen_topic, script_language, 60)
            (content_folder / "script.md").write_text("# " + script.get("title", chosen_topic) + "\n\n" + script["script"] + "\n", encoding="utf-8")
            outputs.append({"type":"script","title":script.get("title",chosen_topic),"url":f"/workspace/autopilot-content/{task_id}/script.md"})
            voice = "en-US-AriaNeural" if script_language == "en" else "tr-TR-EmelNeural"
            try:
                audio = content_factory.create_voiceover(script["script"], voice, content_folder / "narration.mp3")
                outputs.append({"type":"voiceover","title":voice,"url":f"/workspace/autopilot-content/{task_id}/narration.mp3","bytes":audio.stat().st_size})
            except Exception as voice_error:
                notes.append("AI seslendirme: " + str(voice_error)[:140])
        except Exception as script_error:
            notes.append("Senaryo üretimi: " + str(script_error)[:160])
        if not DOWNLOADS_DIR.is_dir():
            if outputs:
                message = "Trend araştırması ve içerik taslağı hazır. " + " | ".join(notes) + " Kaynak video bekleniyor."
                autopilot_store.finish_run(TASK_DB, item["id"], "review", message, task_id, None, outputs)
                return
            raise RuntimeError("İndirilenler klasörü bulunamadı ve içerik üretimi tamamlanamadı.")
        seen = set(item.get("processed_files", []))
        candidates = []
        for file in DOWNLOADS_DIR.iterdir():
            try:
                if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS and file.name not in seen:
                    candidates.append(file)
            except OSError: continue
        if not candidates:
            if outputs:
                message = "Trend konusu, senaryo ve mevcut seslendirme çıktıları hazır. Yeni kaynak video bekleniyor. " + " | ".join(notes)
                autopilot_store.finish_run(TASK_DB, item["id"], "review", message, task_id, None, outputs)
                return
            raise RuntimeError("İşlenecek yeni video yok. İndirilenler klasörüne yeni bir video ekleyin. " + " | ".join(notes))
        source = max(candidates, key=lambda p: p.stat().st_mtime)
        folder = WORK / task_id
        folder.mkdir(parents=True, exist_ok=True)
        local_copy = folder / ("source" + source.suffix.lower())
        shutil.copy2(source, local_copy)
        req = AnalyzeRequest(url=None, clips=item["clips"], min_seconds=item["min_seconds"],
                             max_seconds=item["max_seconds"], language=item["language"])
        set_task(task_id, 1, "Autopilot · kaynak analiz ediliyor", task_type="autopilot",
                 autopilot_id=item["id"], source_file=source.name)
        run_analyze_task(task_id, req, folder, local_copy)
        state = task_states.get(task_id, {})
        if state.get("status") != "completed":
            raise RuntimeError(state.get("error", "Video analizi tamamlanamadı."))
        job = jobs.get(task_id)
        if not job: raise RuntimeError("Analiz projesi oluşturulamadı.")
        # Re-rank transcript clips for the channel niche; retain existing scores on fallback.
        try:
            set_task(task_id, 88, "Autopilot · kanal nişine göre editoryal sıralama")
            niche_prompt = (
                "Türkçe yanıt ver. Aşağıdaki video kesitlerini kanal nişine uygunluk, "
                "tek başına anlaşılabilirlik, güçlü açılış ve izleyiciye sunduğu değer açısından "
                "0-100 arasında puanla. Kaynak metinde olmayan bilgi ekleme ve viral olma garantisi verme. "
                "JSON: {clips:[{id,score,reason,title}]}. Kanal nişi: " + item["niche"] +
                ". Kesitler: " + json.dumps([{"id": c["id"], "text": c["text"][:900]} for c in job["clips"]], ensure_ascii=False)
            )
            niche_result = llm_json(niche_prompt, timeout=90, num_predict=900)
            niche_rows = niche_result.get("clips", []) if isinstance(niche_result, dict) else []
            niche_by_id = {int(x["id"]): x for x in niche_rows if isinstance(x, dict) and "id" in x}
            for candidate in job["clips"]:
                scored = niche_by_id.get(candidate["id"])
                if scored:
                    candidate["score"] = max(0, min(100, int(scored.get("score", candidate["score"]))))
                    candidate["reason"] = str(scored.get("reason", candidate.get("reason", "")))[:500]
                    candidate["title"] = str(scored.get("title", candidate.get("title", "")))[:160]
            save_job(task_id, job)
        except Exception:
            pass
        selected = sorted(job["clips"], key=lambda c: c.get("score", 0), reverse=True)[:3]
        rendered = list(outputs)
        for clip in selected:
            render_id = uuid.uuid4().hex[:10]
            render_req = RenderRequest(job_id=task_id, clip_id=clip["id"], platforms=item["platforms"], captions=True)
            set_task(render_id, 1, "Autopilot · platform çıktıları hazırlanıyor",
                     task_type="autopilot_render", autopilot_id=item["id"], source_file=source.name, outputs=[])
            run_render_task(render_id, render_req, job, clip, item["platforms"])
            render_state = task_states.get(render_id, {})
            if render_state.get("status") != "completed":
                raise RuntimeError(render_state.get("error", "Platform render işlemi başarısız."))
            rendered.extend(render_state.get("outputs", []))
        message = f"{source.name}: {len(selected)} kesit hazır. Trend, senaryo ve seslendirme çıktıları da üretildi. Yayın öncesi onay bekliyor. " + " | ".join(notes)
        autopilot_store.finish_run(TASK_DB, item["id"], "review", message, task_id, task_id, rendered, source.name)
    except Exception as exc:
        autopilot_store.finish_run(TASK_DB, item["id"], "failed", str(exc), task_id,
                                   task_id if task_id in jobs else None, [], None)

def _autopilot_scheduler():
    while not _scheduler_stop.is_set():
        try:
            for item in autopilot_store.claim_due(TASK_DB):
                if _scheduler_stop.is_set():
                    break
                run_autopilot_cycle(item)
        except Exception:
            pass
        _scheduler_stop.wait(20)


def start_autopilot_scheduler():
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        return
    _scheduler_thread = threading.Thread(
        target=_autopilot_scheduler, name="yaman-autopilot-scheduler", daemon=True
    )
    _scheduler_thread.start()


def run_agents_task(task_id: str, req: TeamRequest, job: dict, clip: dict, platforms: list[str]):
    """Run the specialist team, journal each step and persist its report."""
    try:
        agent_names={item["id"]:item["name"] for item in AGENT_CATALOG}
        agent_states={}
        def on_agent_progress(agent_id,status):
            agent_states[agent_id]=status
            done=sum(value=="completed" for value in agent_states.values())
            name=agent_names.get(agent_id,agent_id)
            total=len(AGENT_CATALOG)
            percent=min(95,2+int(done/total*93))
            stage=name+" \u00b7 "+("Tamamland\u0131" if status=="completed" else "\u00c7al\u0131\u015f\u0131yor")
            set_task(task_id,percent,stage,agent_statuses=dict(agent_states),
                current_agent=agent_id,completed_agents=done,total_agents=total)
        set_task(task_id,2,"12 uzman ajan ba\u015flat\u0131l\u0131yor",agent_statuses={})
        def task_llm(prompt,**kwargs):
            if task_is_cancelled(task_id):raise RuntimeError("Task cancelled by user")
            result=llm_json(prompt,**kwargs)
            if task_is_cancelled(task_id):raise RuntimeError("Task cancelled by user")
            return result
        report=run_agent_team(task_llm,job,clip,platforms,progress_callback=on_agent_progress)
        report["job_id"]=req.job_id;report["task_id"]=task_id
        report_path=Path(job["folder"])/f"agents_clip_{req.clip_id}.json"
        temp_path=report_path.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        temp_path.replace(report_path)
        summary=report.get("summary",{})
        stage="Ajan raporlar\u0131 haz\u0131r \u00b7 {} ba\u015far\u0131l\u0131 \u00b7 {} yedek \u00b7 {} hata".format(
            summary.get("completed",0),summary.get("fallback",0),summary.get("failed",0))
        set_task(task_id,100,stage,"completed",result=report)
    except Exception as exc:
        if task_is_cancelled(task_id):
            set_task(task_id,task_states.get(task_id,{}).get("percent",0),"Task cancelled","cancelled",error="Cancelled by user")
        else:
            set_task(task_id,100,"Agent team failed","failed",error=str(exc)[:500])


@app.post("/api/agents/run")
def agents_run(req: TeamRequest, background_tasks: BackgroundTasks):
    job = jobs.get(req.job_id)
    if not job:
        raise HTTPException(404, "\u0130\u015f bulunamad\u0131.")
    clip = next((c for c in job["clips"] if c["id"] == req.clip_id), None)
    if not clip:
        raise HTTPException(404, "Klip bulunamad\u0131.")
    platforms = list(dict.fromkeys(req.platforms))
    if not platforms or any(p not in PLATFORMS for p in platforms):
        raise HTTPException(400, "Ge\u00e7ersiz platform.")
    task_id = uuid.uuid4().hex[:10]
    set_task(task_id,1,"Ajan ekibi kuyru\u011fa al\u0131nd\u0131",outputs=[],task_type="agents",
        request={"job_id":req.job_id,"clip_id":req.clip_id,"platforms":platforms})
    background_tasks.add_task(run_agents_task, task_id, req, job, clip, platforms)
    return {"task_id": task_id, "status": "queued", "job_id": req.job_id, "clip_id": req.clip_id}

@app.get("/api/agents/report/{job_id}/{clip_id}")
def get_agent_report(job_id: str, clip_id: int):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "İş bulunamadı.")
    report_path = Path(job["folder"]) / f"agents_clip_{clip_id}.json"
    if not report_path.is_file():
        raise HTTPException(404, "Bu kesit için henüz ajan raporu yok.")
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(500, f"Ajan raporu okunamadı: {exc}")
