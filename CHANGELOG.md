## [1.8.0] - 2026-11-11

### Added
- Premium AI Creator Studio home hero showing the Whisper → Ollama → FFmpeg workflow and 9:16 output.
- Version-stamped v1.8.0 README hero and GitHub social preview artwork.
- Updated live desktop and mobile screenshots for the README showcase.
- Consistent YAMAN brand identity across favicon, Windows ICO, PWA and Apple touch icons.
- GitHub update checker and user-approved update installation flow with backup and local-data preservation.

### Improved
- Removed the GitHub repository card from the sidebar; the repository link remains in the top bar.
- Moved the desktop sidebar collapse button into a separate row to prevent overlap with the brand mark.
- Reduced the theme icon size and improved mobile layout constraints.
- Rebuilt Turkish, English, German and Spanish README pages with consistent product visuals.
- Clarified MIT Community source, optional commercial modules, third-party dependencies and brand rights in LICENSING.md.

### Preserved
- Existing Whisper, Ollama, FFmpeg, Autopilot, media library and project workflows.
- Local workspace, environment settings, user media, tokens and local application data during updates.

## [1.7.0] - 2026-11-11

### Added
- Optional Auto-Editor silence removal from media-library cards. The original MP4 is preserved and a separate edited copy is created.
- Ollama connection diagnostics, selected-model availability reporting and a Windows desktop-app start action in Settings.
- Actionable Ollama connection, timeout and API error messages for analysis and script generation.

### Improved
- Windows Proactor client-disconnect handling filters only the expected WinError 10054 callback while preserving unrelated asyncio errors.
- README documentation uses UTF-8 Turkish text and corrected installation guidance.
- Settings retains the appearance theme selector; the web asset cache version is refreshed.

### Notes
- Auto-Editor must be installed separately from its official Windows release binary and added to PATH. The CLI is no longer published on PyPI.
- HTTP 206 Partial Content is a normal response for browser video range requests, not an application error.
- Auto-Editor output is created beside the source with the suffix _SILENCE_CUT.mp4; source media is not overwritten.

## [1.6.0] - 2026-11-11

### Added
- Cinematic trailer script direction with multi-shot scene plans, visual prompts, camera movement and three-act pacing.
- Encrypted Runway and Pexels provider credentials, with environment-variable overrides.
- Runway image generation and image-to-video B-roll generation, plus optional generated instrumental score.
- Pexels scene-based stock video search and download with attribution metadata.
- Cinematic vertical montage rendering with opening/closing title cards, narration, optional score mix and media-library integration.

### Notes
- Runway image/video/music generation consumes provider credits and starts only when the user selects the Runway provider.
- Pexels provides licensed stock footage, not AI-generated video; attribution is surfaced.
- Local GTX 1650 4 GB VRAM is not a practical target for modern high-quality video diffusion. A local motion-graphics fallback remains available.
- API credentials are encrypted at rest using the existing local Fernet vault.

## [1.5.9] - 2026-11-11
- One-click source-free Shorts production: local Ollama script generation, neural narration, scene-card design, animated 9:16 rendering and MP4 export.
- Downloadable MP4, script and MP3 outputs with an in-page video preview.
- Responsive end-to-end creator workspace with optional trend-based topic discovery.

## [1.5.8] - 2026-11-11
- Improved content-generation controls and production workflow stability.

## [1.5.7] - 2026-11-11
- Improved creator workspace responsiveness and media handling.

## [1.5.6] - 2026-11-11
- Updated mobile layout and PWA asset cache.

## [1.5.5] - 2026-11-11
- Improved creator project navigation and editing workflow.

## [1.5.4] - 2026-11-11
- Improved local media import and video workflow reliability.

## [1.5.3] - Story-flow video format
- Added a selectable narrative video format: Topic, Introduction, Development, Conclusion and Closing/CTA.
- Added timestamp-grounded AI story-beat selection and a five-part transcript fallback.
- Burned chapter labels into story-format exports and kept speech captions aligned.
- Kept the existing smart-summary format and its output filename separate.

## [1.5.2] - 2026-11-11
- Improved video editing and local AI workflow stability.

## [1.4.1] - 2026-11-11
- Added Turkish, English, German and Spanish locale options with browser-persisted preference.
- Rebuilt all four README language pages with consistent professional layout and screenshots.

## [1.4.0] - 2026-11-11
- Added persistent SQLite task and event history.
- Added task cancellation, retry and recovery after application restart.
- Added local AI agent retry policies.
- Added user-approved OAuth publishing workflows for YouTube, TikTok and Instagram.
- Stored OAuth client credentials and user tokens in the encrypted local Fernet vault.
- Added user-approved resumable MP4 upload for YouTube Data API.
- Added TikTok Content Posting API upload flow and AI-generated label preference.
- Added Instagram Graph API Reels container and publishing workflow.
- Added developer Client ID/Secret management and connection status controls.
- Added user-approved publishing actions to the media library.
- Added Turkish and English interface language selector.

### OAuth limitations
- Real account linking requires a platform developer app, Client ID/Secret, valid callback URL and approved platform scopes.
- Unreviewed TikTok clients may be limited to private posting.
- Instagram Reels publishing requires a publicly reachable HTTPS media URL; localhost paths cannot be used.
- Every publishing action requires user approval; silent background publishing is not performed.

## [1.3.0] - 2026-11-11
- Added four specialist agents, bringing the agent catalog to twelve.
- Improved mobile layout, platform profiles and short-clip selection.
- Added intelligent video recap MP4 generation and report cards.

## [1.2.1] - 2026-11-10
- Repaired the Studio page and improved local video scanning, transcription and system metrics.
