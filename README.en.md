# YAMAN VIRAL STUDIO PRO

<div align="center">

<img src="docs/assets/hero-v1.8.0.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 Premium AI Creator Studio" width="100%">

**LOCAL-FIRST AI VIDEO CREATION · WINDOWS · PWA**

[![Version](https://img.shields.io/badge/Version-1.8.0-8b78f6?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-Installable-5B8DEF?style=for-the-badge)](#installation)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

[🇹🇷 Türkçe](README.md) · **🇬🇧 English** · [🇩🇪 Deutsch](README.de.md) · [🇪🇸 Español](README.es.md)

</div>

**Turn one long video into a complete short-form content workflow.**

## ✦ Overview

YAMAN VIRAL STUDIO PRO is a **local-first AI Creator Studio** for turning long-form videos into structured, edited and platform-ready short videos.

Bring in a source video. Transcribe speech with **Whisper**, discover and shape compelling moments with **Ollama**, then cut, caption and render with **FFmpeg**. Prepare vertical outputs for YouTube Shorts, Instagram Reels and TikTok while keeping the core media workflow on your own machine.

> Your footage stays local by default. Your creative workflow stays in control.

## ⚡ Quick start

**Windows 10/11 · Python 3.12 · FFmpeg**

```powershell
git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
cd YAMAN-VIRAL-STUDIO-PRO
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
.\run_windows.bat
```

Open **http://127.0.0.1:8765**. Install [Ollama](https://ollama.com/download/windows) for local content intelligence. Whisper models may be downloaded on first use.

## 🎬 Creator toolkit

| Workflow | What it does |
|---|---|
| **Whisper transcription** | Converts speech into timestamped text for editing and search |
| **Ollama content intelligence** | Analyses source context, drafts scripts and ranks clip candidates |
| **Smart Recap** | Selects key moments and creates a concise recap |
| **Story Flow** | Builds a narrative sequence from opening to closing |
| **Documentary** | Shapes a chronological, evidence-grounded story |
| **Education** | Organises concepts, steps, examples and a learning recap |
| **Product video** | Structures product messaging without inventing unsupported claims |
| **FFmpeg render** | Cuts, captions and exports vertical MP4 video |
| **Autopilot** | Runs scheduled local-first content workflows |
| **Media library** | Organises source videos, clips and rendered deliverables |

## 🔁 One pipeline. Multiple destinations.

<p align="center"><img src="docs/assets/pipeline.svg" alt="Whisper, Ollama and FFmpeg production pipeline" width="100%"></p>
<p align="center"><img src="docs/assets/video-formats.svg" alt="Five editorial video formats" width="100%"></p>

## 🖥️ Inside the studio

**DESKTOP WORKSPACE**

<p align="center"><img src="docs/assets/screenshot-live-desktop-framed.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 desktop workspace" width="100%"></p>

**MOBILE WORKSPACE**

<p align="center"><img src="docs/assets/screenshot-live-mobile-framed.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 mobile workspace" width="52%"></p>

The interface includes a collapsible icon sidebar, mobile navigation drawer, quick theme switching and a workflow-focused Creator Studio home screen.

## 🧩 Architecture

<p align="center"><img src="docs/assets/architecture.svg" alt="YAMAN VIRAL STUDIO PRO architecture" width="100%"></p>

| Layer | Technology |
|---|---|
| API and application | Python 3.12 · FastAPI |
| Web interface | HTML · CSS · JavaScript |
| Local language model | Ollama |
| Speech recognition | Faster-Whisper |
| Video and audio | FFmpeg · optional Auto-Editor |
| Task history | SQLite |
| Installable app shell | Web App Manifest · Service Worker |

## 🔐 Local-first by design

- Core transcription, analysis and media processing can run locally after models and dependencies are installed.
- Optional Runway, Pexels, Edge TTS and trend research require internet access.
- Provider credentials should remain in the local encrypted credential store.
- Publishing actions require user approval.
- Import and publish only media you are authorised to use.

## ♻️ Updates for installed copies

The app can check the configured GitHub update branch and display a **user-approved update prompt** when a newer commit is available. The updater creates a backup before replacing application files and is designed to preserve local workspace data, settings, credentials and media.

Updates are never installed silently. Review release information and confirm before applying an update.

## 📦 Project structure

```text
app/                 FastAPI application, AI and media logic
web/                 Creator Studio interface and PWA assets
docs/                Architecture, integrations and documentation
docs/assets/         Original product artwork and screenshots
tools/               Local maintenance and update utilities
workspace/           Local database, settings and generated media
.github/workflows/   CI workflows
run_windows.bat      Windows launcher
requirements.txt     Python dependencies
```

## 🛠️ Troubleshooting

- **Ollama not detected:** Start the local Ollama service, run `ollama list`, then check Studio → Settings.
- **FFmpeg missing:** Install FFmpeg and FFprobe and add their executable folder to PATH.
- **First run takes longer:** Whisper and Ollama models may need a one-time download.
- **Update check unavailable:** Verify internet access and GitHub API availability; the current installation remains usable if the check fails.

## 📚 Documentation

[Changelog](CHANGELOG.md) · [Architecture](docs/ARCHITECTURE.md) · [Platform integrations](docs/PLATFORM-INTEGRATIONS.md) · [Demo](docs/DEMO.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Licensing](LICENSING.md)

## 🤝 Contributing

Issues, bug reports and pull requests are welcome. Review the [contribution guide](CONTRIBUTING.md) and [security policy](SECURITY.md) first.

## ⚖️ License

Community Edition source files covered by the root [MIT License](LICENSE) are distributed under MIT terms. Third-party dependencies and services remain subject to their own licenses. See [LICENSING.md](LICENSING.md).

<div align="center">

**YAMAN VIRAL STUDIO PRO · v1.8.0**

*Create locally. Edit intelligently. Publish everywhere.*

[Repository](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO) · [Releases](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/releases) · [Issues](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/issues)

</div>
