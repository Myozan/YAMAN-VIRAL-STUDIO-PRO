<div align="center">

<img src="docs/assets/hero.svg" alt="YAMAN VIRAL STUDIO PRO" width="100%">

# YAMAN VIRAL STUDIO PRO

**Local-first AI video production studio**

[![Version](https://img.shields.io/badge/version-1.3.0-6478ff?style=for-the-badge)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge)](LICENSE)
[![Language](https://img.shields.io/badge/Interface-Turkish-ef4444?style=for-the-badge)](#language--dil)

**Designed & developed by [Ozan Yaman](https://github.com/Myozan)**

[TR T?rk?e](#t?rk?e) ? [EN English](#english) ? [Changelog](CHANGELOG.md)

</div>

---

## T?rk?e

YAMAN VIRAL STUDIO PRO; uzun videolar? yerel bilgisayarda analiz eden, konu?malar? metne d?n??t?ren, k?sa video kesitleri se?en, videodan ak?ll? ?zet haz?rlayan ve YouTube Shorts, Instagram Reels ve TikTok i?in d??a aktarma yapan yerel ?ncelikli bir i?erik ?retim st?dyosudur.

### Ekran g?r?nt?leri

<div align="center">

| Studio | ?zellik haritas? |
|:--:|:--:|
| <img src="docs/assets/screenshot-studio.png" alt="Studio paneli" width="100%"> | <img src="docs/assets/feature-map.svg" alt="?zellik haritas?" width="100%"> |

</div>

### v1.3.0 ?zellikleri

- **Video analizi:** YouTube ba?lant?s? veya Windows Downloads klas?r?nden yerel video tarama.
- **Transkripsiyon:** Faster-Whisper ile zaman damgal? konu?ma metni ve TXT d??a aktarma.
- **Ak?ll? kesit:** Konu?ma yo?unlu?u d???k veya k?sa videolarda daha esnek aday ?retimi ve yedek kesit mant???.
- **Ak?ll? ?zet videosu:** Transkriptteki ?nemli anlar? se?erek dikey MP4, altyaz?, giri? ve kapan?? olu?turma.
- **12 uzman AI ajan?:** Viral strateji, hook, kurgu, SEO, risk kontrol?, altyaz? QA, klip QA, yay?n haz?rl???, izleyici tutma, kapak/g?rsel, yerelle?tirme ve eri?ilebilirlik.
- **Platform profilleri:** YouTube Shorts, Instagram Reels ve TikTok i?in oran, ??z?n?rl?k ve azami s?re ayarlar?. Bu profiller ger?ek render i?leminde kullan?l?r.
- **Sistem izleme:** CPU, GPU, RAM, VRAM, i?lemci modeli, ?ekirdek/thread, saat h?z? ve desteklenen sens?rlerden s?cakl?k.
- **Mobil uyumlu aray?z:** Dar ekranlarda kayd?r?labilir men?, iki s?tunlu g?stergeler ve esnek kartlar.
- **Yerel AI:** Ollama ?zerinden yerel model; video ve ses i?leme yerel ?al??ma alan?nda yap?l?r.

### Mimari

<img src="docs/assets/architecture.svg" alt="YAMAN Viral Studio mimarisi" width="100%">

| Katman | Teknoloji |
|---|---|
| API | Python 3.12, FastAPI, Uvicorn |
| AI | Ollama, Qwen uyumlu yerel modeller |
| Speech-to-text | Faster-Whisper |
| Video | FFmpeg / FFprobe, yt-dlp |
| Aray?z | HTML, CSS, JavaScript |
| Kal?c? i? verisi | Yerel JSON proje kay?tlar? ve SQLite ??renme verisi |

### Kurulum (Windows)

1. Python 3.12 ve FFmpeg/FFprobe kurun.
2. Ollama'y? ba?lat?n ve qwen3:1.7b modelini indirin.
3. Proje klas?r?nde run_windows.bat dosyas?n? ?al??t?r?n veya a?a??daki komutlar? kullan?n:

    .venv\Scriptsctivate
    pip install -r requirements.txt
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8765

4. Taray?c?dan http://127.0.0.1:8765 adresini a??n.

### Platform hesaplar? hakk?nda

Platform profilleri video d??a aktarma ayarlar?n? y?netir. TikTok/Instagram/YouTube hesaplar?na otomatik y?kleme bu s?r?mde etkin de?ildir; ger?ek yay?n i?in resmi geli?tirici uygulamalar?, OAuth izinleri ve kullan?c? onay? gerekir. Uygulama bu ba?lant?lar?n kurulu oldu?unu iddia etmez.

### Donan?m telemetrisi

GPU s?cakl??? NVIDIA s?r?c?s? ve nvidia-smi ?zerinden okunur. CPU s?cakl???, donan?m sens?r sa?lay?c?s? (LibreHardwareMonitor veya OpenHardwareMonitor) eri?ilebilir oldu?unda g?sterilir; sens?r yoksa N/A g?sterilir. CPU model/?ekirdek/thread ve kullan?m verileri ayr? olarak al?n?r.

### G?venlik ve veri

- settings.local.json, platform_profiles.json, .env, ?al??ma alan? videolar? ve g?nl?kler Git'e eklenmez.
- Yaln?zca sahibi oldu?unuz veya i?leme/yay?nlama hakk?n?z bulunan i?erikleri kullan?n.
- Otomatik sosyal medya y?klemesi veya DRM a?ma i?levi bulunmaz.

## English

YAMAN VIRAL STUDIO PRO is a local-first video workflow for transcription, short-clip selection, AI-generated video summaries and platform-ready exports. It runs with FastAPI, Ollama, Faster-Whisper and FFmpeg on the user's own computer.

### Version 1.3.0 highlights

- YouTube URL and local Downloads video ingestion.
- Timestamped Whisper transcript with TXT export.
- More tolerant short/sparse-speech clip candidate generation.
- AI summary MP4 with selected moments, captions, intro and outro.
- Twelve specialist agents with structured per-agent reports.
- Editable YouTube Shorts, Instagram Reels and TikTok export profiles.
- CPU/GPU/RAM/VRAM telemetry and responsive mobile layout.

### Important limitations

Platform profiles configure exported files; direct account publishing is not enabled. CPU temperature requires a supported hardware-monitor sensor provider. The application does not bypass DRM or upload content without configured official platform authorization.

---

## License

This project is released under the MIT License. See LICENSE.
