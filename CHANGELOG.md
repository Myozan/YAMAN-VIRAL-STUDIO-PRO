## [1.8.0] - 2026-11-11

### Added
- Premium AI Creator Studio home hero with the Whisper → Ollama → FFmpeg workflow and 9:16 output preview.
- Custom v1.8.0 version artwork for the README hero and GitHub social preview.
- Updated live desktop and mobile application screenshots for the README showcase.
- Consistent YAMAN brand mark across favicon, Windows ICO, PWA and Apple touch icons.
- GitHub branch update checker and user-approved update installation flow with backups and local-data preservation.

### Improved
- Removed the GitHub repository promotion card from the sidebar; repository access remains in the top bar.
- Moved the desktop sidebar collapse control into a separate control row to prevent overlap with the logo.
- Reduced theme icon dimensions to prevent overflow.
- Improved mobile viewport layout for the main hero and dashboard.
- Rebuilt Turkish, English, German and Spanish README pages with consistent product visuals.
- Clarified MIT Community source, commercial-module boundaries, third-party dependencies and brand rights in LICENSING.md.

### Preserved
- Existing Whisper, Ollama, FFmpeg, Autopilot, video library and project workflows.
- Local workspace, environment settings, user media, tokens and local application data during updates.
## [1.7.0] - 2026-11-11

### Added
- Optional Auto-Editor silence removal from media-library cards. The original MP4 is preserved and a separate edited copy is created.
- Ollama connection diagnostics, selected-model availability reporting and a Windows desktop-app start action in Settings.
- Actionable Ollama connection, timeout and API error messages for analysis and script generation.

### Improved
- Windows Proactor client-disconnect handling now filters only the expected WinError 10054 callback while preserving unrelated asyncio errors.
- README.md rewritten as valid UTF-8 Turkish documentation with corrected characters and updated installation guidance.
- Settings continues to contain the appearance theme selector; the web asset cache version is refreshed.

### Notes
- Auto-Editor must be installed separately from its official Windows release binary and added to PATH. The CLI is no longer published on PyPI.
- HTTP 206 Partial Content is a normal response for browser video range requests, not an application error.
- Auto-Editor output is created beside the source with the suffix _SILENCE_CUT.mp4; source media is not overwritten.

## [1.6.0] - 2026-11-11

### Added
- Cinematic trailer script direction with a multi-shot scene plan, filmable visual prompts, camera movement and three-act pacing.
- Encrypted Runway and Pexels provider credentials, with environment-variable overrides.
- Runway image generation and image-to-video B-roll generation, plus optional generated instrumental score.
- Pexels scene-based stock video search and download with attribution metadata.
- Cinematic vertical montage renderer with opening/closing title cards, narration, optional score mix and media-library integration.

### Notes
- Runway image/video/music generation consumes paid provider credits; generation is only started when the user selects the Runway provider.
- Pexels provides licensed stock footage, not AI-generated video; attribution is surfaced.
- Local GTX 1650 4 GB VRAM is not a practical target for modern high-quality video diffusion. Local motion-graphics fallback remains available.
- API credentials are encrypted at rest using the existing local Fernet vault.

## [1.5.9] - 2026-11-11

### Added
- One-click source-free Shorts production: local Ollama script generation, neural narration, automatic scene-card design, animated 9:16 video rendering and MP4 export.
- Downloadable MP4, script and MP3 outputs with an in-page video preview.
- A responsive end-to-end creator workspace with optional trend-based topic discovery.

### Improved
- Moved appearance themes from the sidebar into Settings and reordered the main navigation.
- Updated PWA asset cache and interface version to v1.5.9.

### Visual generation and privacy notes
- This release creates original typographic motion-graphic scenes locally from generated scene directions; it does not yet generate photorealistic AI images or source-footage B-roll.
- Script generation is local through Ollama. Edge Neural TTS is online and sends narration text to Microsoft's service.
- Trend discovery requires internet access. Generated videos remain local until the user chooses to share them.

# Changelog

## [1.5.8] - 2026-11-11

### Added
- Trend discovery from Google Trends RSS, Google News RSS and Reddit RSS, with source labels, relevance hints and graceful source errors.
- Local Ollama script generation with niche, topic, language and target duration controls; scripts are saved as Markdown and JSON.
- Neural voiceover generation with selectable Turkish and English Edge Neural voices, MP3 preview and download.
- Scheduled Autopilot cycles now attempt trend discovery, script writing and voiceover before processing any new local source video.

### Improved
- Autopilot workspace now includes trend discovery, script editing and voiceover tools.
- PWA shell and static asset cache bumped to v1.5.8.

### Privacy and limitations
- Trend discovery requires an internet connection. RSS ranking is a relevance heuristic, not an official popularity metric.
- Script generation runs on the configured local Ollama model.
- Edge Neural TTS uses an online Microsoft service; narration text is sent to that provider. It is not an offline voice engine.
- Social publishing remains user-approved.


## [1.5.7] - 2026-11-11

### Added
- Local-first Autopilot workspace with daily/weekly schedules, niche/language settings, clip limits, platform selection and run-now controls.
- Persistent SQLite automation schedules and run history, plus atomic due-run claiming for multiple local app instances.
- Downloads-folder watcher that analyzes new local videos, selects the top three clips, renders chosen platform variants and leaves outputs for manual review.

### Improved
- Autopilot navigation, responsive setup wizard, automation cards, pause/resume and delete controls.
- PWA asset cache version bumped to v1.5.7.

### Safety
- Autopilot never publishes automatically; social posting remains behind the existing explicit confirmation flow.
- Clearly documents current local capabilities and features not yet implemented (trend discovery, text-to-video, voice cloning and automatic posting).

## [1.5.6] - 2026-11-11

### Added
- Home-screen automatic editing workflow for Smart Recap and Documentary, including moment selection, trimming, ordering, merging and MP4 export.
- Fade-to-black / fade-in transition or clean-cut selection, plus caption and chapter-title toggles.
- Transcript-only salience scoring fallback to prioritize meaningful spoken moments across the timeline.

### Improved
- Mobile layout alignment for studio panels, summary controls, navigation, system metrics and editing options.
- PWA cache version bumped to v1.5.6.

 / S├ö├Â┬ú├ö├▓├İr├ö├Â┬ú├ö├▓├İm Ge├ö├Â┬úÔöÇ┼şmi├ö├ÂÔòØÔö╝┼şi


## [1.5.5] - 2026-11-11

### Added
- Educational video format with learning objective, introduction, concepts, step-by-step explanation, practical example, recap and mini-quiz.
- Product presentation format with need, product introduction, features, benefits, differentiators, evidence and CTA.
- Separate `education_video.mp4` and `product_video.mp4` exports and media-library entries.
- Source-grounded chapter selection and transcript fallback for both formats; unsupported product claims, prices, reviews and guarantees are not invented.
- Documentary chapter labels are burned into the rendered video, alongside Story, Education and Product chapter labels.

### Improved
- Refreshed Turkish and English README guides for all five production formats, setup, architecture, PWA and security.
- Replaced the README hero and social preview artwork; added a five-format infographic and refreshed live desktop/mobile screenshots.
- PWA shell and asset cache bumped to v1.5.5.

## [1.5.4] - 2026-11-11

### Added
- Documentary narration format with seven timestamp-grounded chapters: topic, strong opening, background, chronological development, findings, conclusion and closing.
- Separate `documentary_video.mp4` export and media-library entry; Smart recap and Story flow remain independent.
- Transcript-based fallback for incomplete local-model chapter responses; unsupported facts and quotations are not fabricated.

### Improved
- Updated PWA shell and asset cache version for the documentary format release.

## [1.5.2] - 2026-11-11

### Added
- Progressive Web App manifest, branded scalable icons and install-to-home-screen support.
- Service worker with an app-shell cache for the interface; API responses and private workspace files are deliberately excluded from caching.
- Install button for supported browsers and Add to Home Screen guidance for iOS Safari.

### Notes
- PWA installation and service workers require HTTPS or localhost/127.0.0.1.
- Offline mode caches the application shell only. Video analysis, AI processing, OAuth, uploads and other API features still require the YAMAN backend and their local services to be running.
- To install on a phone, the app must be reachable from that phone through a trusted HTTPS origin. The default Windows launcher binds to 127.0.0.1 and is intentionally not exposed to the LAN automatically.

## [1.4.1] - 2026-11-11

### Added
- Moved the application language selector into Settings Ôö£├ÂÔö£├æÔö£├Ñ Language & localization.
- Added Turkish, English, German and Spanish locale options with browser-persisted preference.
- Rebuilt all four README language pages with a consistent professional layout, real desktop/mobile screenshots, feature map, workflow, architecture and roadmap visuals.

### Improved
- Expanded the README installation, security, OAuth and project-structure guidance.
- Added clear language-setting instructions to each localized README.

## [1.4.0] - 2026-11-11

### Added
- SQLite tabanl├ö├Â├ç├ö├╗├å kal├ö├Â├ç├ö├╗├åc├ö├Â├ç├ö├╗├å g├ö├Â┬úÔö£├®rev ve olay g├ö├Â┬ú├ö├▓├İnl├ö├Â┬ú├ö├▓├İ├ö├Â├çÔö╝┼ş├ö├Â┬ú├ö├▓├İ.
- Ajan g├ö├Â┬úÔö£├®revlerini iptal etme, ba├ö├ÂÔòØÔö╝┼şar├ö├Â├ç├ö├╗├ås├ö├Â├ç├ö├╗├åz/kesintiye u├ö├Â├çÔö╝┼şram├ö├Â├ç├ö├╗├å├ö├ÂÔòØÔö╝┼ş g├ö├Â┬úÔö£├®revleri yeniden deneme ve uygulama yeniden ba├ö├ÂÔòØÔö╝┼şlad├ö├Â├ç├ö├╗├å├ö├Â├çÔö╝┼ş├ö├Â├ç├ö├╗├ånda g├ö├Â┬úÔö£├®rev durumunu kurtarma.
- Yerel AI ajan ├ö├Â┬úÔöÇ┼şa├ö├Â├çÔö╝┼şr├ö├Â├ç├ö├╗├ålar├ö├Â├ç├ö├╗├ånda s├ö├Â├ç├ö├╗├ån├ö├Â├ç├ö├╗├årl├ö├Â├ç├ö├╗├å yeniden deneme politikas├ö├Â├ç├ö├╗├å.
- YouTube, TikTok ve Instagram i├ö├Â┬úÔöÇ┼şin resm├ö├Â┬úÔö¼┬¢ OAuth ba├ö├Â├çÔö╝┼şlant├ö├Â├ç├ö├╗├å ak├ö├Â├ç├ö├╗├å├ö├ÂÔòØÔö╝┼şlar├ö├Â├ç├ö├╗├å.
- OAuth istemci kimlik bilgileri ve kullan├ö├Â├ç├ö├╗├åc├ö├Â├ç├ö├╗├å tokenlar├ö├Â├ç├ö├╗├å Fernet ile ├ö├ÂÔòØÔö╝┼şifrelenerek yerel kasada saklan├ö├Â├ç├ö├╗├år.
- YouTube Data API ile kullan├ö├Â├ç├ö├╗├åc├ö├Â├ç├ö├╗├å onayl├ö├Â├ç├ö├╗├å resumable MP4 y├ö├Â┬ú├ö├▓├İkleme.
- TikTok Content Posting API ile kullan├ö├Â├ç├ö├╗├åc├ö├Â├ç├ö├╗├å onayl├ö├Â├ç├ö├╗├å Direct Post dosya y├ö├Â┬ú├ö├▓├İkleme ve AI-generated etiket tercihi.
- Instagram Graph API ile Reels container ve yay├ö├Â├ç├ö├╗├ånlama ak├ö├Â├ç├ö├╗├å├ö├ÂÔòØÔö╝┼ş├ö├Â├ç├ö├╗├å; profesyonel hesap/Page ba├ö├Â├çÔö╝┼şlant├ö├Â├ç├ö├╗├ås├ö├Â├ç├ö├╗├å ke├ö├ÂÔòØÔö╝┼şfi.
- Platform Profilleri ekran├ö├Â├ç├ö├╗├åna geli├ö├ÂÔòØÔö╝┼ştirici Client ID/Secret kayd├ö├Â├ç├ö├╗├å, ba├ö├Â├çÔö╝┼şlant├ö├Â├ç├ö├╗├å durumu, ba├ö├Â├çÔö╝┼şlan/kes kontrolleri eklendi.
- Medya k├ö├Â┬ú├ö├▓├İt├ö├Â┬ú├ö├▓├İphanesine kullan├ö├Â├ç├ö├╗├åc├ö├Â├ç├ö├╗├å onayl├ö├Â├ç├ö├╗├å platform yay├ö├Â├ç├ö├╗├ånlama eylemi eklendi.
- T├ö├Â┬ú├ö├▓├İrk├ö├Â┬úÔöÇ┼şe/├ö├Â├ç├ö├╗├Ğngilizce aray├ö├Â┬ú├ö├▓├İz dil se├ö├Â┬úÔöÇ┼şici eklendi.
- README belgeleri dil ba├ö├ÂÔòØÔö╝┼ş├ö├Â├ç├ö├╗├åna ayr├ö├Â├ç├ö├╗├å dosyalara ayr├ö├Â├ç├ö├╗├åld├ö├Â├ç├ö├╗├å: README.md, README.en.md, README.de.md, README.es.md.

### Changed
- CPU kart├ö├Â├ç├ö├╗├ånda yaln├ö├Â├ç├ö├╗├åzca i├ö├ÂÔòØÔö╝┼şlemci modeli ve i├ö├ÂÔòØÔö╝┼şlemci kullan├ö├Â├ç├ö├╗├åm├ö├Â├ç├ö├╗├å g├ö├Â┬úÔö£├®sterilir.
- CPU s├ö├Â├ç├ö├╗├åcakl├ö├Â├ç├ö├╗├å├ö├Â├çÔö╝┼ş├ö├Â├ç├ö├╗├å, ├ö├Â┬úÔöÇ┼şekirdek/thread, saat h├ö├Â├ç├ö├╗├åz├ö├Â├ç├ö├╗├å ve GPU s├ö├Â├ç├ö├╗├åcakl├ö├Â├ç├ö├╗├å├ö├Â├çÔö╝┼ş├ö├Â├ç├ö├╗├å aray├ö├Â┬ú├ö├▓├İzden ve telemetri yan├ö├Â├ç├ö├╗├åt├ö├Â├ç├ö├╗├åndan kald├ö├Â├ç├ö├╗├år├ö├Â├ç├ö├╗├åld├ö├Â├ç├ö├╗├å.
- T├ö├Â┬ú├ö├▓├İrk├ö├Â┬úÔöÇ┼şe gezinme men├ö├Â┬ú├ö├▓├İs├ö├Â┬ú├ö├▓├İ ve g├ö├Â┬úÔö£├®r├ö├Â┬ú├ö├▓├İn├ö├Â┬ú├ö├▓├İr metinler UTF-8/HTML entity tabanl├ö├Â├ç├ö├╗├å olarak yeniden d├ö├Â┬ú├ö├▓├İzenlendi.
- S├ö├Â┬ú├ö├▓├İr├ö├Â┬ú├ö├▓├İm 1.4.0 olarak g├ö├Â┬ú├ö├▓├İncellendi.

### OAuth limitations and requirements
- Ger├ö├Â┬úÔöÇ┼şek hesap ba├ö├Â├çÔö╝┼şlant├ö├Â├ç├ö├╗├ås├ö├Â├ç├ö├╗├å i├ö├Â┬úÔöÇ┼şin platform geli├ö├ÂÔòØÔö╝┼ştirici uygulamas├ö├Â├ç├ö├╗├å, Client ID/Secret, do├ö├Â├çÔö╝┼şru callback adresi ve platform taraf├ö├Â├ç├ö├╗├åndan onaylanm├ö├Â├ç├ö├╗├å├ö├ÂÔòØÔö╝┼ş kapsamlar gerekir.
- TikTok'un denetlenmemi├ö├ÂÔòØÔö╝┼ş istemcileri yaln├ö├Â├ç├ö├╗├åzca ├ö├Â┬úÔö£├®zel g├ö├Â┬úÔö£├®nderi yay├ö├Â├ç├ö├╗├ånlayabilir.
- Instagram Reels, Meta'n├ö├Â├ç├ö├╗├ån eri├ö├ÂÔòØÔö╝┼şebildi├ö├Â├çÔö╝┼şi genel HTTPS medya URL'si gerektirir; localhost dosyalar├ö├Â├ç├ö├╗├å kullan├ö├Â├ç├ö├╗├ålamaz.
- Her yay├ö├Â├ç├ö├╗├ån iste├ö├Â├çÔö╝┼şi kullan├ö├Â├ç├ö├╗├åc├ö├Â├ç├ö├╗├å onay├ö├Â├ç├ö├╗├å gerektirir; arka planda sessiz yay├ö├Â├ç├ö├╗├ån yap├ö├Â├ç├ö├╗├ålmaz.

## [1.3.0] - 2026-11-11
- D├ö├Â┬úÔö£├®rt uzman ajan eklendi; toplam ajan say├ö├Â├ç├ö├╗├ås├ö├Â├ç├ö├╗├å 12'ye ├ö├Â┬úÔöÇ┼ş├ö├Â├ç├ö├╗├åkar├ö├Â├ç├ö├╗├åld├ö├Â├ç├ö├╗├å.
- Mobil d├ö├Â┬ú├ö├▓├İzen, platform profilleri ve k├ö├Â├ç├ö├╗├åsa video kesit se├ö├Â┬úÔöÇ┼şimi iyile├ö├ÂÔòØÔö╝┼ştirildi.
- Videodan ak├ö├Â├ç├ö├╗├åll├ö├Â├ç├ö├╗├å ├ö├Â┬úÔö£├®zet MP4 ├ö├Â┬ú├ö├▓├İretimi ve rapor kartlar├ö├Â├ç├ö├╗├å eklendi.

## [1.2.1] - 2026-11-10
- Studio sayfas├ö├Â├ç├ö├╗├å onar├ö├Â├ç├ö├╗├åld├ö├Â├ç├ö├╗├å; yerel video tarama, transkripsiyon ve sistem g├ö├Â┬úÔö£├®stergeleri geli├ö├ÂÔòØÔö╝┼ştirildi.

## [1.5.3] - Story-flow video format

- Added a selectable narrative video format: Topic, Introduction, Development, Conclusion and Closing/CTA.
- Added timestamp-grounded AI story beat selection and a five-part transcript fallback.
- Burned chapter labels into story-format exports and kept speech captions aligned.
- Kept the existing smart-summary format and its output filename separate.
