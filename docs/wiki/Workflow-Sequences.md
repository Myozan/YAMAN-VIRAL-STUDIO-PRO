# Workflow Sequence Diagrams

## Video analysis and rendering

```mermaid
sequenceDiagram
  actor Creator
  participant UI as Browser
  participant API as FastAPI
  participant DB as SQLite task store
  participant AI as Ollama / Whisper
  participant FF as FFmpeg
  participant FS as Workspace
  Creator->>UI: Select source video
  UI->>API: POST /api/analyze
  API->>DB: Create task
  API-->>UI: task_id
  API->>AI: Transcribe and analyze
  AI-->>API: Transcript and clip candidates
  API->>FS: Save job.json and source metadata
  API->>DB: Update task and events
  Creator->>UI: Request clip render
  UI->>API: POST /api/render
  API->>FF: Crop, subtitle and encode
  FF-->>API: MP4 output
  API->>FS: Save rendered asset
  API->>DB: Complete task
```

## Agent team

The specialist agents are currently executed sequentially. AI agents call Ollama; rule-based agents perform deterministic checks. A model error may yield a fallback result. Agent output is advisory, not publication approval.

## Autopilot

```mermaid
sequenceDiagram
  participant Scheduler
  participant Store as autopilot.py
  participant DB as SQLite
  participant Runner as Autopilot cycle
  Scheduler->>Store: claim_due()
  Store->>DB: BEGIN IMMEDIATE
  Store->>DB: Claim enabled due plans
  Store->>DB: Advance next_run
  Store-->>Scheduler: Claimed plans
  Scheduler->>Runner: Execute production plan
  Runner->>Store: finish_run()
  Store->>DB: Save run result and plan status
```

Autopilot schedules production, not unconditional social publishing.

## OAuth publishing boundary

Account connection, token exchange and upload require provider API permissions and account eligibility. Publishing requires an explicit confirmation flag. Provider app review and quotas remain external dependencies.

Full sequence documentation: [Workflow Sequences](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/blob/import/v1.8.0-premium-ai-creator-studio/docs/WORKFLOW-SEQUENCES.md).
