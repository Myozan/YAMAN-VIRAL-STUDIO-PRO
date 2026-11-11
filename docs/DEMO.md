# End-to-end production demo

This demo was generated through the YAMAN VIRAL STUDIO PRO local API and local services. The source is a synthetic test asset with a generated voiceover and original graphic, not personal or third-party footage.

## Workflow

1. **Import:** a 47.9-second test video was loaded from the Windows Downloads folder.
2. **Transcription:** Faster-Whisper `tiny` detected English speech and produced a timestamped transcript.
3. **Clip discovery:** the app created 2 short-form clip candidates.
4. **Vertical export:** clip 1 was rendered with the YouTube Shorts profile and captions enabled.
5. **Output validation:** FFprobe confirmed H.264 video, AAC audio, 1080 × 1920 resolution and approximately 40 seconds. Both source and final MP4 were decoded with FFmpeg without reported errors.

## Files

- [Synthetic source video](assets/demo-input.mp4)
- [Actual YouTube Shorts MP4 rendered by the app](assets/demo-output-youtube-shorts.mp4)
- [Frame from the rendered output](assets/demo-render-frame.png)
- [Timestamped subtitles (SRT)](assets/demo-transcript.srt)
- [Transcript (TXT)](assets/demo-transcript.txt)

## Clip candidates

- Clip 1: 0.0–40.0s, score 59/100 — Welcome to YUM IN VIRAL STUDIO PRO. This is a local first video p
- Clip 2: 5.5–45.5s, score 59/100 — This is a local first video production workspace. Start with a lo

## Technical notes

- Local health check: FastAPI, FFmpeg and Ollama were reachable.
- Speech model: `tiny` on CPU.
- Installed Ollama model: `qwen3:1.7b`. The app's analysis response does not expose a separate success flag for LLM ranking versus its heuristic fallback, so the displayed candidate scores should not be represented as a verified LLM-only judgment.
- Subtitle overflow was fixed by changing ASS `WrapStyle` from 2 (no wrapping) to 0 (smart wrapping); the final MP4 was re-rendered after the fix.
- No social account was connected and nothing was published. Publishing requires OAuth configuration and explicit user approval.
