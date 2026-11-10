# GitHub AI Agent, OAuth and Video Pipeline Research

Research date: 2026-11-11
Implementation release: v1.4.0

## Integration decisions

YAMAN VIRAL STUDIO PRO remains a local-first FastAPI + Ollama + Faster-Whisper + FFmpeg application. The specialist agent team is implemented in-house and expanded to twelve workers. Task orchestration is persisted in SQLite, while provider OAuth credentials and tokens are encrypted in a local Fernet vault.

## Open-source repositories reviewed

| Repository | License | Useful capability | Decision |
|---|---|---|---|
| [artbyjazi/autoclip](https://github.com/artbyjazi/autoclip) | MIT | Local-first video ingestion, Whisper/Ollama highlight selection, speaker-aware reframing, captions and aspect-ratio exports | Workflow reference. Full package not vendored because it introduces a separate frontend/runtime and optional MediaPipe/WhisperX dependencies. |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | MIT | Role-based agent teams and event-driven Flows | Architecture reviewed. Current specialist agents already use role-scoped prompts, structured outputs and fallback results; adding CrewAI now would duplicate orchestration. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | MIT | Stateful graphs, durable execution, checkpointing and human-in-the-loop | Architecture reference. SQLite task journal, event history, cancellation, retry and restart recovery implemented without adding a heavyweight runtime dependency. |

No third-party source files were copied into this repository.

## v1.4.0 agent orchestration

- Twelve specialist agents: Viral Strategist, Hook Writer, Editor Director, SEO Specialist, Claim Reviewer, Caption QA, Clip QA, Publishing Coordinator, Audience Retention Analyst, Thumbnail/Visual Director, Localization Specialist and Accessibility Reviewer.
- Each agent has its own structured report and fallback result.
- Transient local-model failures receive one bounded retry.
- Task status, request metadata, progress snapshots and audit events are stored in SQLite.
- API supports task history, event inspection, cancellation and retry.
- On process restart, queued/running tasks are marked interrupted and can be retried when their source project is available.
- Cancellation is checked between agent calls; an in-flight Ollama request returns before the worker stops.

## v1.4.0 OAuth and publishing

Official provider APIs are used; OAuth credentials and tokens are encrypted locally using Fernet.

- YouTube: Google OAuth with youtube.upload and resumable upload using the YouTube Data API.
- TikTok: Content Posting API Direct Post with video.publish, creator-info lookup, account-provided privacy options, duration validation, file chunk upload, AI-generated disclosure choice and publish-status polling.
- Instagram: Facebook Login for an Instagram professional account connected to a Page; Reels container, processing-status polling and media_publish. Meta must be able to fetch the supplied public HTTPS video URL.
- Every publish operation requires explicit user confirmation.
- YouTube defaults to private; TikTok UI presents the creator's allowed privacy levels. TikTok unaudited clients are restricted to private visibility.
- No silent background publishing or credential scraping is implemented.

## Official API references

- [YouTube videos.insert](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert)
- [YouTube resumable upload protocol](https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol)
- [TikTok Direct Post](https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post)
- [TikTok Query Creator Info](https://developers.tiktok.com/docs/en/content-posting-api-reference-query-creator-info)
- [TikTok Media Transfer Guide](https://developers.tiktok.com/docs/en/content-posting-api-media-transfer-guide)
- [Meta Instagram Reels publishing](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api)

## Operational constraints

- Each provider needs a registered developer app, client ID/secret, exact callback URI and approved scopes.
- TikTok unaudited apps are limited to private posts; the app must pass TikTok review to unlock broader visibility.
- Instagram publishing requires an eligible professional account linked to a Facebook Page and a publicly accessible HTTPS media URL.
- Local OAuth encryption key .oauth.key must be backed up securely. Losing it makes the local encrypted vault unreadable.
- Real account posting has not been tested because provider developer credentials and user account authorization are not present in the development environment.

## Next engineering priorities

1. Store TikTok/Instagram post status and published media URLs in the task journal.
2. Add resumable upload recovery for interrupted YouTube and TikTok transfers.
3. Add an OAuth refresh/reconnect notification before token expiry.
4. Replace the TikTok privacy text prompt with a visual selector.
5. Add a secure external media host integration for Instagram Reels when the user configures one.
