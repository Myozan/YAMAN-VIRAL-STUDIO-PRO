# YAMAN VIRAL STUDIO PRO

Local-first **AI video repurposing studio** for video analysis, speech transcription, highlight discovery and vertical clip production for YouTube Shorts, Instagram Reels and TikTok.

<p align="center"><img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO local AI video studio" width="100%"></p>

<p align="center"><a href="https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/actions/workflows/ci.yml"><img src="https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/actions/workflows/ci.yml/badge.svg?branch=import%2Fv1.2-source" alt="CI status"></a> <img src="https://img.shields.io/badge/AI-Local--First-7C5CFA" alt="Local-first AI"> <img src="https://img.shields.io/badge/PWA-Installable-5B8DEF" alt="PWA"> <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2ea44f.svg" alt="MIT"></a></p>

<p align="center"><a href="README.md">Türkçe</a> · <b>English</b> · <a href="README.de.md">Deutsch</a> · <a href="README.es.md">Español</a></p>

**Search terms:** AI video editor, video repurposing, YouTube Shorts generator, local LLM, Ollama, Faster-Whisper, FFmpeg, Reels, TikTok.

**v1.5.2 · PWA + responsive UI.** Desktop and mobile workspace previews are included below. The SVG previews are illustrative design assets, not live application screenshots.

## Core capabilities
- Import eligible YouTube sources or local videos from Windows Downloads.
- Transcribe speech with Faster-Whisper and export timestamped transcripts.
- Identify candidate short clips with local AI analysis.
- Render vertical videos with captions for Shorts, Reels and TikTok.
- Coordinate specialist AI agents and persistent task history.
- Configure local Ollama and Whisper models.
- Track GPU, CPU, RAM and VRAM telemetry.

## Screenshots
| Desktop | Mobile |
|---|---|
| ![Desktop dashboard](docs/assets/dashboard-desktop.svg) | ![Mobile dashboard](docs/assets/dashboard-mobile.svg) |

## PWA installation

Install from a supported Chromium browser over HTTPS or localhost. On iOS, use Safari → Share → Add to Home Screen. Offline caching covers the app shell only; AI, video processing, uploads and API features still require the local backend. The Windows launcher binds to `127.0.0.1` by default and is not exposed to the LAN.

## Windows setup
Requirements: Windows 10/11, Python 3.12, FFmpeg and Ollama.

```powershell
git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
cd YAMAN-VIRAL-STUDIO-PRO
ollama pull qwen3:1.7b
run_windows.bat
```

Open http://127.0.0.1:8765. See the [Turkish documentation](README.md), [architecture](docs/ARCHITECTURE.md), [platform integrations](docs/PLATFORM-INTEGRATIONS.md) and [changelog](CHANGELOG.md).

Only use and republish media you have rights to use. OAuth publication requires platform approval and explicit user confirmation.


## Contributing and security

- [Contribution guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Report a bug](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/issues/new?template=bug_report.yml)
- [Request a feature](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/issues/new?template=feature_request.yml)

## Licensing

- **Community Edition:** The existing repository source remains under the [MIT License](LICENSE), including the rights granted for commercial use.
- **Enterprise / Commercial:** Separately identified commercial modules require a signed commercial agreement. This does not narrow rights already granted to MIT-licensed code.
- See the [licensing model](LICENSING.md) and the [commercial agreement template](LICENSE-COMMERCIAL-TEMPLATE.md). The template is not an executed license and requires legal review.
