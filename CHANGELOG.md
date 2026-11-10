# Changelog · Sürüm Geçmişi

Bu dosya yayımlanmış değişiklikleri yol haritasındaki hedeflerden ayrı tutar.  
This file separates shipped changes from planned roadmap items.

## 🇹🇷 Türkçe

### [v1.2] — 10 Kasım 2026

#### Eklenenler
- FastAPI tabanlı, yerel öncelikli video analiz uygulaması.
- yt-dlp ile desteklenen YouTube kaynaklarını alma.
- Faster-Whisper ile zaman damgalı konuşma çözümleme.
- Aday kesitleri değerlendirmek için isteğe bağlı yerel Ollama modeli ve sezgisel yedek puanlama.
- FFmpeg ile video kesme, altyazı işleme ve dikey çıktı üretimi.
- OpenCV tabanlı yüz algılama ve kadraj yardımcıları.
- Yerel proje/çalışma alanı yönetimi ve performans öğrenme kayıtları.
- Sağlık, ayarlar, sistem metrikleri, analiz görevleri, render, metaveri, ajan yardımcıları ve öğrenme için REST API uç noktaları.
- Analiz ilerlemesi, kesitler, ayarlar ve sistem durumu için web paneli.
- CPU/RAM ölçümleri; desteklenen sistemlerde NVIDIA GPU, VRAM ve sıcaklık telemetrisi.
- Windows başlatma betiği ve Python bağımlılık listesi.

#### İyileştirmeler
- Hafif yerel model profili ve yapılandırılabilir Whisper model/cihaz ayarları.
- CUDA kullanılabilir olduğunda GPU destekli Faster-Whisper başlatma; uygun olmayan durumda CPU fallback.
- Düşük kaynaklı Windows sistemleri için daha esnek model seçenekleri.
- Modern koyu panel tasarımı, responsive yerleşim ve daha anlaşılır görev/pipeline durumları.
- UTF-8 ve Türkçe karakter gösterimi iyileştirmeleri.
- Yerel çalışma varsayılanları ve makineye özel ayarların kaynak kodundan ayrılması.

#### Dokümantasyon
- Türkçe ve İngilizce README.
- Mimari, platform entegrasyonları ve ürün yol haritası belgeleri.
- Gerçek Studio ekran görüntüsü, üretim hattı ve mimari diyagramları.
- Uygulanan özelliklerle gelecek hedeflerinin açık biçimde ayrılması.

#### Bilinen kapsam sınırları
- OAuth tabanlı otomatik yayınlama v1.2'nin doğrulanmış kapsamına dahil değildir.
- Kalıcı çok ajanlı orkestrasyon, üretim seviyesinde çok kiracılı altyapı ve merkezi bulut mimarisi yol haritasındadır.
- GPU telemetrisi, her modelin veya FFmpeg işleminin GPU kullandığı anlamına gelmez.

### [Dokümantasyon yenilemesi] — 11 Kasım 2026

- README bilgi mimarisi, kurulum, API referansı, güvenlik ve iki dilli içerik profesyonel biçimde yeniden düzenlendi.
- Kapak tasarımına **Ozan Yaman** geliştirici imzası eklendi.
- Özellik haritası, sürüm yol haritası ve dil desteği infografikleri eklendi.
- Ayrı sürüm geçmişi dosyası oluşturuldu.
- Varsayılan Windows portunun 8765 olduğu, farklı portların geliştirme sırasında seçilebileceği açıklandı.
- Konuşma dili seçimi ile arayüz yerelleştirmesi arasındaki fark netleştirildi.

## 🇬🇧 English

### [v1.2] — 2026-11-10

#### Added
- Local-first video analysis application powered by FastAPI.
- YouTube source ingestion through yt-dlp.
- Timestamped speech transcription using Faster-Whisper.
- Optional local Ollama model for candidate-clip evaluation, with heuristic fallback scoring.
- FFmpeg-based clipping, subtitle processing, and vertical output rendering.
- OpenCV-assisted face detection and framing helpers.
- Local project/workspace handling and learning/performance observations.
- REST endpoints for health, settings, system metrics, analysis tasks, rendering, metadata, agent utilities, and learning records.
- Browser dashboard for analysis progress, clips, settings, and system status.
- CPU and memory metrics, plus NVIDIA GPU/VRAM/temperature telemetry where supported.
- Windows startup script and Python dependency manifest.

#### Improved
- Lightweight local model profile and configurable Whisper model/device settings.
- CUDA-aware Faster-Whisper initialization with CPU fallback when CUDA is unavailable or initialization fails.
- More flexible model options for resource-constrained Windows systems.
- Modern dark dashboard, responsive layout, and clearer task/pipeline states.
- UTF-8 and Turkish-character rendering.
- Local-first defaults and separation of machine-specific settings from source code.

#### Documentation
- Turkish and English README documentation.
- Architecture, platform integration, and product roadmap documents.
- Actual Studio screenshot, workflow diagram, and architecture diagram.
- Clear separation between implemented capabilities and future targets.

#### Known scope limits
- OAuth-based automatic publishing is not part of the verified v1.2 baseline.
- Persistent multi-agent orchestration, production multi-tenancy, and centralized cloud infrastructure remain roadmap work.
- GPU telemetry does not imply that every model or FFmpeg operation runs on the GPU.

### [Documentation refresh] — 2026-11-11

- Reorganized the README information architecture, installation guide, API reference, security notes, and bilingual sections.
- Added **Ozan Yaman** developer credit to the hero artwork.
- Added feature-map, release-roadmap, and language-support infographics.
- Added this release history file.
- Clarified the Windows launcher's default port (8765) and the distinction between speech-language selection and UI localization.
- Corrected the screenshot section to reference the committed Studio screenshot.

---

## Planlanan kilometre taşları · Planned milestones (not released)

| Hedef / Target | Kapsam / Scope |
|---|---|
| v1.3 | Kalıcı ajan iş akışları, retry, iptal ve denetim olayları / Persistent agent workflows, retries, cancellation, audit events |
| v1.4 | Platform bazlı SEO ve metaveri / Platform-specific SEO and metadata |
| v1.5 | Yetkilendirilmiş YouTube OAuth, yükleme ve analitik / Authorized YouTube OAuth, uploads, analytics |
| v1.6 | Uygun hesaplar için Instagram ve TikTok API entegrasyonları / Instagram and TikTok API integrations for eligible accounts |
| v1.7 | Veri güncelliği göstergeli birleşik analitik / Unified analytics with data-freshness indicators |
| v1.8 | Öğrenme, içerik takvimi, onay ve kontrollü otomasyon / Learning, content calendar, approvals, controlled automation |

Bu hedefler yayımlanmış sürümler veya taahhüt edilmiş tarihler değildir.  
These are roadmap targets, not released versions or committed dates.

Ayrıntılar / Details: [docs/ROADMAP.md](docs/ROADMAP.md)
