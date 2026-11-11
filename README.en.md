<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO — Local AI Video Studio" width="100%">

# YAMAN VIRAL STUDIO PRO

### Local-first AI video analysis, Shorts creation and multi-platform content workflow

[🇹🇷 Türkçe](README.md) · [🇬🇧 English](README.en.md) · [🇩🇪 Deutsch](README.de.md) · [🇪🇸 Español](README.es.md)

[![Version](https://img.shields.io/badge/version-1.4.1-6478ff?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Local AI](https://img.shields.io/badge/AI-Local--First-8B5CF6?style=for-the-badge)](#architecture)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

**Designed and developed by [Ozan Yaman](https://github.com/Myozan)**

</div>

---

## ✨ Overview

YAMAN VIRAL STUDIO PRO is a local-first AI video studio that analyzes long-form videos, transcribes speech with timestamps, identifies strong moments and prepares short-form content for YouTube Shorts, Instagram Reels and TikTok.

Its Ollama, Faster-Whisper and FFmpeg workflow is designed to keep content processing on the user's own computer wherever possible.

## 🖥️ Application screenshots

| Desktop workspace | Responsive mobile view |
|:---:|:---:|
| <img src="docs/assets/dashboard-desktop.png" alt="Desktop application screen" width="100%"> | <img src="docs/assets/dashboard-mobile.png" alt="Mobile application screen" width="72%"> |

## 🚀 Key capabilities

<img src="docs/assets/feature-map.svg" alt="Product feature map" width="100%">

- **Video ingestion:** YouTube URL or local Windows Downloads folder.
- **Smart transcription:** Timestamped Faster-Whisper transcript and TXT export.
- **AI clip selection:** Candidate moments based on hooks, context, speech density and watchability signals.
- **AI summary video:** Vertical MP4 combining key moments, subtitles, intro and outro.
- **12 specialist AI agents:** Strategy, hooks, editing, SEO, risk review, accessibility, localization and publishing preparation.
- **Task orchestration:** SQLite task history, event log, cancellation, retry and recovery after restart.
- **Multilingual interface:** Turkish, English, German and Spanish; language preference is managed in Settings.
- **Platform workflows:** OAuth connection and user-approved publishing preparation for YouTube, TikTok and Instagram.
- **System monitoring:** GPU, CPU, RAM and VRAM usage.
- **Responsive UI:** Adaptive desktop and mobile layouts.

## 🔄 Content workflow

<img src="docs/assets/pipeline.svg" alt="Video production workflow" width="100%">

1. Import a source video.
2. Transcribe speech with Whisper.
3. Identify strong moments and clips with local AI.
4. Apply vertical framing, subtitles and platform profiles.
5. Review the MP4 output and prepare it for the selected platform.

## 🧩 Architecture

<img src="docs/assets/architecture.svg" alt="Application architecture" width="100%">

| Layer | Technology |
|---|---|
| API and task management | Python 3.12 · FastAPI · Uvicorn |
| Local language model | Ollama · Qwen |
| Speech recognition | Faster-Whisper |
| Video processing | FFmpeg · FFprobe · yt-dlp |
| Web interface | HTML · CSS · JavaScript |
| Persistent task history | SQLite |
| OAuth secrets | Local Fernet encryption |

## ⚙️ Windows installation

**Requirements:** Windows 10/11, Python 3.12, FFmpeg and Ollama.

1. Clone the repository: **git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git**
2. Open the project folder.
3. Download the local model: **ollama pull qwen3:1.7b**
4. Run **run_windows.bat**.
5. Open **http://127.0.0.1:8765** in your browser.

For a manual setup, create a Python virtual environment and run **pip install -r requirements.txt**.

## 🌐 Language and appearance settings

Open **Settings → Language & localization** in the application and choose Türkçe, English, Deutsch or Español. Your preference is stored in the browser and restored on your next visit. The appearance theme can be changed separately to Dark, Light or Ocean.

## 🔐 OAuth and publishing

Configure provider developer credentials in Platform Profiles. Application credentials and tokens are encrypted locally.

| Platform | Configuration | Scope |
|---|---|---|
| YouTube | YAMAN_GOOGLE_CLIENT_ID / YAMAN_GOOGLE_CLIENT_SECRET | youtube.upload |
| TikTok | YAMAN_TIKTOK_CLIENT_KEY / YAMAN_TIKTOK_CLIENT_SECRET | video.publish |
| Instagram | YAMAN_META_APP_ID / YAMAN_META_APP_SECRET | instagram_basic, instagram_content_publish, pages_show_list |

Register the exact OAuth callback URL in each developer console. Every publishing action requires user confirmation. YouTube uploads default to private; TikTok app review and Instagram's public HTTPS media URL requirements depend on platform policies.

## 🛡️ Security and privacy

- AI and video processing are designed to use local services.
- OAuth secrets and access tokens are encrypted with Fernet.
- Never commit .oauth.key, the token vault, settings.local.json or workspace data.
- Back up .oauth.key securely; losing it makes the encrypted token vault unreadable.
- Import only content you own or are authorized to use and republish.

## 🗂️ Project structure

- **app/** — FastAPI application and AI/video logic
- **web/** — Web interface, styles and client code
- **docs/** — Architecture, integrations and visual documentation
- **workspace/** — Local generated files (excluded from Git)
- **run_windows.bat** — Windows launcher
- **requirements.txt** — Python dependencies

## 🧭 Roadmap

<img src="docs/assets/roadmap.svg" alt="Product roadmap" width="100%">

## 📚 Technical documentation

- [AI agents and OAuth research](docs/AI-AGENTS-RESEARCH.md)
- [Architecture notes](docs/ARCHITECTURE.md)
- [Platform integrations](docs/PLATFORM-INTEGRATIONS.md)
- [Changelog](CHANGELOG.md)

## 📄 License

MIT — see [LICENSE](LICENSE).

<div align="center">

**YAMAN VIRAL STUDIO PRO** · Built with focus by [Ozan Yaman](https://github.com/Myozan)

</div>
