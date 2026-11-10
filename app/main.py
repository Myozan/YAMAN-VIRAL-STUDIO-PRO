from __future__ import annotations
import ctypes, json, os, re, shutil, subprocess, sys, time, uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yt_dlp
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl
from app.learning import ViralLearningEngine
from app.agents import run_agent_team
from app.framing import render_face_tracked

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
app = FastAPI(title="YAMAN VIRAL STUDIO PRO", version="1.0.0")
app.mount("/assets", StaticFiles(directory=BASE / "web"), name="assets")
app.mount("/workspace", StaticFiles(directory=WORK), name="workspace")
jobs: dict[str, dict[str, Any]] = {}
task_states: dict[str, dict[str, Any]] = {}
_cpu_sample = None
learning = ViralLearningEngine(WORK / "viral_learning.sqlite3")
_whisper = None

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    clips: int = Field(default=8, ge=1, le=20)
    min_seconds: int = Field(default=20, ge=10, le=60)
    max_seconds: int = Field(default=55, ge=20, le=180)
    language: str = "auto"

class RenderRequest(BaseModel):
    job_id: str
    clip_id: int
    platforms: list[str] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])
    captions: bool = True

class PerformanceRequest(BaseModel):
    clip_fingerprint: str = Field(min_length=8, max_length=128)
    platform: str
    views: int = Field(ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    avg_watch_seconds: float = Field(default=0, ge=0)
    video_seconds: float = Field(gt=0)

class TeamRequest(BaseModel):
    job_id: str
    clip_id: int
    platforms: list[str] = Field(default_factory=lambda: ['youtube','instagram','tiktok'])

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
        raise RuntimeError(f"{name} bulunamadÄ±. Kurup PATH'e ekleyin.")

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
    host = (urlparse(url).hostname or "").lower()
    allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtube-nocookie.com"}
    if host not in allowed:
        raise ValueError("GÃ¼venlik nedeniyle yalnÄ±zca youtube.com veya youtu.be baÄŸlantÄ±larÄ± kabul edilir.")

def download_video(url: str, folder: Path, progress_callback=None) -> Path:
    validate_youtube_url(url)
    def download_hook(data):
        if progress_callback and data.get("status") == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            downloaded = data.get("downloaded_bytes", 0)
            if total:
                progress_callback(8 + min(14, int(downloaded / total * 14)), "Video indiriliyor")
        elif progress_callback and data.get("status") == "finished":
            progress_callback(22, "Video indirildi, hazÄ±rlanÄ±yor")
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
    raise RuntimeError("Video dosyasÄ± indirilemedi.")

def probe_duration(path: Path) -> float:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    if p.returncode:
        raise RuntimeError("Video bilgisi okunamadÄ±: " + p.stderr[-1000:])
    return float(p.stdout.strip())

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
                progress_callback(part, f"Whisper konuÅŸmayÄ± Ã§Ã¶zÃ¼mlÃ¼yor Â· {part}%")
        return result, info.language

    result, detected_language = run_transcription(True)
    recognized_words = sum(len(item["text"].split()) for item in result)

    # VAD Ã§ok az konuÅŸma bulursa filtresiz tekrar dene.
    if not result or recognized_words < 8:
        retry_result, retry_language = run_transcription(False)
        retry_words = sum(len(item["text"].split()) for item in retry_result)
        if retry_words > recognized_words:
            result, detected_language = retry_result, retry_language

    return result, detected_language

def heuristic_score(text: str) -> tuple[int, list[str]]:
    t = text.lower()
    score, reasons = 35, []
    hooks = ["ama", "Ã§Ã¼nkÃ¼", "aslÄ±nda", "inanÄ±lmaz", "nasÄ±l", "neden", "sÄ±r", "hata", "gerÃ§ek", "kimse", "however", "secret", "mistake", "why", "how"]
    hits = [w for w in hooks if w in t]
    score += min(25, len(hits) * 5)
    if hits: reasons.append("Merak uyandÄ±ran ifade")
    if "?" in text: score += 8; reasons.append("Soru / merak unsuru")
    if "!" in text: score += 4; reasons.append("Duygu / vurgu")
    n = len(text.split())
    if 35 <= n <= 120: score += 15; reasons.append("KÄ±sa ve anlaÅŸÄ±lÄ±r anlatÄ±m")
    elif n > 170: score -= 8
    if re.search(r"\d", text): score += 4; reasons.append("Somut bilgi veya sayÄ±")
    return max(1, min(95, score)), reasons or ["Editoryal deÄŸerlendirme gerekli"]

def llm_json(prompt: str, timeout: int = 180):
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "think": False, "keep_alive": 0, "options": {"num_predict": 512}},
        timeout=timeout
    )
    r.raise_for_status()
    return json.loads(r.json().get("response", "{}"))

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
    """KonuÅŸma segmentlerinden esnek, sabit sÃ¼reli klip adaylarÄ± Ã¼retir."""
    candidates = []
    seen = set()

    if not segments or duration <= 0:
        return candidates

    effective_min = min(int(min_s), 12)
    effective_max = max(int(max_s), effective_min)
    window_seconds = min(effective_max, int(duration))

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

        if len(text.split()) < 8:
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
WrapStyle: 2
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

def render_variant(job: dict, clip: dict, platform: str, captions: bool, face_tracking: bool = True) -> Path:
    profile = PLATFORMS[platform]
    folder = Path(job["folder"])
    out = folder / f"clip_{clip['id']}_{platform}.mp4"
    source_video = Path(job["video"])
    if face_tracking:
        tracked = folder / ("clip_" + str(clip["id"]) + "_" + platform + "_tracked.mp4")
        render_face_tracked(source_video, tracked, clip["start"], clip["duration"], profile["width"], profile["height"])
        source_video = tracked
    vf = f"scale={profile['width']}:{profile['height']}:force_original_aspect_ratio=increase,crop={profile['width']}:{profile['height']},setsar=1"
    if captions:
        ass = folder / f"clip_{clip['id']}_{platform}.ass"
        create_ass(job["segments"], clip, ass, profile["margin"])
        vf += f",ass='{escape_filter_path(ass)}'"
    command([
        "ffmpeg", "-y", "-i", str(source_video), "-t", str(clip["duration"]),
        "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)
    ])
    return out

def fallback_metadata(clip: dict, platform: str):
    title = re.sub(r"\s+", " ", clip.get("title", "Ä°zlemeden geÃ§me!")).strip()[:95]
    tags = ["#shorts", "#reels", "#tiktok", "#keÅŸfet", "#viral"]
    return {"title": title, "description": clip["text"][:400] + "\n\n" + " ".join(tags),
            "hashtags": tags, "platform": platform}

def system_metrics():
    """Windows sistem CPU ve RAM kullanÄ±mÄ±nÄ± anlÄ±k Ã¶lÃ§er; harici paket gerektirmez."""
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
            raise OSError("RAM bilgisi okunamadÄ±")
        idle1, kernel1, user1 = FILETIME(), FILETIME(), FILETIME()
        if not kernel.GetSystemTimes(ctypes.byref(idle1), ctypes.byref(kernel1), ctypes.byref(user1)):
            raise OSError("CPU bilgisi okunamadÄ±")
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
        result = {"cpu_percent": cpu, "ram_percent": round(used / total * 100, 1) if total else 0,
                  "ram_used_mb": round(used / 1048576), "ram_total_mb": round(total / 1048576)}
        smi = shutil.which("nvidia-smi") or r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
        if Path(smi).is_file():
            try:
                gpu = subprocess.run([smi, "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                    "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if gpu.returncode == 0 and gpu.stdout.strip():
                    parts = [x.strip() for x in gpu.stdout.strip().splitlines()[0].split(",")]
                    result.update({"gpu_available": True, "gpu_name": parts[0],
                        "gpu_percent": float(parts[1]), "vram_used_mb": float(parts[2]),
                        "vram_total_mb": float(parts[3]), "gpu_temp_c": float(parts[4])})
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

@app.get("/api/health")
def health():
    ffmpeg = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
    ollama = False
    try: ollama = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).ok
    except Exception: pass
    return {"ok": True, "ffmpeg": ffmpeg, "ollama": ollama, "model": OLLAMA_MODEL,
            "whisper_model": WHISPER_MODEL, "platforms": list(PLATFORMS)}

@app.get("/api/platforms")
def platforms():
    return {
        key: {**value, "connected": False, "connection_mode": "OAuth not configured"}
        for key, value in PLATFORMS.items()
    }

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

@app.get("/api/settings")
def get_settings():
    return {"ollama_url": OLLAMA_URL, "ollama_model": OLLAMA_MODEL,
            "whisper_model": WHISPER_MODEL, "whisper_device": WHISPER_DEVICE,
            "available_whisper_models": ["tiny", "base", "small", "medium", "large-v3"],
            "local_only": True}

@app.post("/api/settings")
def update_settings(req: SettingsRequest):
    global OLLAMA_MODEL, WHISPER_MODEL, WHISPER_DEVICE, _whisper
    if not re.fullmatch(r"[A-Za-z0-9._:-]+", req.ollama_model):
        raise HTTPException(400, "GeÃ§ersiz Ollama model adÄ±.")
    OLLAMA_MODEL = req.ollama_model
    WHISPER_MODEL = req.whisper_model
    WHISPER_DEVICE = req.whisper_device
    _whisper = None
    config_path = BASE / "settings.local.json"
    config_path.write_text(json.dumps(req.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return {"saved": True, "settings": req.model_dump()}

def set_task(task_id: str, percent: int, stage: str, status: str = "running", **extra):
    state = task_states.setdefault(task_id, {})
    state.update({"task_id": task_id, "percent": max(0, min(100, int(percent))),
                  "stage": stage, "status": status, **extra})

def run_analyze_task(task_id: str, req: AnalyzeRequest, folder: Path):
    try:
        set_task(task_id, 3, "AraÃ§lar kontrol ediliyor")
        require_binary("ffmpeg"); require_binary("ffprobe")
        video = download_video(str(req.url), folder,
            lambda value, label: set_task(task_id, value, label))
        set_task(task_id, 24, "Video bilgileri okunuyor")
        duration = probe_duration(video)
        set_task(task_id, 30, "Whisper modeli hazÄ±rlanÄ±yor")
        set_task(task_id, 36, "KonuÅŸma Ã§Ã¶zÃ¼mleniyor Â· Whisper")
        segments, language = transcribe(video, req.language,
            lambda value, label: set_task(task_id, value, label), duration)
        set_task(task_id, 70, "KonuÅŸma analizi tamamlandÄ± Â· Shorts adaylarÄ± seÃ§iliyor")
        candidates = make_candidates(segments, duration, req.clips, req.min_seconds, req.max_seconds)
        set_task(task_id, 82, "AI editÃ¶r adaylarÄ± deÄŸerlendiriyor")
        candidates = rank_candidates(candidates)
        for c in candidates:
            c["learning_adjustment"] = learning.adjustment("youtube")
            c["score"] = max(1, min(100, c["score"] + c["learning_adjustment"]))
        candidates = sorted(candidates, key=lambda x:x["score"], reverse=True)[:req.clips]
        if not candidates:
            raise RuntimeError("Yeterli konuÅŸma iÃ§eren kesit bulunamadÄ±. Daha uzun bir video veya farklÄ± sÃ¼re seÃ§in.")
        jobs[task_id] = {"folder": str(folder), "video": str(video), "duration": duration,
                         "language": language, "segments": segments, "clips": candidates}
        result = {"job_id": task_id, "duration": duration, "language": language, "clips": candidates,
                  "ai_mode": "local Ollama (fallback: heuristic)", "platforms": list(PLATFORMS)}
        set_task(task_id, 100, "Analiz tamamlandÄ± Â· Shorts listesi hazÄ±r", "completed", result=result)
    except Exception as exc:
        shutil.rmtree(folder, ignore_errors=True)
        set_task(task_id, 100, "Ä°ÅŸlem baÅŸarÄ±sÄ±z", "failed", error=str(exc))

def run_render_task(task_id: str, req: RenderRequest, job: dict, clip: dict, platforms: list[str]):
    try:
        outputs = []
        total = len(platforms)
        for index, platform in enumerate(platforms):
            label = PLATFORMS[platform]["label"]
            start_percent = 5 + int(index / total * 90)
            set_task(task_id, start_percent, f"{label} Â· Kadraj ve yÃ¼z takibi")
            path = render_variant(job, clip, platform, req.captions, face_tracking=True)
            outputs.append({"platform": platform, "label": label,
                            "file": f"/workspace/{req.job_id}/{path.name}"})
            set_task(task_id, 5 + int((index + 1) / total * 90), f"{label} Â· TamamlandÄ±")
        set_task(task_id, 100, "TÃ¼m platform Ã§Ä±ktÄ±larÄ± hazÄ±r", "completed",
                 result={"outputs": outputs, "message": "DÄ±ÅŸa aktarma tamamlandÄ±."})
    except Exception as exc:
        set_task(task_id, 100, "Render baÅŸarÄ±sÄ±z", "failed", error=f"Render hatasÄ±: {exc}")

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    task_id = uuid.uuid4().hex[:10]
    folder = WORK / task_id
    folder.mkdir(parents=True, exist_ok=True)
    set_task(task_id, 1, "Analiz kuyruÄŸa alÄ±ndÄ±")
    background_tasks.add_task(run_analyze_task, task_id, req, folder)
    return {"task_id": task_id, "status": "queued"}

@app.post("/api/render")
def render(req: RenderRequest, background_tasks: BackgroundTasks):
    job = jobs.get(req.job_id)
    if not job: raise HTTPException(404, "Ä°ÅŸ bulunamadÄ±. Videoyu yeniden analiz edin.")
    clip = next((c for c in job["clips"] if c["id"] == req.clip_id), None)
    if not clip: raise HTTPException(404, "Klip bulunamadÄ±.")
    platforms = list(dict.fromkeys(req.platforms))
    if not platforms or any(p not in PLATFORMS for p in platforms):
        raise HTTPException(400, "GeÃ§ersiz platform seÃ§imi.")
    task_id = uuid.uuid4().hex[:10]
    set_task(task_id, 1, "Render kuyruÄŸa alÄ±ndÄ±")
    background_tasks.add_task(run_render_task, task_id, req, job, clip, platforms)
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    state = task_states.get(task_id)
    if not state:
        raise HTTPException(404, "Ä°ÅŸlem kaydÄ± bulunamadÄ±.")
    return dict(state)

@app.post("/api/metadata")
def metadata(req: MetadataRequest):
    job = jobs.get(req.job_id)
    if not job: raise HTTPException(404, "Ä°ÅŸ bulunamadÄ±.")
    clip = next((c for c in job["clips"] if c["id"] == req.clip_id), None)
    if not clip: raise HTTPException(404, "Klip bulunamadÄ±.")
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
    if not job: raise HTTPException(404, "Ä°ÅŸ bulunamadÄ±.")
    return {"job_id": job_id, "duration": job["duration"], "language": job["language"], "clips": job["clips"]}

@app.get("/")
def home():
    return FileResponse(BASE / "web" / "index.html")

@app.get("/api/learning")
def learning_insights():
    return learning.insights()

@app.post("/api/learning/record")
def record_performance(req: PerformanceRequest):
    if req.platform not in PLATFORMS: raise HTTPException(400,"GeÃ§ersiz platform.")
    return learning.record(req.model_dump())

@app.post("/api/agents/run")
def agents_run(req: TeamRequest):
    job=jobs.get(req.job_id)
    if not job: raise HTTPException(404,"Ä°ÅŸ bulunamadÄ±.")
    clip=next((c for c in job["clips"] if c["id"]==req.clip_id),None)
    if not clip: raise HTTPException(404,"Klip bulunamadÄ±.")
    if any(p not in PLATFORMS for p in req.platforms): raise HTTPException(400,"GeÃ§ersiz platform.")
    return {"agents":run_agent_team(llm_json,job,clip,req.platforms)}
