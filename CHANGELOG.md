## [1.5.5] - 2026-11-11

### Added
- Educational video format with learning objective, introduction, concepts, step-by-step explanation, practical example, recap and mini-quiz.
- Product presentation format with need, product introduction, features, benefits, differentiators, evidence and CTA.
- Separate `education_video.mp4` and `product_video.mp4` exports and media-library entries.
- Source-grounded chapter selection and transcript fallback for both formats; unsupported product claims, prices, reviews and guarantees are not invented.
- Documentary chapter labels are burned into the rendered video, alongside Story, Education and Product chapter labels.

### Improved
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

# Changelog / Sürüm Geçmişi

## [1.4.1] - 2026-11-11

### Added
- Moved the application language selector into Settings → Language & localization.
- Added Turkish, English, German and Spanish locale options with browser-persisted preference.
- Rebuilt all four README language pages with a consistent professional layout, real desktop/mobile screenshots, feature map, workflow, architecture and roadmap visuals.

### Improved
- Expanded the README installation, security, OAuth and project-structure guidance.
- Added clear language-setting instructions to each localized README.

## [1.4.0] - 2026-11-11

### Added
- SQLite tabanlı kalıcı görev ve olay günlüğü.
- Ajan görevlerini iptal etme, başarısız/kesintiye uğramış görevleri yeniden deneme ve uygulama yeniden başladığında görev durumunu kurtarma.
- Yerel AI ajan çağrılarında sınırlı yeniden deneme politikası.
- YouTube, TikTok ve Instagram için resmî OAuth bağlantı akışları.
- OAuth istemci kimlik bilgileri ve kullanıcı tokenları Fernet ile şifrelenerek yerel kasada saklanır.
- YouTube Data API ile kullanıcı onaylı resumable MP4 yükleme.
- TikTok Content Posting API ile kullanıcı onaylı Direct Post dosya yükleme ve AI-generated etiket tercihi.
- Instagram Graph API ile Reels container ve yayınlama akışı; profesyonel hesap/Page bağlantısı keşfi.
- Platform Profilleri ekranına geliştirici Client ID/Secret kaydı, bağlantı durumu, bağlan/kes kontrolleri eklendi.
- Medya kütüphanesine kullanıcı onaylı platform yayınlama eylemi eklendi.
- Türkçe/İngilizce arayüz dil seçici eklendi.
- README belgeleri dil başına ayrı dosyalara ayrıldı: README.md, README.en.md, README.de.md, README.es.md.

### Changed
- CPU kartında yalnızca işlemci modeli ve işlemci kullanımı gösterilir.
- CPU sıcaklığı, çekirdek/thread, saat hızı ve GPU sıcaklığı arayüzden ve telemetri yanıtından kaldırıldı.
- Türkçe gezinme menüsü ve görünür metinler UTF-8/HTML entity tabanlı olarak yeniden düzenlendi.
- Sürüm 1.4.0 olarak güncellendi.

### OAuth limitations and requirements
- Gerçek hesap bağlantısı için platform geliştirici uygulaması, Client ID/Secret, doğru callback adresi ve platform tarafından onaylanmış kapsamlar gerekir.
- TikTok'un denetlenmemiş istemcileri yalnızca özel gönderi yayınlayabilir.
- Instagram Reels, Meta'nın erişebildiği genel HTTPS medya URL'si gerektirir; localhost dosyaları kullanılamaz.
- Her yayın isteği kullanıcı onayı gerektirir; arka planda sessiz yayın yapılmaz.

## [1.3.0] - 2026-11-11
- Dört uzman ajan eklendi; toplam ajan sayısı 12'ye çıkarıldı.
- Mobil düzen, platform profilleri ve kısa video kesit seçimi iyileştirildi.
- Videodan akıllı özet MP4 üretimi ve rapor kartları eklendi.

## [1.2.1] - 2026-11-10
- Studio sayfası onarıldı; yerel video tarama, transkripsiyon ve sistem göstergeleri geliştirildi.

## [1.5.3] - Story-flow video format

- Added a selectable narrative video format: Topic, Introduction, Development, Conclusion and Closing/CTA.
- Added timestamp-grounded AI story beat selection and a five-part transcript fallback.
- Burned chapter labels into story-format exports and kept speech captions aligned.
- Kept the existing smart-summary format and its output filename separate.
