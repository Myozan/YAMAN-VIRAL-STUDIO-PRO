# Changelog · Sürüm Geçmişi

Bu dosya yayımlanmış değişiklikleri yol haritasındaki hedeflerden ayrı tutar.
This file records shipped changes separately from planned roadmap work.

## 🇹🇷 Türkçe

### [v1.2] — 10 Kasım 2026

#### Eklenenler
- FastAPI tabanlı, yerel öncelikli video analiz uygulaması.
- yt-dlp ile desteklenen YouTube kaynaklarını içe aktarma.
- Faster-Whisper ile zaman damgalı konuşma çözümleme.
- İsteğe bağlı yerel Ollama modeliyle aday klip değerlendirme ve sezgisel yedek puanlama.
- FFmpeg ile klip kesme, altyazı işleme ve YouTube Shorts, Instagram Reels ve TikTok için dikey video üretimi.
- Yerel proje/çalışma alanı yönetimi ve performans öğrenme kayıtları.
- Sağlık, ayarlar, sistem metrikleri, analiz görevleri, render, metaveri ve öğrenme için REST API uç noktaları.
- Analiz, klipler, ayarlar ve sistem durumu için web paneli.
- CPU/RAM ölçümleri ve desteklenen sistemlerde NVIDIA GPU/VRAM/sıcaklık telemetrisi.
- Windows başlatma betiği ve Python bağımlılık listesi.

#### İyileştirmeler ve düzeltmeler
- Hafif yerel model profili ve yapılandırılabilir Whisper model/cihaz ayarları.
- CUDA kullanılabilir olduğunda GPU destekli Faster-Whisper başlatma; uygun olmayan durumda CPU yedeği.
- Düşük kaynaklı Windows sistemleri için daha esnek model seçenekleri.
- Modern koyu panel, responsive yerleşim ve daha anlaşılır görev/pipeline durumları.
- UTF-8 ve Türkçe karakter gösterimi iyileştirmeleri.
- Yerel çalışma varsayılanları ve makineye özel ayarların kaynak kodundan ayrılması.
- OpenCV 5 sürümlerinde bulunmayan cv2.CascadeClassifier özelliğine render bağımlılığı kaldırıldı; dikey çıktı FFmpeg üzerinden üretilir.
- Render edilmiş MP4 dosyaları için video kütüphanesi, oynatıcı, indirme ve canlı render önizlemeleri eklendi.
- Analiz işleri diske kaydedilerek uygulama yeniden başlatıldığında proje listesinden geri yüklenir.

#### Dokümantasyon
- Türkçe ve İngilizce README, mimari, kurulum, API, güvenlik ve yol haritası belgeleri.
- Gerçek Studio ekran görüntüsü ve mimari/özellik/yol haritası görselleri.
- Geliştirici kredisi: **Ozan Yaman**.
- Uygulanan özelliklerle gelecek hedeflerinin açık biçimde ayrılması.

#### Bilinen kapsam sınırları
- OAuth tabanlı otomatik yayınlama, v1.2 için doğrulanmış kapsamda değildir.
- Kalıcı çok ajanlı orkestrasyon, üretim seviyesinde çok kiracılı altyapı ve merkezi bulut mimarisi yol haritasındadır.
- GPU telemetrisi, her modelin veya FFmpeg işleminin GPU kullandığı anlamına gelmez.
- Dikey kadraj, mevcut sürümde FFmpeg merkez kırpma yaklaşımını kullanır; yüz takibi garantisi verilmez.

### [Dokümantasyon yenilemesi] — 11 Kasım 2026
- README bilgi mimarisi, kurulum, API referansı, güvenlik ve iki dilli içerik yeniden düzenlendi.
- Kapak tasarımına **Ozan Yaman** geliştirici imzası eklendi.
- Özellik haritası, sürüm yol haritası ve dil desteği infografikleri eklendi.
- Varsayılan Windows portunun 8765 olduğu ve geliştirme sırasında farklı port seçilebileceği açıklandı.
- Konuşma dili seçimi ile arayüz yerelleştirmesi arasındaki fark netleştirildi.

### [Render ve kütüphane düzeltmesi] — 11 Kasım 2026
- OpenCV 5 uyumsuzluğundan kaynaklanan CascadeClassifier render hatası giderildi.
- Tek geçişli FFmpeg render yolu varsayılan hâle getirildi; gereksiz ara video üretimi önlendi.
- Video kütüphanesi ve MP4 oynatıcı akışı için kalıcı iş/çıktı kayıtları iyileştirildi.

## 🇬🇧 English

### [v1.2] — 2026-11-10

#### Added
- Local-first video analysis application powered by FastAPI.
- Supported YouTube source ingestion through yt-dlp.
- Timestamped speech transcription using Faster-Whisper.
- Optional local Ollama model for candidate-clip evaluation, with heuristic fallback scoring.
- FFmpeg-based clipping, subtitle processing, and vertical outputs for YouTube Shorts, Instagram Reels, and TikTok.
- Local project/workspace management and performance observations.
- REST endpoints for health, settings, system metrics, analysis jobs, rendering, metadata, and learning.
- Browser dashboard for analysis, clips, settings, and system status.
- CPU/RAM metrics and optional NVIDIA GPU/VRAM/temperature telemetry.
- Windows launcher and Python dependency manifest.

#### Improved and fixed
- Lightweight local model profile and configurable Whisper model/device settings.
- CUDA-aware Faster-Whisper initialization with CPU fallback.
- More flexible options for resource-constrained Windows systems.
- Responsive dark dashboard and clearer task/pipeline states.
- UTF-8 and Turkish-character handling.
- Local-first defaults and separation of machine-specific settings from source code.
- Removed the render-time dependency on cv2.CascadeClassifier, which is absent in OpenCV 5 builds; vertical rendering uses FFmpeg.
- Added a generated-video library with playback, download, and live render previews.
- Persisted analysis jobs so projects can be restored after application restarts.

#### Documentation
- Bilingual README plus architecture, installation, API, security, and roadmap documentation.
- Studio screenshot and architecture/feature/roadmap visuals.
- Developer credit: **Ozan Yaman**.
- Clear separation between shipped capabilities and roadmap targets.

#### Known scope limits
- OAuth-based automatic publishing is not part of the verified v1.2 scope.
- Persistent multi-agent orchestration, production multi-tenancy, and centralized cloud infrastructure remain roadmap work.
- GPU telemetry does not imply that every model or FFmpeg operation runs on the GPU.
- Current vertical framing uses FFmpeg center cropping; face tracking is not guaranteed.

### [Documentation refresh] — 2026-11-11
- Reorganized README information architecture, installation, API reference, security notes, and bilingual sections.
- Added developer credit and feature, roadmap, and language-support infographics.
- Clarified the default Windows port (8765) and speech-language versus UI localization.

### [Render and library fixes] — 2026-11-11
- Fixed the OpenCV 5 CascadeClassifier render failure.
- Made the single-pass FFmpeg render path the default and removed unnecessary intermediate video generation.
- Improved persistence for the video library and MP4 playback workflow.

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
