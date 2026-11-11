# Autopilot Guide

Autopilot, yerel SQLite veritabanında saklanan içerik üretim planlarını zamanlamaya ve uygun zamanda çalıştırmaya yarar. Plan adı, niş, dil, klip sayısı, klip süreleri, platformlar, sıklık, saat ve saat dilimi alanları saklanır.

## Scheduling model

- Frequency: daily veya weekly.
- Time: 24 saat biçiminde HH:MM.
- Timezone: IANA saat dilimi; varsayılan Europe/Istanbul.
- Enabled: planın etkin olup olmadığını belirler.
- Next run: bir sonraki planlanan çalışma zamanı.
- Runs: her çalıştırma için durum, mesaj ve çıktı referansları saklanır.

Haftalık zamanlama Pazartesi günü temel alınır. Haftalık seçenek ayrı bir gün seçici sunmaz.

## Durable execution

- Manual runs and scheduled runs are inserted into the same SQLite durable task queue.
- The schedule poller only claims due schedules; it does not perform content generation in its local thread.
- Advancing a due schedule, reserving the Autopilot plan and inserting the queue/public task journal happen in one SQLite transaction.
- Multiple Uvicorn processes share the same database and cannot enqueue the same due occurrence twice.
- Manual and scheduled runs share an active-run guard; a queued or running plan cannot be started again, edited or deleted.
- Upgrade reconciliation marks orphaned legacy process-local runs as failed instead of leaving a plan stuck in `running`; active durable queue runs are preserved.
- Queue workers own the execution lease. Stale workers cannot overwrite progress or mark the plan failed after another worker has reclaimed the task.
- The durable task ID is reused for run history, making completion replay idempotent.
- Queue execution is at-least-once. A process crash can repeat unfinished work; deterministic task folders and render output names are used where possible.
- The Autopilot page includes queue counts, worker heartbeats, global concurrency and recent task metadata.

## API operations

- GET /api/autopilot — planları listele
- POST /api/autopilot — plan oluştur
- PATCH /api/autopilot/{id} — planı güncelle
- DELETE /api/autopilot/{id} — planı sil
- POST /api/autopilot/{id}/run — kalıcı kuyruğa manuel çalıştırma ekle
- GET /api/queue/health — worker ve kuyruk sağlığı
- GET /api/queue/tasks?limit=50 — son görevlerin güvenli metadata listesi

## Example plan

    {
      "name": "Teknoloji Shorts",
      "niche": "Teknoloji",
      "language": "tr",
      "clips": 5,
      "min_seconds": 20,
      "max_seconds": 55,
      "platforms": ["youtube", "instagram", "tiktok"],
      "frequency": "daily",
      "publish_time": "09:00",
      "timezone": "Europe/Istanbul",
      "enabled": true
    }

## Operational behavior

Autopilot planları içerik üretim akışını tetikler; sosyal platformlarda otomatik ve koşulsuz yayın yapılmaz. Platforma yayınlama, ayrı OAuth bağlantısı, izinler, hesap uygunluğu ve açık kullanıcı onayı gerektirir. Zamanlanmış üretim için uygulama ve en az bir queue worker süreci açık olmalıdır.

## Safety checklist

- Kaynak videoların işleme haklarını doğrulayın.
- Çalışma saatini ve saat dilimini kontrol edin.
- Üretilen dosyaları ve maliyetli dış servis kullanımını gözden geçirin.
- Yayın öncesi video, başlık, açıklama ve platformu onaylayın.
- Otomatik tekrarların disk alanı tüketimini takip edin.
- Worker çökmesi sonrası aynı task ID ile yeniden denemeyi ve çıktı dosyalarının bütünlüğünü kontrol edin.
