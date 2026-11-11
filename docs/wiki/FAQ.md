# Frequently Asked Questions

## Is YAMAN VIRAL STUDIO PRO fully offline?

No. It is local-first. Ollama and Faster-Whisper can run locally after models are installed, and FFmpeg processes media locally. First-time model/package downloads and optional services such as Edge TTS, Runway, Pexels, trend RSS and platform APIs require network access.

## Where does the app run?

The documented Windows launcher starts FastAPI at http://127.0.0.1:8765.

## Does it require Ollama?

Ollama is optional for the application to start, but local AI analysis and script generation depend on it. Some workflows can use heuristic or transcript-based fallback behavior.

## Does it publish automatically to every platform?

No. Publishing depends on OAuth setup, provider permissions, account eligibility and app review. The publish endpoint requires explicit confirmation. Autopilot scheduling does not mean silent, unconditional social publishing.

## Which platforms are supported?

The current code includes profiles and publishing paths for YouTube, Instagram and TikTok. Provider-side permissions and restrictions still apply.

## Why is the first transcription slow?

Faster-Whisper may download a model and initialize it on first use. CPU/GPU choice, model size and source video duration affect processing time.

## Can I expose the app to the internet?

Do not expose the inspected v1.8.0 application directly. It does not show a general authentication/authorization layer protecting every API route, and workspace files are mounted under /workspace. Add authentication, access controls, HTTPS, private media authorization and operational hardening first.

## Where are the local databases and files?

Runtime files are stored under workspace. See [Database Schema](Database-Schema) for database files and backup requirements.

## How do I report a bug?

Open an issue in the GitHub repository with steps to reproduce, version, Windows/Python versions and sanitized logs. Never include credentials, tokens or private media.
