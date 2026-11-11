# YAMAN VIRAL STUDIO PRO

Local-first AI video analysis, Shorts production and multi-platform content workflows.

**Professional UI refresh v1.5** adds icon-led navigation, a branded app mark and favicon, GitHub shortcuts, a workspace breadcrumb, refined dark surfaces, keyboard focus states and mobile-first navigation.

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
| ![Desktop dashboard](docs/assets/dashboard-desktop.png) | ![Mobile dashboard](docs/assets/dashboard-mobile.png) |

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


## Licensing

- **Community Edition:** The existing repository source remains under the [MIT License](LICENSE), including the rights granted for commercial use.
- **Enterprise / Commercial:** Separately identified commercial modules require a signed commercial agreement. This does not narrow rights already granted to MIT-licensed code.
- See the [licensing model](LICENSING.md) and the [commercial agreement template](LICENSE-COMMERCIAL-TEMPLATE.md). The template is not an executed license and requires legal review.
