<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO — Yerel AI Video Stüdyosu" width="100%">

# YAMAN VIRAL STUDIO PRO

### Yerel yapay zekâ destekli video analiz, Shorts üretimi ve çok formatlı içerik stüdyosu

**v1.8.0 · Premium AI Creator Studio · Local-first AI · Windows · PWA**

[![Version](https://img.shields.io/badge/version-1.8.0-8b78f6?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

[ Türkçe ](README.md) · [ English ](README.en.md) · [ Deutsch ](README.de.md) · [ Español ](README.es.md)

</div>

---

## Genel bakış

**YAMAN VIRAL STUDIO PRO**, uzun videoları analiz eden, konuşmaları zaman damgalı metne dönüştüren, güçlü anları seçen ve YouTube Shorts, Instagram Reels ve TikTok için dikey videolar hazırlayan yerel öncelikli bir içerik stüdyosudur.

Ollama, Faster-Whisper ve FFmpeg tabanlı temel iş akışı bilgisayarınızda çalışır. İsteğe bağlı Runway, Pexels ve Edge TTS entegrasyonları çevrimiçi hizmet kullanır.

## Öne çıkan özellikler

- Yerel video ve desteklenen YouTube kaynaklarını içe aktarma.
- Faster-Whisper ile konuşma tanıma ve zaman damgalı transkripsiyon.
- Ollama ile yerel senaryo üretimi ve klip sıralama.
- Shorts, Reels ve TikTok için dikey MP4 render.
- Akıllı özet, hikâye, belgesel, eğitim ve ürün tanıtımı formatları.
- AI ajanları, görev geçmişi, Autopilot ve medya kütüphanesi.
- Runway AI ve Pexels ile isteğe bağlı sahne/B-roll üretimi.
- Video kütüphanesindeki MP4 dosyaları için isteğe bağlı Auto-Editor sessizlik temizleme.
- Ayarlar içinden Ollama bağlantı kontrolü ve başlatma.
- Windows video aktarımında istemci bağlantısı kesilmelerinin kontrollü yönetimi.
- Türkçe, İngilizce, Almanca ve İspanyolca arayüz; üç görünüm teması.
- v1.8.0 Premium AI Creator Studio: daraltılabilir ikon menüsü, tooltip navigasyonu, mor-mavi tasarım dili ve üst çubuktan hızlı tema değiştirme.

## v1.8.0 — Premium AI Creator Studio

Arayüz; profesyonel mor-mavi vurgu paleti, derin katmanlı paneller, cam efektli üst çubuk, yenilenmiş kartlar ve daha net tipografiyle güncellendi. Masaüstünde sol menü daraltılarak ikon moduna alınabilir; tercih tarayıcıda saklanır ve ikonların üzerine gelindiğinde araç ipuçları görünür. Üst çubuktaki tema düğmesi Gece, Okyanus ve Açık temalar arasında geçiş yapar. Ayarlar bölümündeki tema seçici korunmuştur. Video işleme, Ollama, Autopilot, medya kütüphanesi ve mevcut üretim akışları değiştirilmemiştir.

## v1.7.0 — Akıllı kurgu ve yerel motor güvenilirliği

### Auto-Editor

Video kütüphanesindeki MP4 kartlarına **Sessizlikleri temizle** eylemi eklendi. İşlem orijinal videoyu değiştirmez; _SILENCE_CUT.mp4 uzantılı ayrı bir çıktı oluşturur. Varsayılan eşik yüzde 6, kenar payı 0,3 saniyedir.

Auto-Editor CLI resmi Windows ikilisinden kurulmalıdır. CLI artık PyPI üzerinden yayımlanmıyor; pip ile kurulum önerilmez. [Resmî kurulum belgesi](https://auto-editor.com/installing) · [GitHub Releases](https://github.com/WyattBlue/auto-editor/releases)

Kurulumdan sonra PowerShell'de auto-editor --help komutuyla doğrulayın. Ardından uygulamayı yeniden başlatın.

### Ollama bağlantısı

- Ayarlar bölümünde bağlantıyı kontrol etme ve Ollama masaüstü uygulamasını başlatma.
- Model listesinin ve seçili modelin kullanılabilirliğinin kontrolü.
- Bağlantı yok, zaman aşımı ve API hataları için açıklayıcı hata mesajları.
- Windows'ta varsayılan Ollama API adresi: http://127.0.0.1:11434.

Ollama Windows uygulaması arka planda API sunar. [Ollama Windows belgeleri](https://docs.ollama.com/windows) · [API başlangıç kılavuzu](https://docs.ollama.com/api)

### Windows video aktarımı

Tarayıcı video aktarımını durdurduğunda veya bağlantıyı sıfırladığında görülebilen WinError 10054 Proactor callback olayı, yalnızca beklenen bağlantı kapanışı bağlamında filtrelenir. Diğer asyncio hataları normal şekilde loglanmaya devam eder. HTTP 206 Partial Content video Range istekleri için normal bir yanıttır; hata değildir.

## Kurulum

### Gereksinimler

- Windows 10/11
- Python 3.12
- FFmpeg ve FFprobe (PATH içinde)
- Ollama (yerel AI özellikleri için)
- Auto-Editor (isteğe bağlı sessizlik temizleme)
- Edge TTS (çevrimiçi seslendirme için)

### Adımlar

1. Depoyu klonlayın: git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
2. Proje klasörüne girin.
3. Sanal ortam oluşturun: py -3.12 -m venv .venv
4. Ortamı etkinleştirin: .venv\Scripts\Activate.ps1
5. Bağımlılıkları yükleyin: pip install -r requirements.txt
6. Ortam dosyasını kopyalayın: Copy-Item .env.example .env
7. Uygulamayı başlatın: .\run_windows.bat
8. Tarayıcıda http://127.0.0.1:8765 adresini açın.

### Ollama kurulumu ve sorun giderme

1. [Ollama for Windows](https://ollama.com/download) uygulamasını kurup açın.
2. PowerShell'de ollama list komutuyla kurulu modelleri kontrol edin.
3. Örnek model yoksa ollama pull qwen3:1.7b komutunu çalıştırın.
4. API kontrolü için Invoke-RestMethod http://127.0.0.1:11434/api/tags komutunu çalıştırın.
5. Studio > Ayarlar bölümünden **Bağlantıyı kontrol et** düğmesine basın.
6. Ollama kapalıysa aynı sayfadaki **Ollama'yı başlat** düğmesini kullanın.

Ollama bulunamazsa resmi kurulum sayfasından yükleyin.

## Mimari

| Katman | Teknoloji |
|---|---|
| API | Python 3.12, FastAPI |
| Web arayüzü | HTML, CSS, JavaScript |
| Yerel LLM | Ollama |
| Konuşma tanıma | Faster-Whisper |
| Video/ses işleme | FFmpeg, isteğe bağlı Auto-Editor |
| Görev geçmişi | SQLite |
| PWA | Web App Manifest, Service Worker |

## Gizlilik ve güvenlik

- Yerel AI ve video işleme, yerel servislerle çalışacak şekilde tasarlanmıştır.
- Runway, Pexels, Edge TTS ve trend araştırması internet bağlantısı kullanır.
- OAuth sırları ve sağlayıcı API anahtarları yerel şifreli kasada tutulur.
- Auto-Editor yeni çıktı üretir; kaynak MP4'ü üzerine yazmaz.
- Sosyal medya paylaşımı açık kullanıcı onayı gerektirir.
- Yalnızca kullanma ve yeniden yayınlama hakkına sahip olduğunuz içerikleri içe aktarın.

## Proje yapısı

- app/: FastAPI uygulaması, AI ve video iş mantığı
- web/: Web arayüzü, stiller ve istemci kodu
- docs/: Mimari, entegrasyon ve demo dokümantasyonu
- workspace/: Yerel çalışma alanı ve üretim çıktıları
- .github/workflows/: CI iş akışları
- run_windows.bat: Windows başlatıcısı
- requirements.txt: Python bağımlılıkları

## Belgeler

- [Katkı rehberi](CONTRIBUTING.md)
- [Güvenlik politikası](SECURITY.md)
- [Mimari notları](docs/ARCHITECTURE.md)
- [Platform entegrasyonları](docs/PLATFORM-INTEGRATIONS.md)
- [Sürüm geçmişi](CHANGELOG.md)

## Lisans

Community Edition kaynak kodu [MIT Lisansı](LICENSE) kapsamındadır. Ticari modüller için [LICENSING.md](LICENSING.md) dosyasına bakın.

---

<div align="center">

**YAMAN VIRAL STUDIO PRO** · [GitHub](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO)

</div>
