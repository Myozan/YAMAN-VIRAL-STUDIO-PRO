# YAMAN VIRAL STUDIO PRO

Local-first AI video clipping studio. Analyze an authorized YouTube video, transcribe speech with Faster-Whisper, rank candidate highlights with local Ollama, and export captioned vertical MP4 variants for YouTube Shorts, Instagram Reels, and TikTok.

## Features
- Local AI: Ollama (default `qwen3:8b`) and Faster-Whisper
- YouTube URL ingestion via yt-dlp with a YouTube host allowlist
- Highlight extraction and heuristic + LLM ranking
- Word-level karaoke-style ASS captions burned into video
- Three platform-specific exports with distinct caption safe margins
- Platform-specific title, description and hashtag generation
- FastAPI backend and responsive Turkish dashboard

## Requirements
- Windows 10/11 or Linux/macOS; Python 3.10+
- FFmpeg and ffprobe installed and available in PATH
- Ollama installed and running
- Whisper model downloads on first run

## Windows quick start
1. Install Python, FFmpeg, and Ollama.
2. Run `ollama pull qwen3:8b`.
3. Extract this repository and run `run_windows.bat`.
4. Open http://127.0.0.1:8765

Manual:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen3:8b
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

## API
- `GET /api/health`
- `GET /api/platforms`
- `POST /api/analyze` JSON: `{ "url": "https://youtu.be/...", "clips": 8, "min_seconds": 20, "max_seconds": 55, "language": "auto" }`
- `POST /api/render` JSON: `{ "job_id": "...", "clip_id": 1, "platforms": ["youtube","instagram","tiktok"], "captions": true }`
- `POST /api/metadata` JSON: `{ "job_id": "...", "clip_id": 1, "platforms": ["youtube","instagram","tiktok"] }`
- `GET /api/jobs/{job_id}`

## GitHub publishing
Create an empty GitHub repository named `yaman-viral-studio-pro`, then:
```bash
git init
git add .
git commit -m "Initial YAMAN VIRAL STUDIO PRO"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/yaman-viral-studio-pro.git
git push -u origin main
```
Generated media under `workspace/` is excluded by `.gitignore`.

## Known limitations
- Reframing currently uses center crop; face-aware speaker tracking is not implemented.
- Word-level captions rely on Whisper word timestamps; fallback is segment text.
- Jobs live in memory and do not survive a restart. No durable queue, account system, or auto-publishing is included.
- Virality scores are editorial estimates, not predictions or guarantees.
- Platform OAuth publishing requires separate credentials, app review and explicit account authorization.
- Process only content you own or are licensed to download, edit and republish. No DRM or access-control bypass is provided.

## Security
The app binds to localhost. Do not expose it publicly. Before multi-user deployment add authentication, job isolation, quotas, persistent storage, background workers, upload scanning and CSRF protection.

## v1.1 PRO
- OpenCV face-aware crop tracks the largest detected face with smoothed horizontal framing; center framing remains if no face is detected. Designed for one prominent speaker.
- SQLite learning engine records manually entered views, likes, comments, shares and average watch time. Conservative adjustment activates after at least three samples per platform.
- Four agents: video analysis, edit planning, SEO metadata and publishing preparation. Publishing prepares exports only; real uploads require authorized OAuth integrations.
- Endpoints: `GET /api/learning`, `POST /api/learning/record`, `POST /api/agents/run`.

## v1.2 — Application workspaces
- Sidebar navigation now opens Studio, Content Production, Projects, Platform Profiles and Settings pages.
- Projects lists jobs from the current server session (RAM-backed; restart clears this list).
- Platform Profiles shows Shorts/Reels/TikTok export settings and accurately marks OAuth accounts as not connected.
- Settings lets the user select local Ollama model and Whisper model/device; saved to `settings.local.json`.
- Launcher checks FFmpeg and Ollama CLI and attempts to add the standard per-user Ollama install folder to PATH.

### Ollama Windows install troubleshooting
If the PowerShell install script fails, use the official Windows installer download page: https://ollama.com/download/windows. Ollama's Windows installer normally installs per-user without administrator rights. After installation, open a new terminal and verify `ollama --version`, then `ollama pull qwen3:8b`. Logs are under `%LOCALAPPDATA%\Ollama`; binary installation is normally under `%LOCALAPPDATA%\Programs\Ollama`.
