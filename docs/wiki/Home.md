# YAMAN VIRAL STUDIO PRO Wiki

YAMAN VIRAL STUDIO PRO, Windows üzerinde çalışan yerel öncelikli bir AI video içerik üretim stüdyosudur. Uzun videoları analiz ederek YouTube Shorts, Instagram Reels ve TikTok için kısa dikey içerikler hazırlamaya yardımcı olur.

**Ürün sürümü:** README'de tanımlanan v1.8.0  
**Çalışma adresi:** http://127.0.0.1:8765  
**Varsayılan yaklaşım:** Yerel işleme, kullanıcı kontrollü dışa aktarma ve yayınlama.

## Dokümantasyon

- [Installation Guide](Installation) — Windows kurulumu ve ilk çalıştırma
- [System Requirements](System-Requirements) — Donanım ve yazılım gereksinimleri
- [Architecture](Architecture) — Uygulama bileşenleri ve veri akışı
- [AI Engine](AI-Engine) — Ollama ve Faster-Whisper yapılandırması
- [Video Production](Video-Production) — İçerik üretim hattı
- [Troubleshooting](Troubleshooting) — Yaygın sorunlar ve çözümler

## Üretim hattı

1. Kaynak videoyu çalışma alanına alın.
2. Faster-Whisper ile konuşmayı zaman damgalı metne dönüştürün.
3. Ollama ile içerik ve klip adaylarını analiz edin.
4. Klipleri düzenleyin, altyazı ve dikey kadrajı hazırlayın.
5. FFmpeg ile MP4 çıktısı oluşturun.
6. Çıktıyı inceleyin ve hedef platforma manuel olarak yükleyin.

## Önemli not

Bu Wiki, depodaki README, requirements.txt, .env.example, başlatıcı ve mimari dokümanından doğrulanabilen bilgileri temel alır. Mimari dokümanında geçen bazı gelişmiş bileşenler hedeflenen/genişletilebilir mimariyi anlatabilir; her bileşenin mevcut sürümde etkin olduğu varsayılmamalıdır.

---
**YAMAN SOFTWARE · Built for Creators**
