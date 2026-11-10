from __future__ import annotations
import json, os, re, shutil, subprocess, uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl
from app.learning import ViralLearningEngine
from app.agents import run_agent_team
from app.framing import render_face_tracked
from faster_whisper import WhisperModel

BASE = Path(__file__).resolve().parent.parent
WORK = BASE / "workspace"
WORK.mkdir(exist_ok=True)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "auto")
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
        raise RuntimeError(f"{name} bulunamadı. Kurup PATH'e ekleyin.")

def get_whisper():
    global _whisper
    if _whisper is None:
        _whisper = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8")
    return _whisper

def validate_youtube_url(url: str):
    host = (urlparse(url).hostname or "").lower()
    allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtube-nocookie.com"}
    if host not in allowed:
        raise ValueError("Güvenlik nedeniyle yalnızca youtube.com veya youtu.be bağlantıları kabul edilir.")

def download_video(url: str, folder: Path) -> Path:
    validate_youtube_url(url)
    opts = {
        "outtmpl": str(folder / "source.%(ext)s"),
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4", "noplaylist": True, "quiet": True,
        "no_warnings": True, "restrictfilenames": True,
        "max_filesize": MAX_DOWNLOAD_MB * 1024 * 1024,
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

def transcribe(path: Path, language: str):
    model = get_whisper()
    lang = None if language == "auto" else language
    segments, info = model.transcribe(str(path), language=lang, word_timestamps=True, vad_filter=True)
    result = []
    for seg in segments:
        words = []
        if seg.words:
            for w in seg.words:
                words.append({"start": float(w.start), "end": float(w.end), "text": w.word.strip()})
        result.append({"start": float(seg.start), "end": float(seg.end), "text": seg.text.strip(), "words": words})
    return result, info.language

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

def llm_json(prompt: str, timeout: int = 180):
    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
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
    candidates, seen = [], set()
    for i, seg in enumerate(segments):
        start = max(0.0, seg["start"] - 1.0)
        target = start + max_s
        chunk = [s for s in segments[i:] if s["start"] < target and s["end"] > start]
        if not chunk: continue
        end = min(duration, max(s["end"] for s in chunk) + 0.8)
        if end - start < min_s: continue
        text = " ".join(s["text"] for s in chunk).strip()
        if len(text.split()) < 25: continue
        key = round(start / 9)
        if key in seen: continue
        seen.add(key)
        score, reasons = heuristic_score(text)
        candidates.append({
            "id": len(candidates)+1, "start": round(start, 2), "end": round(end, 2),
            "duration": round(end-start, 1), "text": text, "score": score,
            "hook": text[:100], "title": text[:65], "reason": ", ".join(reasons)
        })
    return candidates[:max(count*5, count)]

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
    title = re.sub(r"\s+", " ", clip.get("title", "İzlemeden geçme!")).strip()[:95]
    tags = ["#shorts", "#reels", "#tiktok", "#keşfet", "#viral"]
    return {"title": title, "description": clip["text"][:400] + "\n\n" + " ".join(tags),
            "hashtags": tags, "platform": platform}

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
        raise HTTPException(400, "Geçersiz Ollama model adı.")
    OLLAMA_MODEL = req.ollama_model
    WHISPER_MODEL = req.whisper_model
    WHISPER_DEVICE = req.whisper_device
    _whisper = None
    config_path = BASE / "settings.local.json"
    config_path.write_text(json.dumps(req.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return {"saved": True, "settings": req.model_dump()}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    job_id = uuid.uuid4().hex[:10]
    folder = WORK / job_id
    folder.mkdir(parents=True)
    try:
        require_binary("ffmpeg"); require_binary("ffprobe")
        video = download_video(str(req.url), folder)
        duration = probe_duration(video)
        segments, language = transcribe(video, req.language)
        candidates = make_candidates(segments, duration, req.clips, req.min_seconds, req.max_seconds)
        candidates = rank_candidates(candidates)
        for c in candidates:
            c["learning_adjustment"] = learning.adjustment("youtube")
            c["score"] = max(1, min(100, c["score"] + c["learning_adjustment"]))
        candidates = sorted(candidates, key=lambda x:x["score"], reverse=True)[:req.clips]
        if not candidates:
            raise RuntimeError("Yeterli konuşma içeren kesit bulunamadı. Daha uzun bir video veya farklı süre seçin.")
        jobs[job_id] = {"folder": str(folder), "video": str(video), "duration": duration,
                        "language": language, "segments": segments, "clips": candidates}
        return {"job_id": job_id, "duration": duration, "language": language, "clips": candidates,
                "ai_mode": "local Ollama (fallback: heuristic)", "platforms": list(PLATFORMS)}
    except Exception as e:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(500, str(e))

@app.post("/api/render")
def render(req: RenderRequest):
    job = jobs.get(req.job_id)
    if not job: raise HTTPException(404, "İş bulunamadı. Videoyu yeniden analiz edin.")
    clip = next((c for c in job["clips"] if c["id"] == req.clip_id), None)
    if not clip: raise HTTPException(404, "Klip bulunamadı.")
    platforms = list(dict.fromkeys(req.platforms))
    if not platforms or any(p not in PLATFORMS for p in platforms):
        raise HTTPException(400, "Geçersiz platform seçimi.")
    try:
        outputs = []
        for platform in platforms:
            path = render_variant(job, clip, platform, req.captions, face_tracking=True)
            outputs.append({"platform": platform, "label": PLATFORMS[platform]["label"],
                            "file": f"/workspace/{req.job_id}/{path.name}"})
        return {"outputs": outputs, "message": "Dışa aktarma tamamlandı."}
    except Exception as e:
        raise HTTPException(500, f"Render hatası: {e}")

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

@app.post("/api/agents/run")
def agents_run(req: TeamRequest):
    job=jobs.get(req.job_id)
    if not job: raise HTTPException(404,"İş bulunamadı.")
    clip=next((c for c in job["clips"] if c["id"]==req.clip_id),None)
    if not clip: raise HTTPException(404,"Klip bulunamadı.")
    if any(p not in PLATFORMS for p in req.platforms): raise HTTPException(400,"Geçersiz platform.")
    return {"agents":run_agent_team(llm_json,job,clip,req.platforms)}
