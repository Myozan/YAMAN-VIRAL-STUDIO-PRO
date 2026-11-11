# YAMAN VIRAL STUDIO PRO Wiki

YAMAN VIRAL STUDIO PRO, Windows üzerinde çalışan yerel öncelikli bir AI video içerik üretim stüdyosudur. Uzun videoları analiz ederek YouTube Shorts, Instagram Reels ve TikTok için kısa dikey içerikler hazırlamaya yardımcı olur.

**Ürün sürümü:** v1.8.0  
**Çalışma adresi:** http://127.0.0.1:8765  
**Varsayılan yaklaşım:** Yerel işleme, kullanıcı kontrollü dışa aktarma ve yayınlama.

## Product guides
- [Installation Guide](Installation)
- [System Requirements](System-Requirements)
- [Video Production](Video-Production)
- [Autopilot Guide](Autopilot)

## Engineering documentation
- [Architecture](Architecture)
- [API Reference](API-Reference)
- [Agent System](Agent-System)
- [Database Schema](Database-Schema)
- [Security & Privacy](Security)
- [Deployment Guide](Deployment)
- [Developer Guide](Developer-Guide)
- [Release Management](Release-Management)
- [AI Engine Configuration](AI-Engine)
- [Voice & Whisper](Voice-Engine)
- [Platform Integrations](Platform-Integrations)
- [FAQ](FAQ)
- [Troubleshooting](Troubleshooting)

## Core production pipeline
1. Kaynak videoyu çalışma alanına alın.
2. Faster-Whisper ile konuşmayı zaman damgalı metne dönüştürün.
3. Ollama ile içerik ve klip adaylarını analiz edin.
4. Klipleri düzenleyin, altyazı ve dikey kadrajı hazırlayın.
5. FFmpeg ile MP4 çıktısı oluşturun.
6. Çıktıyı inceleyin ve hedef platforma manuel olarak yükleyin veya desteklenen OAuth akışında açık onayla yayınlayın.

## Documentation accuracy
Bu Wiki, v1.8.0 kaynak kodundan doğrulanabilen özellikleri ve önerilen genişletmeleri ayırır. Mimari tasarımda bulunan ancak kurulumda etkin olmayan PostgreSQL, Redis, LangGraph ve çok kullanıcılı dağıtım bileşenleri mevcut ürün özelliği olarak değerlendirilmemelidir.

---
**YAMAN SOFTWARE · Built for Creators**
