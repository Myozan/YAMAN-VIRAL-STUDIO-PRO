# API Reference

Bu referans, v1.8.0 kaynak kodundaki FastAPI route tanımlarına göre hazırlanmıştır. En güncel şema, uygulama çalışırken **/docs** (Swagger UI) ve **/openapi.json** üzerinden alınabilir.

**Base URL:** http://127.0.0.1:8765  
**Content type:** JSON (dosya yükleme/indirme uçları hariç)  
**Authentication:** Mevcut yerel uygulamada genel bir kullanıcı oturum doğrulama katmanı belgelenmemiştir. Bu nedenle API'yi internete veya güvenilmeyen LAN'a açmayın.

## Health and local services

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/health | Uygulama, FFmpeg, Ollama ve platform durumu |
| GET | /api/system/metrics | CPU/RAM ve desteklenen sistemlerde GPU metrikleri |
| GET | /api/ollama/status | Ollama bağlantısı ve model listesi |
| POST | /api/ollama/start | Yerel Ollama servisini başlatmayı dener |
| GET | /api/auto-editor/status | Auto-Editor kullanılabilirliği |
| POST | /api/auto-editor/silence-remove | Workspace MP4 dosyasının sessizlik temizlenmiş kopyasını üretir |

## Analysis and rendering

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/analyze | YouTube URL'sini analiz kuyruğuna alır |
| GET | /api/local/videos | Yerel video seçeneklerini listeler |
| POST | /api/analyze/local | Yerel videoyu analiz kuyruğuna alır |
| GET | /api/jobs/{job_id} | Analiz işinin klip ve transkript bilgisi |
| POST | /api/render | Seçili klibi platform formatlarında render eder |
| POST | /api/summary/run | Akıllı özet veya yapılandırılmış video üretir |
| GET | /api/summary/{job_id} | Kaydedilmiş özet/iş bilgisi |

### Analyze request

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "clips": 8,
  "min_seconds": 20,
  "max_seconds": 55,
  "language": "auto"
}
```

Yerel analiz için `url` yerine `filename` alanını kullanan `/api/analyze/local` isteği gönderilir. Kesit sayısı 1–20, minimum süre 10–60 saniye, maksimum süre 20–180 saniye aralığındadır.

### Render request

```json
{
  "job_id": "JOB_ID",
  "clip_id": 1,
  "platforms": ["youtube", "instagram", "tiktok"],
  "captions": true
}
```

## Task orchestration

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/queue/health | Kalıcı kuyruk sayıları, worker heartbeat ve global concurrency |
| GET | /api/queue/tasks?limit=50&status=queued | Son görevlerin payload içermeyen metadata listesi |
| GET | /api/tasks/history | Son görevlerin geçmişi |
| GET | /api/tasks/{task_id} | Görev durumu ve ilerleme |
| GET | /api/tasks/{task_id}/events | Görev olay geçmişi |
| POST | /api/tasks/{task_id}/cancel | Çalışan görevi iptal etmeyi dener |
| POST | /api/tasks/{task_id}/retry | Yeniden denenebilir görevi tekrar başlatır |

Görev durumları arasında queued, running, completed, failed, cancelled ve interrupted bulunur. Kalıcı kuyruk görevleri worker lease süresi dolduğunda aynı-host worker tarafından yeniden alınabilir. `/api/queue/tasks` özel payload içeriğini döndürmez.

## Content creation

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/content/voices | Ses kataloğu |
| POST | /api/content/trends | RSS kaynaklarından konu keşfi |
| POST | /api/content/script | Yerel Ollama ile senaryo |
| POST | /api/content/voiceover | Metinden ses üretimi |
| POST | /api/content/create-video | Tam video üretim akışı |
| POST | /api/content/create-cinematic | Sinematik video üretim akışı |

### Script request

```json
{
  "niche": "Teknoloji",
  "topic": "Yapay zekâ araçları",
  "language": "tr",
  "duration": 60
}
```

### Complete video request

Alanlar: niche, topic, region, language, duration, voice, captions, auto_trend, style, visual_provider, shot_count, generate_music. İzin verilen style değerleri shorts/trailer; visual_provider değerleri motion/runway/pexels şeklindedir. Tam alan kısıtları için canlı OpenAPI şemasına bakın.

## AI agents and learning

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/agents/run | Bir klip için uzman ajan takımını çalıştırır |
| GET | /api/agents/report/{job_id}/{clip_id} | Ajan raporunu getirir |
| GET | /api/learning | Yerel performans içgörüleri |
| POST | /api/learning/record | Platform performans örneği kaydeder |

## Autopilot

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/autopilot | Planları listeler |
| POST | /api/autopilot | Yeni plan oluşturur |
| PATCH | /api/autopilot/{autopilot_id} | Planı günceller |
| DELETE | /api/autopilot/{autopilot_id} | Planı siler |
| POST | /api/autopilot/{autopilot_id}/run | Planı kalıcı kuyruğa ekler; çift çalıştırma 409 döndürür |

## Platform and OAuth

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/platforms | Platform profillerini listeler |
| POST | /api/platforms/profile | Platform profilini günceller |
| GET | /api/oauth/config/status | OAuth uygulama ayarı durumu |
| POST | /api/oauth/config | Platform OAuth uygulama kimlik bilgilerini kaydeder |
| GET | /api/oauth/status | Bağlı hesap durumları |
| GET | /api/oauth/start/{platform_name} | OAuth akışını başlatır |
| GET | /api/oauth/callback/{platform_name} | OAuth dönüşünü işler |
| DELETE | /api/oauth/{platform_name} | Yerel bağlantı bilgisini kaldırır |
| GET | /api/publish/tiktok/creator | TikTok creator kısıtlarını sorgular |
| POST | /api/publish/{platform_name} | Açık kullanıcı onayıyla platforma yükler |

Platform yayınlama, geçerli OAuth erişimi, platform hesabı uygunluğu ve API izinlerine bağlıdır. Her uygulama/proje otomatik yayınlama için onaylı olmayabilir.

## Settings and assets

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/settings | Yerel model ve uygulama ayarları |
| POST | /api/settings | Ollama/Whisper ayarlarını kaydeder |
| GET | /api/media/library | Yerel medya kütüphanesi |
| GET | /api/projects | Yerel proje listesi |
| GET | /api/visual-providers | Runway/Pexels yapılandırma durumu |
| POST | /api/visual-providers | Görsel sağlayıcı anahtarlarını şifreli kasaya kaydeder |
| GET | /api/update/status | Güncelleme durumunu kontrol eder |
| POST | /api/update/apply | Beklenen commit doğrulamasıyla güncellemeyi uygular |

## Error handling

FastAPI doğrulama hataları genellikle 422, bulunamayan kaynaklar 404, servis/entegrasyon problemleri 4xx/5xx yanıtları döndürür. Hata gövdeleri uygulama sürümüne göre değişebilir. Hassas logları veya token'ları paylaşmayın.
