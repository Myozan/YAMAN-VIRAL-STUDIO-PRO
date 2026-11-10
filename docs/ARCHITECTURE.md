# Architecture

## High-level components

- Web UI: Studio, Content Production, Projects, Platform Profiles, Settings, Agent Center, SEO Studio, Live Analytics, Publishing Calendar.
- FastAPI application: authentication/session boundary, REST API, validation, orchestration entry points.
- Workflow engine: LangGraph state graph with explicit nodes, edges, retries, interrupt/approval nodes, and resumable execution.
- Agent adapters: role prompts and structured output contracts; Ollama is the first local inference provider.
- Media pipeline: yt-dlp (source retrieval subject to rights/platform terms), Faster-Whisper, FFmpeg, OpenCV.
- Persistence: PostgreSQL for users, projects, workflows, assets, metadata, connections, posts, analytics snapshots, approvals, audit events.
- Queue/cache: Redis for background work, scheduling, short-lived locks, and rate-limit coordination.
- Object storage: local filesystem initially; configurable NAS/object-storage adapter later.
- Platform adapters: YouTube, Instagram Graph API, TikTok Content Posting API.
- Observability: structured logs, workflow event stream, health checks, metrics freshness and API quota tracking.

## Agent workflow

1. Intake validates source URL, user rights/authorization declaration, language, target platforms, and output constraints.
2. Video Analyst consumes transcript and sampled frames; returns timestamped candidate moments with evidence.
3. Editor prepares clip boundaries, aspect ratio, subtitles, framing, and render plan.
4. SEO Specialist produces one structured metadata object per selected platform.
5. Compliance Agent checks content, rights declarations, prohibited material, platform constraints, and metadata consistency.
6. Approval interrupt presents preview, metadata, target account, schedule, and final publish action.
7. Publishing Agent calls only the selected platform adapter after approval and valid OAuth grant.
8. Analytics Agent syncs available post metrics and records provider timestamps/definitions.
9. Learning Agent updates recommendations only after sufficient observations and records confidence/sample size.

Each node emits a typed result and an immutable workflow event. Agent outputs are not trusted as executable commands.

## Suggested persistence entities

- users, sessions
- projects, source_media, transcripts, clips, rendered_assets
- workflow_runs, workflow_steps, workflow_events
- metadata_packages, metadata_revisions
- platform_connections, encrypted_oauth_tokens, granted_scopes
- publish_jobs, published_posts, publish_attempts
- analytics_snapshots, metric_definitions, sync_cursors
- approvals, audit_events
- model_profiles, prompt_versions, learning_observations

## Security boundaries

- Bind the local development server to 127.0.0.1 by default.
- Keep OAuth client secrets and token encryption keys out of source control.
- Encrypt refresh/access tokens at rest using an OS-protected or environment-injected key.
- Redact tokens, authorization headers, and sensitive query parameters from logs.
- Validate OAuth state and PKCE where supported; validate redirect URIs exactly.
- Request minimum scopes and support disconnect/revoke.
- Require explicit approval before first publishing and before enabling unattended publishing rules.
- Use per-user ownership checks for every project, connection, and asset.
- Do not expose arbitrary shell, filesystem, or network tools to LLM agents.
- Apply upload size, duration, and URL/domain restrictions to media ingestion.

## Live analytics semantics

"Live" means periodically refreshed within the provider's API limits, not guaranteed second-by-second streaming. Every metric must carry:
- provider and account
- post/video identifier
- metric name and provider definition
- value and period/window
- fetched_at and provider_updated_at when available
- freshness state (fresh, delayed, stale, unavailable)
- source API and permission context

Do not compare unlike metrics as if they had identical definitions across platforms.

## Recommended deployment progression

### Local single-user
FastAPI + static UI + SQLite/PostgreSQL + local filesystem + Ollama. Redis optional until background concurrency is needed.

### Connected publishing
PostgreSQL + Redis worker + encrypted OAuth token store + platform adapters + scheduler.

### Multi-user/production
Tenant isolation, managed secrets, HTTPS reverse proxy, database backups, object storage, monitoring, quotas, and formal OAuth app review.
