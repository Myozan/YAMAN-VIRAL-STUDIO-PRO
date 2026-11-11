# Engineering Architecture

This page documents the **verified v1.8.0 runtime**. The broader [Architecture](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/ARCHITECTURE.md) file describes a future-state design.

## Runtime diagram

```mermaid
flowchart TB
  U[Browser / PWA] -->|localhost:8765| API[FastAPI + Uvicorn]
  API --> UI[Static web assets]
  API --> ORCH[In-process orchestration]
  ORCH --> TASK[BackgroundTasks + SQLite task store]
  ORCH --> AGENT[Specialist agents]
  AGENT --> OLLAMA[Ollama local]
  ORCH --> WHISPER[Faster-Whisper]
  ORCH --> FFMPEG[FFmpeg / FFprobe]
  ORCH --> YTDLP[yt-dlp]
  ORCH --> DB[(orchestration.sqlite3)]
  ORCH --> LEARN[(viral_learning.sqlite3)]
  ORCH --> FS[Workspace files and job.json]
  ORCH --> EDGE[Edge TTS / RSS]
  ORCH --> VISUAL[Optional Runway / Pexels]
  API --> SOCIAL[OAuth and social APIs]
```

## Current technology

| Layer | Implementation |
|---|---|
| API | Python 3.12, FastAPI, Uvicorn |
| UI | HTML, CSS, JavaScript, PWA |
| Local LLM | Ollama |
| Speech-to-text | Faster-Whisper |
| Media | FFmpeg / FFprobe, optional Auto-Editor |
| Source retrieval | yt-dlp |
| Persistence | SQLite, JSON, filesystem |
| Agent team | Task-scoped Ollama calls + deterministic validators |

## Task lifecycle

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running
  running --> completed
  running --> failed
  running --> cancelled
  running --> interrupted: app restart
  failed --> queued: retry
  interrupted --> queued: retry
```

The task system is in-process. It is not a distributed worker queue. Existing queued/running tasks are marked interrupted on startup.

## Important security note

The inspected v1.8.0 source does not show a general authentication and authorization layer protecting every API route. The app is intended for local use. Do not expose it to a LAN or public internet without authentication, per-user access control, private media protection, HTTPS, rate limiting and audit logging.

## Full diagrams

See [Engineering Architecture](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/ENGINEERING-ARCHITECTURE.md) and [Workflow Sequences](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/WORKFLOW-SEQUENCES.md).
