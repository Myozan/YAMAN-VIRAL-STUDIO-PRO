# GitHub AI Agent and Video Pipeline Research

Research date: 2026-11-11

## Integration decision

YAMAN VIRAL STUDIO PRO remains a Windows-friendly, local-first FastAPI + Ollama + Faster-Whisper + FFmpeg application. The v1.3.0 implementation expands the in-house specialist team from eight to twelve focused workers and keeps each report in the existing per-clip report-card format. No third-party framework source was copied into the application.

## Repositories reviewed

| Repository | License | Useful capability | Decision |
|---|---|---|---|
| [artbyjazi/autoclip](https://github.com/artbyjazi/autoclip) | MIT | Local-first video ingestion, Whisper/Ollama highlight selection, speaker-aware reframing, caption styles, aspect-ratio exports | Best video-pipeline reference. Workflow ideas were assessed against our current pipeline; the full package was not vendored because it introduces a separate frontend/runtime and optional MediaPipe/WhisperX dependencies. |
| [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | MIT | Role-based agent teams and event-driven Flows | Reviewed. Our existing specialist workers already use role-scoped prompts, independent outputs and fallback results; adding CrewAI now would duplicate orchestration and expand dependencies. |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | MIT | Stateful graphs, durable execution, checkpointing, human-in-the-loop and resumable workflows | Recommended future option if jobs need durable resume, cancellation and human approval gates. Not added to runtime in v1.3.0. |

## v1.3.0 implementation

- Added four local Ollama specialists: Audience Retention Analyst, Thumbnail/Visual Director, Localization Specialist and Accessibility Reviewer.
- Existing agents remain Viral Strategist, Hook Writer, Editor Director, SEO Specialist, Claim Reviewer, Caption QA, Clip QA and Publishing Coordinator.
- Reports remain structured JSON and are shown in the existing clip report panel.
- Agent progress totals are driven by the catalog instead of a hard-coded eight-agent count.
- Short/sparse speech is less likely to fail before candidate generation; a fallback candidate is produced from real recognized transcript segments when possible.
- Platform export profiles are now editable and persisted locally; their dimensions and maximum duration are applied by FFmpeg rendering.

## Not enabled

- No automatic TikTok/Instagram/YouTube account upload. Official API access and OAuth credentials must be configured and approved separately.
- No third-party agent code was copied or installed. The reviewed repositories are documented as design references, not bundled dependencies.
- No browser-control agent is allowed to publish or modify accounts without explicit user approval.

## Next engineering priorities

1. Parallel agent execution with bounded worker concurrency.
2. Durable task checkpoints, cancellation, retry policy and restart recovery.
3. Optional sandboxed web-research tool for claim verification.
4. Agent output schema validation and user approval checkpoints.
