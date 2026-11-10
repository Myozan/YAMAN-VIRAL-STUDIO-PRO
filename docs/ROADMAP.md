# YAMAN VIRAL STUDIO PRO — Product Roadmap

## Product direction
Evolve the local-first video clipping MVP into a governed content operations platform: ingest and analyze source videos, create platform-specific edits and metadata, publish through official APIs after authorization, observe available performance metrics, and use measured outcomes to improve future recommendations.

## Release plan

### v1.3 — Agent foundation
- Add LangGraph as the workflow orchestrator, behind a provider-neutral agent interface.
- Implement supervisor, video analyst, editor, SEO, compliance, publishing-preparation, analytics, and learning roles.
- Persist workflow runs, step events, agent outputs, approvals, and failures.
- Keep Ollama as the local model provider; support a small-model profile for 8 GB RAM systems.
- Add deterministic fallback behavior when the local model is unavailable.
- Add workflow inspection, retries, cancellation, and audit history.

Acceptance:
- An analysis request creates a persisted workflow.
- Every agent step has status, timestamps, input/output references, and error details.
- Model failure does not silently claim success; deterministic fallback is labeled.
- No platform publish action can execute without an active account grant and required approval.

### v1.4 — SEO and metadata engine
- Generate independent metadata packages for YouTube, Instagram Reels, and TikTok.
- Include title/caption, description, keywords, hashtags, platform tags where supported, language, category, cover guidance, and CTA.
- Add keyword extraction, duplicate detection, length validation, policy checks, and editable previews.
- Score metadata quality transparently; never represent an internal score as an official platform ranking.
- Store prompt/model/version and user edits for learning.

Acceptance:
- One source clip can produce distinct platform metadata variants.
- All generated metadata is editable before publishing.
- Unsupported metadata fields are omitted rather than sent to APIs.

### v1.5 — YouTube integration
- OAuth 2.0 authorization with least-privilege scopes.
- Upload and schedule supported video formats using YouTube Data API.
- Read channel/video analytics through YouTube Analytics API where granted.
- Store refresh tokens encrypted; support disconnect and token revocation.
- Show API quota and ingestion freshness.

### v1.6 — Instagram and TikTok integrations
- Instagram Graph API for eligible professional accounts and supported media publishing/insights.
- TikTok Content Posting API with creator capability checks, consent, and publishing status.
- Handle platform review requirements, permissions, media constraints, and rate limits.
- Keep per-platform connection status independent.

### v1.7 — Live Analytics Center
- Unified metrics dashboard with platform-specific availability labels.
- Poll at platform-compliant intervals; use webhooks where officially supported.
- Display last successful sync, data age, rate-limit state, and partial-data warnings.
- Compare posts only where metric definitions are comparable.

### v1.8 — Learning and content operations
- Link published posts to source clips, edits, metadata, and workflow runs.
- Learn from actual results with sample-size thresholds and uncertainty indicators.
- Recommend experiments; do not autonomously change strategy without user-configured rules.
- Add content calendar, approval queues, and policy-based automation.

## Engineering principles
1. Local-first for media analysis; official cloud APIs only for platform operations and authorized analytics.
2. Human approval by default for publishing; optional automation must be explicitly configured.
3. Never store account passwords. Use OAuth and encrypted, revocable tokens.
4. Treat API metrics as delayed/partial unless the provider guarantees otherwise.
5. Keep provider-specific code behind adapters.
6. Do not copy third-party repositories wholesale; use dependencies under their licenses and preserve notices.
7. Make every publish, token, and settings change auditable.

## Branch strategy
- `main`: stable releases only.
- `feature/v1.3-agent-foundation`: current architecture and roadmap work.
- Subsequent feature branches should be cut from the reviewed v1.3 baseline.
