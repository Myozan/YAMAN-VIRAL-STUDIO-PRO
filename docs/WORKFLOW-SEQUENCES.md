# Workflow Sequences — v1.8.0

## 1. Source video analysis

```mermaid
sequenceDiagram
  autonumber
  actor User
  participant UI as Browser UI
  participant API as FastAPI
  participant Task as Task Store
  participant DL as yt-dlp / Local file
  participant STT as Faster-Whisper
  participant LLM as Ollama
  participant FS as Workspace
  User->>UI: Select source and clip constraints
  UI->>API: POST /api/analyze or /api/analyze/local
  API->>API: Validate request model
  API->>Task: Create queued task
  API-->>UI: task_id
  API->>DL: Retrieve source or resolve local video
  DL-->>API: Local media path
  API->>STT: Transcribe with timestamps
  STT-->>API: Segments + detected language
  API->>LLM: Analyze transcript / rank moments
  LLM-->>API: Candidate moments (fallback may apply)
  API->>FS: Persist job.json and media metadata
  API->>Task: Complete task + events
  UI->>API: Poll task/job endpoints
  API-->>UI: Status, clips and transcript
```

## 2. Clip render

```mermaid
sequenceDiagram
  autonumber
  actor User
  participant UI as Browser
  participant API as FastAPI
  participant Task as SQLite task store
  participant FF as FFmpeg
  participant FS as Workspace
  User->>UI: Select clip, platforms and captions
  UI->>API: POST /api/render
  API->>Task: Create render task
  API-->>UI: task_id
  API->>FF: Probe, crop, encode and subtitle
  FF-->>API: Render result / process error
  API->>FS: Save platform output
  API->>Task: Persist status and task events
  UI->>API: GET task status / events
  API-->>UI: Render progress and result
```

## 3. AI agent report

```mermaid
sequenceDiagram
  actor User
  participant API as FastAPI
  participant Team as run_agent_team
  participant LLM as Ollama JSON function
  participant Rules as Deterministic QA
  API->>Team: job + clip + selected platforms
  Team->>LLM: Viral, hook, editor, SEO, claim and audience tasks
  LLM-->>Team: JSON result or fallback
  Team->>Rules: Caption, clip and publishing checks
  Rules-->>Team: Deterministic check report
  Team->>LLM: Thumbnail, localization and accessibility tasks
  LLM-->>Team: JSON result or fallback
  Team-->>API: UI-ready report with per-agent status
  API-->>User: Agent report
```

The agent sequence is a logical overview. Individual agent calls are sequential in the current implementation, not a parallel graph. Model failures may produce fallback status.

## 4. Autopilot scheduling

```mermaid
sequenceDiagram
  participant Scheduler as In-process scheduler
  participant Store as autopilot.py
  participant DB as SQLite
  participant Runner as Autopilot cycle
  participant Pipeline as Content / task pipeline
  Scheduler->>Store: claim_due()
  Store->>DB: BEGIN IMMEDIATE
  Store->>DB: Read enabled plans
  Store->>DB: Advance next_run and mark running
  Store->>DB: COMMIT
  Store-->>Scheduler: Claimed plans
  Scheduler->>Runner: Execute plan
  Runner->>Pipeline: Create content task
  Pipeline-->>Runner: Task/job/output references
  Runner->>Store: finish_run()
  Store->>DB: Insert autopilot_runs + update plan status
```

Autopilot schedules content production. It does not grant unattended social publishing permission. Publishing is a separate operation.

## 5. OAuth and publication approval boundary

```mermaid
sequenceDiagram
  actor User
  participant UI as Browser
  participant API as FastAPI
  participant Provider as OAuth / Platform API
  participant Vault as Encrypted local vault
  User->>UI: Connect account
  UI->>API: GET /api/oauth/start/{platform}
  API->>Provider: Redirect to authorization
  Provider-->>API: OAuth callback code + state
  API->>API: Validate state / PKCE where supported
  API->>Provider: Exchange code for token
  API->>Vault: Encrypt and persist credentials
  User->>UI: Review post and confirm publishing
  UI->>API: POST /api/publish/{platform}
  API->>API: Require confirm_publish and validate request
  API->>Provider: Upload / publish using provider API
  Provider-->>API: Provider response
  API-->>UI: Publish result
```

OAuth app approval, scopes, account eligibility, quota and platform policy can limit publication. No diagram implies that provider app review has already been granted.
