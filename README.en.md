<div align="center">

# YAMAN VIRAL STUDIO PRO

[TR Turkish](README.md) | [EN English](README.en.md) | [DE German](README.de.md) | [ES Spanish](README.es.md)

**Local-first AI video production studio**

Designed & developed by [Ozan Yaman](https://github.com/Myozan) | Version 1.4.0

</div>

## Overview

YAMAN VIRAL STUDIO PRO is a local-first video workflow for transcription, short-clip selection, AI video summaries and export profiles for YouTube Shorts, Instagram Reels and TikTok. It uses FastAPI, Ollama, Faster-Whisper and FFmpeg.

## Features

- YouTube URL and local Downloads folder ingestion.
- Timestamped Whisper transcripts and TXT export.
- Short/sparse-speech fallback for clip selection.
- AI summary MP4 with selected moments, subtitles, intro and outro.
- Twelve specialist agents with individual structured reports.
- Persistent agent task history, event audit trail, cancellation, retry and restart recovery using SQLite.
- Turkish/English interface language switch.
- OAuth connection and user-approved publishing workflows for YouTube, TikTok and Instagram.
- Encrypted local storage for OAuth app credentials and access tokens.
- Editable platform export profiles and CPU/GPU/RAM/VRAM monitoring.
- CPU card shows only processor model and usage.

## Windows setup

Install Python 3.12, FFmpeg and Ollama. Run ollama pull qwen3:1.7b, start run_windows.bat and open http://127.0.0.1:8765.

## OAuth and publishing setup

Configure provider credentials in the Platform Profiles page. They are encrypted locally.

- Google/YouTube: YAMAN_GOOGLE_CLIENT_ID and YAMAN_GOOGLE_CLIENT_SECRET. Required scope: youtube.upload.
- TikTok: YAMAN_TIKTOK_CLIENT_KEY and YAMAN_TIKTOK_CLIENT_SECRET. Required approved scope: video.publish.
- Meta/Instagram: YAMAN_META_APP_ID and YAMAN_META_APP_SECRET. Required scopes: instagram_basic, instagram_content_publish and pages_show_list.

Register the exact callback URL displayed by the app in each developer console. YouTube uploads default to private. TikTok unaudited apps are restricted to private posts. Instagram Reels requires a professional account linked to a Facebook Page and a publicly accessible HTTPS video URL. Every publish action requires explicit user confirmation.

## Security

OAuth secrets and tokens are encrypted with Fernet and stored outside Git. Back up the local .oauth.key file; without it, the encrypted OAuth vault cannot be decrypted. Never commit client secrets, tokens, or local workspace data.

## License

MIT. See LICENSE.
