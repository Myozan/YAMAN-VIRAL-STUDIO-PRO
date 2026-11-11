# Architecture

> This page describes the verified v1.8.0 runtime. The expanded design in the repository's `docs/ARCHITECTURE.md` is a future-state target, not a shipped component list. See [Engineering Architecture](Engineering-Architecture), [Workflow Sequences](Workflow-Sequences) and [Database ERD](Database-ERD).

YAMAN VIRAL STUDIO PRO, yerel öncelikli bir video üretim uygulaması olarak tasarlanmıştır. Bu sayfa, depodaki mimari tanımı ile mevcut kurulum dosyalarının doğruladığı teknolojileri birbirinden ayırır.

## High-level overview

    Browser / PWA
         |
         v
    FastAPI application (127.0.0.1:8765)
         |
         +--> Content & workflow orchestration
         +--> Ollama (127.0.0.1:11434) [optional local LLM]
         +--> Faster-Whisper [speech-to-text]
         +--> FFmpeg / FFprobe [media processing]
         +--> Local workspace [media, settings, generated assets]

## Teknoloji katmanları

| Katman | Teknoloji / sorumluluk |
|---|---|
| API | Python 3.12, FastAPI, Uvicorn |
| UI | HTML, CSS, JavaScript ve PWA varlıkları |
| LLM | Ollama; yerel model sağlayıcısı |
| Speech-to-text | Faster-Whisper |
| Media | FFmpeg, FFprobe; isteğe bağlı Auto-Editor |
| Download | yt-dlp; yalnızca kullanım ve platform koşullarına uygun kaynaklar |
| Persistence | Yerel çalışma alanı; mimari tasarım dokümanında SQLite/PostgreSQL seçenekleri |

## Media production flow

1. **Intake:** Kaynak medya ve üretim hedefleri belirlenir.
2. **Transcription:** Faster-Whisper konuşmayı zaman damgalı metne dönüştürür.
3. **Analysis:** Ollama yapılandırmaya göre içerik ve klip önerileri üretir.
4. **Editing:** Klip sınırları, altyazı, kadraj ve çıktı formatı hazırlanır.
5. **Rendering:** FFmpeg video ve ses işlemlerini gerçekleştirir.
6. **Review & export:** Kullanıcı çıktıyı inceler ve dışa aktarır.

## Existing implementation vs. extended architecture

Depodaki docs/ARCHITECTURE.md daha geniş bir mimariyi de tanımlar: LangGraph tabanlı workflow, PostgreSQL, Redis, platform adaptörleri, yayınlama onayı ve analitik bileşenleri.

Bunlar mimari dokümanda tanımlanmış tasarım bileşenleridir. Mevcut requirements.txt içinde LangGraph, PostgreSQL istemcisi veya Redis bağımlılığı bulunmadığından, bu bileşenlerin tamamının mevcut kurulumda etkin olduğu varsayılmamalıdır. İlgili modüller ayrıca doğrulanmalıdır.

## Security boundaries

- Geliştirme sunucusunu varsayılan olarak loopback arayüzüne bağlayın.
- API anahtarlarını, OAuth sırlarını ve token'ları kaynak kodda saklamayın.
- Kullanıcı onayı olmadan sosyal platformlarda yayın yapmayın.
- LLM çıktısını güvenilir komut veya kod olarak çalıştırmayın.
- Kaynak medya için telif, kullanım hakkı ve platform koşullarını gözetin.
- Harici ağ erişimi açılacaksa kimlik doğrulama ve güvenlik katmanlarını önce tamamlayın.

## Related documentation

- [Installation Guide](Installation)
- [System Requirements](System-Requirements)
- [AI Engine](AI-Engine)
- [Video Production](Video-Production)
