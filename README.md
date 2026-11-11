<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO — Yerel AI Video Stüdyosu" width="100%">

# YAMAN VIRAL STUDIO PRO

### Yerel yapay zekâ destekli video analiz, Shorts üretimi ve çok formatlı içerik stüdyosu

**v1.5.7 · Local-first AI · Windows · PWA**

[![Version](https://img.shields.io/badge/version-1.5.7-6478ff?style=for-the-badge)](CHANGELOG.md)
[![CI](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/actions/workflows/ci.yml/badge.svg?branch=import%2Fv1.2-source)](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-installable-5B8DEF?style=for-the-badge)](#pwa-kurulumu)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

[ T?rk?e ](README.md) ? [ English ](README.en.md) ? [ Deutsch ](README.de.md) ? [ Espa?ol ](README.es.md)

</div>

---

[GitHub sosyal önizleme PNG](docs/assets/social-preview.png) · [Beş format infografiği](docs/assets/video-formats.svg)

## Genel bakış

**YAMAN VIRAL STUDIO PRO**, uzun videoları analiz edip konuşmaları zaman damgalı metne dönüştüren, güçlü anları bulan ve farklı yayın hedefleri için düzenlenmiş videolar üreten yerel öncelikli bir içerik stüdyosudur.

Ollama, Faster-Whisper ve FFmpeg tabanlı iş akışı; video analizi, transkripsiyon ve render işlemlerini mümkün olduğunca kullanıcının kendi bilgisayarında tutar. Tek bir özet yaklaşımına bağlı kalmadan beş ayrı editoryal üretim modu sunar.

## Beş üretim modu

<img src="docs/assets/video-formats.svg" alt="YAMAN VIRAL STUDIO PRO beş video üretim modu" width="100%">

| Mod | İçerik akışı | Çıktı |
|---|---|---|
| **Akıllı Özet** | Kaynağın önemli anlarını seçer ve kısa, akıcı bir özet oluşturur. | `summary_video.mp4` |
| **Hikâye Akışı** | Konu → Giriş → Gelişme → Sonuç → Kapanış | `story_video.mp4` |
| **Belgesel Anlatımı** | Konu → Güçlü Açılış → Arka Plan → Kronolojik Gelişme → Bulgular → Sonuç → Kapanış | `documentary_video.mp4` |
| **Eğitim Videosu** | Öğrenme Hedefi → Giriş → Temel Kavramlar → Adım Adım Anlatım → Uygulama → Özet → Mini Test | `education_video.mp4` |
| **Ürün Tanıtımı** | İhtiyaç → Ürün → Özellikler → Faydalar → Fark Yaratan Detay → Kanıt → CTA | `product_video.mp4` |

Her anlatı formatı kendi bölüm başlıklarını videoya işler ve ayrı MP4 çıktısı üretir. Bölüm seçimi kaynak transkriptin zaman damgalarına dayanır. Model eksik veya geçersiz bölüm döndürürse transkript tabanlı güvenli yedek akış devreye girer.

**İçerik doğruluğu:** Sistem kaynakta bulunmayan ürün özelliği, fiyat, müşteri yorumu, sertifika, garanti, tarih, alıntı veya kanıtı uydurmamalıdır. Özellikle Ürün Tanıtımı modu yalnızca kaynakta desteklenen iddiaları kullanır.

## Güncel uygulama ekranları

Aşağıdaki görseller yerel uygulamanın güncel arayüzünden alınmıştır.

| Masaüstü | Mobil / kompakt görünüm |
|:---:|:---:|
| <img src="docs/assets/screenshot-live-desktop.png" alt="YAMAN VIRAL STUDIO PRO masaüstü ekranı" width="100%"> | <img src="docs/assets/screenshot-live-mobile.png" alt="YAMAN VIRAL STUDIO PRO mobil ekranı" width="78%"> |

## Ürün demosu

- [20 saniyelik stüdyo tanıtım videosu](docs/assets/showcase-demo.mp4)
- [Animasyonlu arayüz önizlemesi](docs/assets/showcase-demo.gif)
- [Uçtan uca Shorts üretim videosu](docs/assets/demo-output-youtube-shorts.mp4)
- [Örnek kaynak video](docs/assets/demo-input.mp4)
- [Zaman damgalı altyazı dosyası](docs/assets/demo-transcript.srt)
- [Demo raporu](docs/DEMO.md)

> Demo medya dosyaları test amaçlı sentetik içeriktir; gerçek kişi veya üçüncü taraf video kaydı değildir.

## Öne çıkan yetenekler

- **Video içe aktarma:** Yerel video dosyaları ve desteklenen YouTube kaynakları.
- **Konuşma tanıma:** Faster-Whisper ile zaman damgalı transkripsiyon; TXT/SRT iş akışları.
- **Yerel AI:** Ollama üzerinden yerel model entegrasyonu ve yapılandırılabilir model seçimi.
- **Akıllı kesit keşfi:** Hook, bağlam, konuşma yoğunluğu ve izlenebilirlik sinyallerine göre klip adayları.
- **Çok formatlı render:** Dikey video, altyazı, bölüm başlıkları, giriş/kapanış ve ayrı MP4 çıktıları.
- **Uzman AI ajanları:** Strateji, hook, kurgu, SEO, risk kontrolü, erişilebilirlik ve yerelleştirme görevleri.
- **Görev yönetimi:** SQLite tabanlı görev geçmişi, olay günlüğü, iptal, yeniden deneme ve kurtarma.
- **Platform hazırlığı:** YouTube, TikTok ve Instagram için kullanıcı onaylı yayın hazırlığı.
- **Sistem izleme:** GPU, CPU, RAM ve VRAM metrikleri.
- **Responsive arayüz:** Masaüstü ve mobil ekranlara uyumlu web arayüzü; PWA kurulumu.
- **Çok dilli arayüz:** Türkçe, İngilizce, Almanca ve İspanyolca.

## Autopilot — zamanlanmış yerel üretim

Autopilot, seçilen yayın takviminde Windows İndirilenler klasörüne eklenen yeni videoları tarar; videoyu Whisper ile çözümler, yerel AI ile kesitleri sıralar ve en iyi üç kesiti YouTube Shorts, Instagram Reels ve TikTok için render eder. Üretilen MP4 dosyaları Video Kütüphanesi'nde ve proje klasöründe saklanır.

- Günlük veya haftalık çalışma saati ve Europe/Istanbul saat dilimi.
- Kanal nişi, konuşma dili, kesit adedi ve hedef klip süresi ayarları.
- Platform başına ayrı çıktı; zamanlama duraklatma, yeniden etkinleştirme ve manuel çalıştırma.
- Kalıcı SQLite otomasyon ve çalışma kayıtları; uygulama yeniden başladığında planlar korunur.
- **Güvenlik:** Sosyal medya paylaşımı otomatik yapılmaz. Her çıktı kullanıcı incelemesi ve açık yayın onayı bekler.
- **Çalışma koşulu:** Zamanlayıcı yerel uygulama çalışırken ve bilgisayar açıkken işler.

Bu sürüm mevcut videoları yeniden kullanır. Konu trendi keşfi, sıfırdan metinden video/ses üretimi, ses klonlama ve otomatik platform gönderimi henüz bu yerel Autopilot kapsamına dahil değildir.

## Mimari

<img src="docs/assets/architecture.svg" alt="YAMAN VIRAL STUDIO PRO mimarisi" width="100%">

| Katman | Teknoloji |
|---|---|
| API ve uygulama | Python 3.12, FastAPI |
| Web arayüzü | HTML, CSS, JavaScript |
| Yerel LLM | Ollama |
| Konuşma tanıma | Faster-Whisper |
| Video / ses işleme | FFmpeg |
| Görev geçmişi | SQLite |
| PWA | Web App Manifest, Service Worker |

## Windows kurulumu

### Gereksinimler

- Windows 10/11
- Python 3.12 önerilir
- FFmpeg (PATH içinde erişilebilir olmalı)
- Ollama (yerel AI özellikleri için)
- Faster-Whisper modelleri ilk kullanımda indirilebilir

### Başlatma

1. Depoyu klonla:

   ```powershell
   git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
   cd YAMAN-VIRAL-STUDIO-PRO
   ```

2. Bağımlılıkları yükle:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Örnek ortam dosyasını incele ve yerel ayarlarını yapılandır:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Uygulamayı başlat:

   ```powershell
   .\run_windows.bat
   ```

5. Tarayıcıda aç: **http://127.0.0.1:8765**

> Yerel Ollama servisi ve Whisper modelleri ilk kullanımda model indirebilir. Bu ilk indirme tamamlandıktan sonra yapılandırılmış yerel iş akışları internet bağlantısı olmadan çalıştırılabilir; OAuth ve platform yayınlama gibi çevrimiçi entegrasyonlar istisnadır.

## PWA kurulumu

Uygulama HTTPS veya localhost üzerinden desteklenen tarayıcılara yüklenebilir.

1. Masaüstünde Chrome/Edge menüsünden **Uygulamayı yükle** seçeneğini kullan.
2. iPhone/iPad'de Safari → Paylaş → **Ana Ekrana Ekle** yolunu izle.
3. PWA önbelleği yalnızca uygulama kabuğunu tutar. Video analizi, AI, yükleme ve API işlemleri için yerel sunucu çalışır durumda olmalıdır.
4. Windows başlatıcısı güvenlik amacıyla varsayılan olarak yalnızca `127.0.0.1` adresinde dinler; LAN erişimi otomatik açılmaz.

## Güvenlik ve gizlilik

- AI ve video işleme bileşenleri yerel servislerle çalışacak şekilde tasarlanmıştır.
- OAuth sırları ve erişim tokenları şifreli kasada saklanır.
- `.env`, `.oauth.key`, token kasası, `settings.local.json` ve özel çalışma alanı verileri Git'e eklenmemelidir.
- OAuth üzerinden yayınlama kullanıcı onayı gerektirir. Platformların geliştirici incelemesi ve yayın politikaları geçerlidir.
- Yalnızca kullanma ve yeniden yayınlama hakkına sahip olduğun içerikleri içe aktar.

## Proje yapısı

```text
app/                 FastAPI uygulaması, AI ve video iş mantığı
web/                 Web arayüzü, stiller ve istemci kodu
docs/                Mimari, entegrasyon, demo ve görsel dokümantasyon
docs/assets/         Ürün görselleri, ekran görüntüleri ve demo medyası
workspace/           Yerel çalışma alanı ve üretim çıktıları
.github/workflows/   CI iş akışları
run_windows.bat      Windows başlatıcısı
requirements.txt     Python bağımlılıkları
```

## Geliştirme ve katkı

- [Katkı rehberi](CONTRIBUTING.md)
- [Güvenlik politikası](SECURITY.md)
- [Mimari notları](docs/ARCHITECTURE.md)
- [Platform entegrasyonları](docs/PLATFORM-INTEGRATIONS.md)
- [AI ajanları araştırması](docs/AI-AGENTS-RESEARCH.md)
- [Sürüm geçmişi](CHANGELOG.md)
- [Hata bildir](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/issues/new?template=bug_report.yml)
- [Özellik öner](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/issues/new?template=feature_request.yml)

## Lisanslama

Community Edition kaynak kodu [MIT Lisansı](LICENSE) kapsamındadır. Ayrı ticari modüller ve kurumsal lisans sınırları için [LICENSING.md](LICENSING.md) ve [ticari lisans taslağını](LICENSE-COMMERCIAL-TEMPLATE.md) incele.

---

<div align="center">

**YAMAN VIRAL STUDIO PRO** · [GitHub](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO)

</div>
