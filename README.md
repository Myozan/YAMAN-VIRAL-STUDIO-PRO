<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO" width="100%">

# YAMAN VIRAL STUDIO PRO

**Yerel öncelikli yapay zekâ video üretim stüdyosu**

[TR Türkçe](README.md) | [EN English](README.en.md) | [DE Deutsch](README.de.md) | [ES Español](README.es.md) | [Sürüm geçmişi](CHANGELOG.md)

[![Version](https://img.shields.io/badge/version-1.4.0-6478ff?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)

**Geliştirici: [Ozan Yaman](https://github.com/Myozan)**

</div>

---

## Proje hakkında

YAMAN VIRAL STUDIO PRO; videoları yerel bilgisayarda analiz eden, konuşmaları zaman damgalı metne dönüştüren, kısa video kesitleri seçen, akıllı özet videosu oluşturan ve YouTube Shorts, Instagram Reels ile TikTok için dışa aktarma sağlayan yerel öncelikli bir üretim stüdyosudur.

## 1.4.0 özellikleri

- **Video analizi:** YouTube bağlantısı veya Windows Downloads klasöründen yerel video içe aktarma.
- **Transkripsiyon:** Faster-Whisper ile zaman damgalı konuşma metni ve TXT dışa aktarma.
- **Akıllı kesit:** Kısa ve az konuşmalı videolar için esnek kesit adayı ve yedek seçim.
- **Akıllı özet videosu:** Önemli anları seçerek dikey MP4, altyazı, giriş ve kapanış üretme.
- **12 uzman AI ajanı:** Viral strateji, hook, kurgu, SEO, risk kontrolü, altyazı QA, klip QA, yayın hazırlığı, izleyici tutma, kapak/görsel, yerelleştirme ve erişilebilirlik.
- **Kalıcı ajan orkestrasyonu:** SQLite görev geçmişi, olay günlüğü, iptal, yeniden deneme ve uygulama yeniden başladığında kesintiye uğrayan görevleri kurtarma.
- **Çok dilli arayüz:** Türkçe / İngilizce dil seçimi.
- **OAuth hesap bağlantısı:** YouTube, TikTok ve Instagram için resmî OAuth akışları; kimlik bilgileri ve erişim tokenları yerel olarak şifrelenir.
- **Kullanıcı onaylı yayın:** Her yükleme açık kullanıcı onayı ister. YouTube ve TikTok yerel MP4 dosyasını yükleyebilir. Instagram Reels için herkese açık HTTPS video adresi gerekir.
- **Platform profilleri:** 9:16, 1:1, 16:9; 720p/1080p ve azami süre ayarları.
- **Sistem izleme:** GPU, CPU, RAM ve VRAM kullanım göstergeleri. CPU kartında yalnızca işlemci modeli ve işlemci kullanımı gösterilir.
- **Mobil uyumlu arayüz:** Küçük ekranlarda kaydırılabilir menü, esnek kartlar ve uyarlanabilir göstergeler.

## Mimari

| Katman | Teknoloji |
|---|---|
| API | Python 3.12, FastAPI, Uvicorn |
| Yerel AI | Ollama, Qwen |
| Konuşma tanıma | Faster-Whisper |
| Video | FFmpeg / FFprobe, yt-dlp |
| Arayüz | HTML, CSS, JavaScript |
| Görev geçmişi | SQLite |
| OAuth gizli verileri | Fernet şifreleme |

## Windows kurulumu

1. Python 3.12, FFmpeg ve Ollama kurun.
2. Yerel modeli indirin: ollama pull qwen3:1.7b
3. Proje klasöründe run_windows.bat dosyasını çalıştırın.
4. Tarayıcıdan http://127.0.0.1:8765 adresini açın.

Bağımlılıkları elle kurmak için:

    .venv\Scripts\activate
    pip install -r requirements.txt

## OAuth ve otomatik yayınlama kurulumu

Platform Profilleri sayfasında her sağlayıcı için geliştirici uygulaması kimlik bilgilerini kaydedin. Bu bilgiler uygulama tarafından yerel diskte şifrelenir.

| Platform | Geliştirici değişkenleri | Gerekli izin |
|---|---|---|
| YouTube | YAMAN_GOOGLE_CLIENT_ID / YAMAN_GOOGLE_CLIENT_SECRET | youtube.upload |
| TikTok | YAMAN_TIKTOK_CLIENT_KEY / YAMAN_TIKTOK_CLIENT_SECRET | video.publish |
| Instagram | YAMAN_META_APP_ID / YAMAN_META_APP_SECRET | instagram_basic, instagram_content_publish, pages_show_list |

Platform Profilleri ekranında gösterilen OAuth Callback adresini ilgili geliştirici konsoluna birebir ekleyin. İsteğe bağlı olarak YAMAN_PUBLIC_BASE_URL tanımlayabilirsiniz.

- YouTube yüklemeleri varsayılan olarak **private** gizlilik düzeyinde başlar.
- TikTok Direct Post için Content Posting API ve onaylı video.publish izni gerekir. Denetlenmemiş uygulamalar yalnızca özel gönderi oluşturabilir.
- Instagram Reels için profesyonel hesap, Facebook Sayfası bağlantısı ve Meta tarafından erişilebilen herkese açık HTTPS video adresi gerekir.
- Yayınlama düğmesi her seferinde kullanıcı onayı ister; sessiz veya arka planda otomatik paylaşım yapılmaz.

## Güvenlik

- OAuth istemci sırları ve tokenlar şifreli yerel dosyalarda tutulur.
- .oauth.key, OAuth token kasası, uygulama kimlik bilgileri, yerel ayarlar ve workspace Git'e eklenmez.
- OAuth anahtar dosyasını yedekleyin; kaybolursa kayıtlı tokenları çözmek mümkün olmaz.
- Yalnızca sahibi olduğunuz veya dağıtım hakkına sahip olduğunuz içerikleri yayınlayın.

## Sınırlamalar

- Instagram Graph API yerel localhost dosyasını çekemez; Reels için genel erişilebilir HTTPS medya URL'si gereklidir.
- TikTok'un denetlenmemiş geliştirici uygulamaları herkese açık yayın yapamaz.
- OAuth bağlantısı için her platformda kayıtlı geliştirici uygulaması, doğru callback adresi ve onaylı izinler gereklidir.

## Teknik araştırma

Ajan mimarisi ve platform entegrasyonu kararları için [AI Agent / OAuth araştırma notları](docs/AI-AGENTS-RESEARCH.md) dosyasına bakın.

## Lisans

MIT. Ayrıntılar için LICENSE dosyasına bakın.
