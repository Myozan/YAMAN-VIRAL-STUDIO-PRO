# YAMAN-VIRAL-STUDIO-PRO

Local-first AI video clipping and social content operations platform.

## Project status
The repository is being prepared for the v1.3 agent-foundation milestone. The current branch contains the product roadmap, architecture, and platform integration specifications. These documents are implementation plans, not claims that OAuth publishing or live analytics are already implemented.

## Documentation
- [Product roadmap](docs/ROADMAP.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Platform integrations](docs/PLATFORM-INTEGRATIONS.md)

## Direction
- Local media analysis with Ollama, Whisper, FFmpeg, and OpenCV.
- Multi-agent workflows orchestrated with LangGraph.
- Platform-specific SEO metadata for YouTube, Instagram, and TikTok.
- Official OAuth-based publishing and authorized analytics.
- Approval gates, audit history, and performance-based learning.

## Security
Never commit OAuth credentials, access/refresh tokens, encryption keys, local settings files, downloaded media, or generated secrets. Use environment variables or a protected local secret store. Publishing must remain approval-gated unless the account owner explicitly configures an unattended rule.

## Development
See the roadmap and architecture documents before implementing new modules. Platform integrations must use official APIs and respect account eligibility, app review, permissions, rate limits, and API terms.
