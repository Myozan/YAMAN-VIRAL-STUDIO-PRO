# Showcase assets

This folder contains the public-facing visual assets for YAMAN VIRAL STUDIO PRO.

## Live captures

- `assets/screenshot-live-desktop.png` — live app UI captured from the current repository branch at 1600 × 1100.
- `assets/screenshot-live-mobile.png` — compact responsive viewport capture at 600 × 1200.
- `assets/social-preview.png` — 1280 × 640 GitHub social preview, rendered from the repository's social-preview artwork.

The system gauges in the live screenshots are real values at capture time and naturally change with the machine load.

## Product overview

- `assets/showcase-demo.mp4` — 20-second visual product overview.
- `assets/showcase-demo.gif` — lightweight animated preview for the README.

The overview is composed from live application screenshots with transitions. It is a product/visual tour, not a screen recording of a completed video-analysis job. No user video or third-party copyrighted source was used.

## Recreate captures

1. Clone the current branch and install `requirements.txt`.
2. Ensure FFmpeg/FFprobe and the local Ollama service are available.
3. Start the app on localhost.
4. Capture the desktop and compact viewports with a Chromium-based browser.
5. Rebuild the product overview from the updated screenshots using FFmpeg.

Do not publish screenshots containing OAuth secrets, private account details, or user media without permission.
