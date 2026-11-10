# Changelog

All notable project changes are documented here. This file tracks shipped changes separately from roadmap proposals.

## [1.2] — 2026-11-10

### Added
- Local-first video analysis workflow built around FastAPI.
- YouTube source retrieval through yt-dlp.
- Timestamped speech transcription using Faster-Whisper.
- Optional local Ollama model integration for candidate-clip evaluation, with a deterministic/heuristic fallback path.
- FFmpeg-based clip rendering, subtitle processing, and vertical output targets for YouTube Shorts, Instagram Reels, and TikTok.
- OpenCV-assisted face detection and framing helpers.
- Local project/workspace handling and learning/performance observations.
- REST endpoints for health, settings, system metrics, analysis tasks, rendering, metadata, agent utilities, and learning records.
- Browser dashboard for analysis progress, clips, settings, and system status.
- CPU and memory metrics, plus optional NVIDIA GPU/VRAM/temperature telemetry where supported.
- Windows startup script and Python dependency manifest.

### Improved
- Lightweight local model profile and configurable Whisper model/device settings.
- GPU-aware Faster-Whisper initialization with CPU fallback when CUDA is unavailable or initialization fails.
- Better low-resource configuration options for Windows systems.
- Modernized dark dashboard, responsive layout, and clearer task/pipeline states.
- UTF-8/Turkish character handling in the interface and progress messages.
- Local-only defaults and clearer separation between application code and machine-specific settings.

### Documentation
- Bilingual Turkish and English project documentation.
- Architecture, platform integration, and product roadmap documents.
- Product screenshots, workflow and architecture diagrams.
- Clear distinction between implemented v1.2 capabilities and future roadmap targets.

### Known scope limits
- OAuth-based automatic publishing is not part of the verified v1.2 baseline.
- Persistent multi-agent orchestration, production multi-tenancy, centralized cloud infrastructure, and a switchable multilingual UI remain roadmap work.
- GPU telemetry does not imply that every model or FFmpeg operation runs on the GPU.

## [Documentation refresh] — 2026-11-11

### Added
- Expanded feature-map, release-roadmap, and language-support SVG infographics.
- Project author credit, **Ozan Yaman**, integrated into the hero artwork and documentation.
- This changelog with an explicit shipped-vs-planned release policy.

### Improved
- README information architecture, navigation, installation notes, API reference, security guidance, and bilingual coverage.
- Clarified that the default Windows launcher uses port `8765`; a developer may choose another available port for a local session.
- Clarified speech-language selection versus user-interface localization.
- Corrected the screenshot section to reference the actual committed Studio screenshot.

---

## Planned milestones (not released)

The following are roadmap targets, not shipped release entries:

| Target | Planned scope |
|---|---|
| v1.3 | Persistent agent workflow foundation, retries, cancellation, audit events |
| v1.4 | Platform-specific SEO metadata generation and validation |
| v1.5 | Authorized YouTube OAuth, upload/scheduling, available analytics |
| v1.6 | Eligible Instagram and TikTok official API integrations |
| v1.7 | Unified analytics with freshness and metric-availability indicators |
| v1.8 | Learning from measured outcomes, content calendar, approvals and controlled automation |

See [docs/ROADMAP.md](docs/ROADMAP.md) for scope and acceptance criteria.
