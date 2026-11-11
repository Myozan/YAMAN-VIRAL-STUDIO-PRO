# YAMAN VIRAL STUDIO PRO

<div align="center">

<img src="docs/assets/hero-v1.8.0.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 Premium AI Creator Studio" width="100%">

**YEREL AI VIDEO ÜRETİM STÜDYOSU · WINDOWS · PWA**

[![Sürüm](https://img.shields.io/badge/Sürüm-1.8.0-8b78f6?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-Kurulabilir-5B8DEF?style=for-the-badge)](#kurulum)
[![Lisans](https://img.shields.io/badge/Lisans-MIT-2ea44f?style=for-the-badge)](LICENSE)

[Türkçe](README.md) · [English](README.en.md) · [Deutsch](README.de.md) · [Español](README.es.md)

**Tek bir uzun videodan, tüm dikey platformlara hazır içerik üretin.**

[Hızlı başlangıç](#hızlı-başlangıç) · [Özellikler](#creator-studio-araçları) · [Ekranlar](#stüdyonun-içinden) · [Mimari](#mimari) · [Lisans](#lisans)

</div>

---

## ✦ YAMAN VIRAL STUDIO PRO nedir?

YAMAN VIRAL STUDIO PRO, uzun videoları analiz edip düzenlenmiş ve platformlara hazır kısa videolara dönüştürmek için tasarlanmış **yerel öncelikli bir AI Creator Studio** uygulamasıdır.

Kaynak videoyu içe aktarın. **Whisper** ile konuşmayı zaman damgalı metne dönüştürün, **Ollama** ile güçlü anları keşfedip içerik akışını oluşturun, **FFmpeg** ile kesin, altyazı ekleyin ve dışa aktarın. YouTube Shorts, Instagram Reels ve TikTok için dikey çıktılar hazırlayın.

> **Videolarınız varsayılan olarak bilgisayarınızda kalır. Üretim sürecinin kontrolü sizdedir.**

## ⚡ Hızlı başlangıç

**Windows 10/11 · Python 3.12 · FFmpeg**

```powershell
git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
cd YAMAN-VIRAL-STUDIO-PRO
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
.\run_windows.bat
```

Tarayıcıdan **http://127.0.0.1:8765** adresini açın.

Yerel içerik zekâsı için [Ollama](https://ollama.com/download/windows) kurun ve donanımınıza uygun bir model indirin. Whisper modelleri ilk kullanımda indirilebilir.

## 🎬 Creator Studio araçları

| İş akışı | Ne yapar? |
|---|---|
| **Whisper transkripsiyon** | Konuşmayı zaman damgalı metne dönüştürür. |
| **Ollama içerik zekâsı** | Kaynağı analiz eder, senaryo taslağı hazırlar ve klip adaylarını sıralar. |
| **Smart Recap** | Önemli anları seçerek kısa bir video özeti oluşturur. |
| **Story Flow** | Açılıştan sonuca kadar anlatı akışı kurar. |
| **Documentary** | Kronolojik ve kaynakla desteklenen bir hikâye oluşturur. |
| **Education** | Kavramları, adımları, örnekleri ve öğrenme özetini düzenler. |
| **Product video** | Dayanağı olmayan iddialar üretmeden ürün videosu akışı hazırlar. |
| **FFmpeg render** | Videoyu keser, altyazı ekler ve dikey MP4 olarak dışa aktarır. |
| **Autopilot** | Planlı, yerel öncelikli içerik akışlarını çalıştırır. |
| **Medya kütüphanesi** | Kaynak videoları, klipleri ve çıktıları yönetir. |

### Tek üretim hattı. Birden fazla platform.

<p align="center"><img src="docs/assets/pipeline.svg" alt="Whisper, Ollama ve FFmpeg üretim hattı" width="100%"></p>
<p align="center"><img src="docs/assets/video-formats.svg" alt="Beş farklı video anlatım formatı" width="100%"></p>

## 🖥️ Stüdyonun içinden

**MASAÜSTÜ ÇALIŞMA ALANI**

<p align="center"><img src="docs/assets/screenshot-live-desktop-framed.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 masaüstü arayüzü" width="100%"></p>

**MOBİL ÇALIŞMA ALANI**

<p align="center"><img src="docs/assets/screenshot-live-mobile-framed.png" alt="YAMAN VIRAL STUDIO PRO v1.8.0 gerçek mobil görünümü, 390 piksel viewport" width="390"></p>

Arayüz; daraltılabilir ikon menüsü, mobil açılır navigasyon, hızlı tema değiştirme ve üretim hattını öne çıkaran ana sayfa içerir.

## 🧩 Mimari

<p align="center"><img src="docs/assets/architecture.svg" alt="YAMAN VIRAL STUDIO PRO yazılım mimarisi" width="100%"></p>

| Katman | Teknoloji |
|---|---|
| API ve uygulama | Python 3.12 · FastAPI |
| Web arayüzü | HTML · CSS · JavaScript |
| Yerel dil modeli | Ollama |
| Konuşma tanıma | Faster-Whisper |
| Video ve ses | FFmpeg · isteğe bağlı Auto-Editor |
| Görev geçmişi | SQLite |
| Kurulabilir uygulama | Web App Manifest · Service Worker |

## 🔐 Yerel öncelikli tasarım

- Transkripsiyon, analiz ve medya işleme; modeller ve bağımlılıklar kurulduktan sonra yerel olarak çalışabilir.
- Runway, Pexels, Edge TTS ve trend araştırması gibi isteğe bağlı servisler internet bağlantısı gerektirir.
- Servis erişim anahtarları ve token'lar yerel şifreli kasada tutulmalıdır.
- Yayınlama işlemleri kullanıcı onayı gerektirir.
- Yalnızca kullanım ve yayınlama hakkına sahip olduğunuz medyaları içe aktarın.

## ♻️ Kurulu sürümler için güncelleme

Uygulama, yapılandırılmış GitHub güncelleme dalını kontrol edebilir ve daha yeni bir commit bulunduğunda **kullanıcı onaylı güncelleme bildirimi** gösterebilir. Uygulama dosyaları değiştirilmeden önce yedek alınır; yerel çalışma alanı, ayarlar, kimlik bilgileri ve medya dosyaları korunacak şekilde tasarlanmıştır.

Güncellemeler sessizce kurulmaz. Sürüm bilgisini inceleyin ve yüklemeyi onaylayın.

## 📦 Proje yapısı

```text
app/                 FastAPI uygulaması, AI ve medya iş mantığı
web/                 Creator Studio arayüzü ve PWA varlıkları
docs/                Mimari, entegrasyon ve dokümantasyon
docs/assets/         Ürün görselleri ve ekran görüntüleri
tools/               Yerel bakım ve güncelleme araçları
workspace/           Yerel veritabanı, ayarlar ve üretilen medya
.github/workflows/   CI iş akışları
run_windows.bat      Windows başlatıcısı
requirements.txt     Python bağımlılıkları
```

## 🛠️ Sorun giderme

- **Ollama algılanmıyor:** Yerel servisi başlatın, `ollama list` komutunu çalıştırın ve Studio → Ayarlar bölümünden bağlantıyı kontrol edin.
- **FFmpeg bulunamıyor:** FFmpeg ve FFprobe kurup çalıştırılabilir dosya klasörünü PATH değişkenine ekleyin.
- **İlk açılış uzun sürüyor:** Whisper ve Ollama modelleri ilk kullanımda indirilebilir.
- **Güncelleme kontrolü başarısız:** İnternet bağlantısını ve GitHub API erişimini kontrol edin. Kontrol başarısız olsa da mevcut kurulum kullanılabilir.

## 📚 Dokümantasyon

- [GitHub Wiki](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/wiki) · [Wiki kaynak dosyaları](docs/wiki/Home.md)
- [Kurulum ve hızlı başlangıç](docs/wiki/Installation.md)
- [Mevcut sürüm mimarisi ve diyagramlar](docs/ENGINEERING-ARCHITECTURE.md)
- [Veritabanı ERD](docs/DATABASE-ERD.md)
- [İş akışı sequence diyagramları](docs/WORKFLOW-SEQUENCES.md)
- [Test stratejisi](docs/TESTING-STRATEGY.md)
- [Operasyon ve kurtarma rehberi](docs/OPERATIONS-RUNBOOK.md)
- [Gelecek mimari hedefi](docs/ARCHITECTURE.md)
- [API Reference](docs/wiki/API-Reference.md)
- [AI Agent System](docs/wiki/Agent-System.md)
- [Autopilot](docs/wiki/Autopilot.md)
- [Database Schema](docs/wiki/Database-Schema.md)
- [Security](docs/wiki/Security.md)
- [Deployment](docs/wiki/Deployment.md)
- [Developer Guide](docs/wiki/Developer-Guide.md)
- [Sürüm geçmişi](CHANGELOG.md)
- [Platform entegrasyonları](docs/PLATFORM-INTEGRATIONS.md)
- [Katkıda bulunma](CONTRIBUTING.md)
- [Güvenlik politikası](SECURITY.md)
- [Lisanslama rehberi](LICENSING.md)

## 🤝 Katkıda bulunun

Hata bildirimleri, öneriler ve pull request'ler memnuniyetle karşılanır. Katkıdan önce [katkı rehberini](CONTRIBUTING.md) ve [güvenlik politikasını](SECURITY.md) inceleyin.

## ⚖️ Lisans

Kök dizindeki [MIT Lisansı](LICENSE) kapsamındaki Community Edition kaynak dosyaları MIT koşullarıyla dağıtılır. Üçüncü taraf bağımlılıkları ve servisler kendi lisans koşullarına tabidir. Ayrıntılar için [LICENSING.md](LICENSING.md) dosyasına bakın.

---

<div align="center">

**YAMAN VIRAL STUDIO PRO · v1.8.0**

*Yerelde üretin. Akıllıca düzenleyin. Her yerde yayınlayın.*

[GitHub deposu](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO) · [Sürümler](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/releases) · [Sorunlar](https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO/issues)

</div>
