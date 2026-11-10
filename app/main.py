from __future__ import annotations
import ctypes, json, os, platform, re, shutil, subprocess, sys, time, uuid
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
from app.agents import AGENT_CATALOG, run_agent_team
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
app = FastAPI(title="YAMAN VIRAL STUDIO PRO", version="1.3.0")
app.mount("/assets", StaticFiles(directory=BASE / "web"), name="assets")
app.mount("/workspace", StaticFiles(directory=WORK), name="workspace")
jobs: dict[str, dict[str, Any]] = {}
task_states: dict[str, dict[str, Any]] = {}
_cpu_sample = None
learning = ViralLearningEngine(WORK / "viral_learning.sqlite3")


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
    host = (urlparse(url).hostname or "").lower()
    allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtube-nocookie.com"}
    if host not in allowed:
        raise ValueError("Güvenlik nedeniyle yalnızca youtube.com veya youtu.be bağlantıları kabul edilir.")

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

def probe_duration(path: Path) -> float:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    if p.returncode:
        raise RuntimeError("Video bilgisi okunamadı: " + p.stderr[-1000:])
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
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json", "think": False, "keep_alive": 0, "options": {"num_predict": num_predict}},
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
    return out

def fallback_metadata(clip: dict, platform: str):
    title = re.sub(r"\s+", " ", clip.get("title", "İzlemeden geçme!")).strip()[:95]
    tags = ["#shorts", "#reels", "#tiktok", "#keşfet", "#viral"]
    return {"title": title, "description": clip["text"][:400] + "\n\n" + " ".join(tags),
            "hashtags": tags, "platform": platform}

_cpu_hardware_cache = {"at": 0, "data": {}}

def cpu_hardware_info():
    """Read CPU identity and hardware-monitor temperature sensors."""
    global _cpu_hardware_cache
    now = time.time()
    if now - _cpu_hardware_cache["at"] < 10:
        return dict(_cpu_hardware_cache["data"])
    info = {"cpu_temp_c": None, "cpu_temp_source": "Sensor provider not detected",
            "cpu_name": platform.processor() or "CPU", "cpu_cores": os.cpu_count() or 1,
            "cpu_threads": os.cpu_count() or 1, "cpu_clock_mhz": None}
    ps = "$cpu=Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors,CurrentClockSpeed; $s=@(); foreach($ns in @('root/LibreHardwareMonitor','root/OpenHardwareMonitor')) { try {$s=@(Get-CimInstance -Namespace $ns -ClassName Sensor -ErrorAction Stop | Where-Object {$_.SensorType -eq 'Temperature' -and $_.Name -match 'CPU Package|CPU Core|Tctl|CPU Die|CPU CCD'}); if($s.Count -gt 0){break} } catch {} }; $t=$null; if($s.Count -gt 0){$t=($s | Sort-Object Value -Descending | Select-Object -First 1).Value}; [PSCustomObject]@{name=$cpu.Name;cores=$cpu.NumberOfCores;threads=$cpu.NumberOfLogicalProcessors;clock=$cpu.CurrentClockSpeed;temp=$t;source=$(if($s.Count -gt 0){'Hardware Monitor'}else{'Sensor provider not detected'})} | ConvertTo-Json -Compress"
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            capture_output=True, text=True, timeout=4,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if proc.returncode == 0 and proc.stdout.strip():
            hw = json.loads(proc.stdout.strip().splitlines()[-1])
            info.update({"cpu_name": hw.get("name") or info["cpu_name"],
                "cpu_cores": hw.get("cores") or info["cpu_cores"],
                "cpu_threads": hw.get("threads") or info["cpu_threads"],
                "cpu_clock_mhz": hw.get("clock"), "cpu_temp_c": hw.get("temp"),
                "cpu_temp_source": hw.get("source") or info["cpu_temp_source"]})
    except Exception:
        pass
    _cpu_hardware_cache = {"at": now, "data": info}
    return dict(info)

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
            path = folder / "summary_video.mp4"
            if path.is_file():
                try:
                    stat = path.stat()
                    items.append({"job_id": folder.name, "clip_id": "summary", "platform": "summary",
                                  "label": "\u0041k\u0131ll\u0131 Video \u00d6zeti", "filename": path.name,
                                  "file": f"/workspace/{folder.name}/{path.name}",
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
            "local_only": True}

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
    state = task_states.setdefault(task_id, {})
    state.update({"task_id": task_id, "percent": max(0, min(100, int(percent))),
                  "stage": stage, "status": status, **extra})

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
        seg = min(usable, key=lambda x: abs((float(x.get("start", 0)) + float(x.get("end", 0))) / 2 - target))
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


def build_summary_moments(job: dict, target_seconds: int) -> dict:
    segments = job.get("segments", [])
    duration = float(job.get("duration", 0))
    transcript = "\n".join(
        f"{float(x.get('start', 0)):.1f}-{float(x.get('end', 0)):.1f}s: {str(x.get('text', '')).strip()}"
        for x in segments if str(x.get("text", "")).strip()
    )
    # Keep the prompt compact enough for small local models; retain timeline coverage.
    if len(transcript) > 8500:
        lines = transcript.splitlines()
        stride = max(1, len(lines) // 90)
        transcript = "\n".join(lines[::stride])[:8500]
    fallback = fallback_summary_moments(segments, duration, target_seconds)
    data = {}
    try:
        prompt = (
            "You are a concise video editor and summarizer. Answer in Turkish. "
            "Use only the timestamped transcript; do not invent facts. "
            "Summarize the main idea and 3-5 key points. Use source timestamps in seconds. "
            "Choose up to 5 moments, each 6-22 seconds, in chronological order, preserving context. "
            f"Keep total selected duration close to {target_seconds} seconds without exceeding it. "
            "Return valid JSON only with this schema: "
            "{\"title\":\"...\",\"summary\":\"...\",\"key_points\":[\"...\"],"
            "\"intro\":\"...\",\"outro\":\"...\",\"moments\":[{\"start\":1,\"end\":12,\"reason\":\"...\"}]}. "
            "Transcript:\n" + transcript
        )
        data = llm_json(prompt, timeout=180, num_predict=768)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    moments = []
    raw = data.get("moments", []) if isinstance(data, dict) else []
    for item in raw[:8] if isinstance(raw, list) else []:
        try:
            start = max(0.0, float(item.get("start", 0)))
            end = min(duration, float(item.get("end", 0)))
            if end <= start:
                continue
            end = min(end, start + 22)
            if end - start < 4 or any(abs(start - old["start"]) < 4 for old in moments):
                continue
            moments.append({"start": round(start, 2), "end": round(end, 2),
                            "reason": str(item.get("reason", "\u00d6nemli i\u00e7erik b\u00f6l\u00fcm\u00fc"))[:200]})
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
    selected_duration = sum(x["end"] - x["start"] for x in selected)
    if selected_duration < target_seconds * 0.65:
        for extra in fallback:
            if selected_duration >= target_seconds:
                break
            if any(abs(extra["start"] - item["start"]) < 10 for item in selected):
                continue
            length = min(extra["end"] - extra["start"], target_seconds - selected_duration)
            if length >= 4:
                selected.append({"start": extra["start"], "end": round(extra["start"] + length, 2),
                                 "reason": extra.get("reason", "Important speech moment")})
                selected_duration += length
        selected.sort(key=lambda x: x["start"])
    if not selected:
        selected = fallback
    title = str(data.get("title") or "Videonun k\u0131sa \u00f6zeti")[:100]
    summary = str(data.get("summary") or "Video i\u00e7indeki \u00f6nemli konu\u015fma b\u00f6l\u00fcmleri se\u00e7ilerek k\u0131sa bir \u00f6zet ak\u0131\u015f\u0131 olu\u015fturuldu.")[:1500]
    key_points = data.get("key_points")
    if not isinstance(key_points, list) or not key_points:
        key_points = [str(x.get("reason", "\u00d6nemli b\u00f6l\u00fcm")) for x in selected[:5]]
    return {"title": title, "summary": summary, "key_points": [str(x)[:220] for x in key_points[:6]],
            "intro": str(data.get("intro") or title)[:150],
            "outro": str(data.get("outro") or "\u0130zledi\u011fin i\u00e7in te\u015fekk\u00fcrler.")[:150],
            "moments": selected, "method": "local Ollama" if data else "transcript fallback"}


def render_summary_video(job: dict, summary: dict, task_id: str) -> Path:
    """Render selected moments as one portrait MP4 with timed captions and intro/outro."""
    require_binary("ffmpeg")
    folder, source = Path(job["folder"]), Path(job["video"])
    if not source.is_file():
        raise RuntimeError("\u00d6zet video kaynak dosyas\u0131 bulunamad\u0131.")
    moments, parts, mapped = summary["moments"], [], []
    timeline = 0.0
    for index, moment in enumerate(moments, 1):
        start, length = float(moment["start"]), float(moment["end"]) - float(moment["start"])
        if length < 3:
            continue
        part = folder / f"summary_part_{index:02d}.mp4"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(start), "-i", str(source),
               "-t", str(length), "-map", "0:v:0", "-map", "0:a?",
               "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30",
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
    concat_file, joined = folder / "summary_concat.txt", folder / "summary_joined.mp4"
    concat_file.write_text("".join(f"file '{x.name}'\n" for x in parts), encoding="utf-8")
    command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
             "-safe", "0", "-i", str(concat_file), "-c", "copy", "-movflags", "+faststart", str(joined)])
    ass = folder / "summary_video.ass"
    create_ass(mapped, {"start": 0.0, "end": timeline, "duration": timeline}, ass, 280)
    with ass.open("a", encoding="utf-8") as handle:
        handle.write(f"Dialogue: 1,0:00:00.00,{ass_time(min(4.0,timeline))},Viral,,0,0,300,,{{\\an8\\fs76\\bord5}}{ass_escape(summary['title'])}\n")
        if timeline > 5:
            handle.write(f"Dialogue: 1,{ass_time(max(0,timeline-4))},{ass_time(timeline)},Viral,,0,0,300,,{{\\an8\\fs64\\bord5}}{ass_escape(summary['outro'])}\n")
    output = folder / "summary_video.mp4"
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


def run_summary_task(task_id: str, job_id: str, job: dict, target_seconds: int):
    try:
        set_task(task_id, 5, "Video ozeti hazirlaniyor - Yerel AI")
        summary = build_summary_moments(job, target_seconds)
        set_task(task_id, 38, "Onemli anlar secildi - Ozet videosu hazirlaniyor",
                 summary=summary, total_moments=len(summary["moments"]))
        output = render_summary_video(job, summary, task_id)
        summary["output"] = {"file": f"/workspace/{job_id}/{output.name}", "filename": output.name,
                             "size_mb": round(output.stat().st_size/(1024*1024),2),
                             "duration_seconds": round(sum(float(x["end"])-float(x["start"]) for x in summary["moments"]),1)}
        (Path(job["folder"])/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
        set_task(task_id,100,"Akilli ozet videosu hazir","completed",result=summary)
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
    background_tasks.add_task(run_summary_task, task_id, req.job_id, job, req.target_seconds)
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

@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
    state = task_states.get(task_id)
    if not state:
        raise HTTPException(404, "İşlem kaydı bulunamadı.")
    return dict(state)

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

def run_agents_task(task_id: str, req: TeamRequest, job: dict, clip: dict, platforms: list[str]):
    """Run the specialist team in a background task and persist its report."""
    try:
        agent_names = {item["id"]: item["name"] for item in AGENT_CATALOG}
        agent_states = {}
        def on_agent_progress(agent_id, status):
            agent_states[agent_id] = status
            done = sum(value == "completed" for value in agent_states.values())
            name = agent_names.get(agent_id, agent_id)
            total_agents = len(AGENT_CATALOG)
            percent = min(95, 2 + int(done / total_agents * 93))
            stage = name + " \\u00b7 " + ("Tamamland\\u0131" if status == "completed" else "\\u00c7al\\u0131\\u015f\\u0131yor")
            set_task(task_id, percent, stage, agent_statuses=dict(agent_states),
                     current_agent=agent_id, completed_agents=done, total_agents=len(AGENT_CATALOG))
        set_task(task_id, 2, "12 uzman ajan ba\u015flat\u0131l\u0131yor", agent_statuses={})
        report = run_agent_team(llm_json, job, clip, platforms, progress_callback=on_agent_progress)
        report["job_id"] = req.job_id
        report["task_id"] = task_id
        report_path = Path(job["folder"]) / f"agents_clip_{req.clip_id}.json"
        temp_path = report_path.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(report_path)
        summary = report.get("summary", {})
        stage = "Ajan raporlar\\u0131 haz\\u0131r \\u00b7 {} ba\\u015far\\u0131l\\u0131 \\u00b7 {} yedek \\u00b7 {} hata".format(summary.get("completed", 0), summary.get("fallback", 0), summary.get("failed", 0))
        set_task(task_id, 100, stage, "completed", result=report)
    except Exception as exc:
        set_task(task_id, 100, "Ajan ekibi ba\u015far\u0131s\u0131z", "failed", error=str(exc)[:500])


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
    set_task(task_id, 1, "Ajan ekibi kuyru\u011fa al\u0131nd\u0131", outputs=[])
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
