# Autopilot Guide

Autopilot, yerel SQLite veritabanında saklanan içerik üretim planlarını zamanlamaya ve uygun zamanda çalıştırmaya yarar. Kaynak kodundaki uygulama; plan adı, niş, dil, klip sayısı, klip süreleri, platformlar, sıklık, saat ve saat dilimi alanlarını tutar.

## Scheduling model

- Frequency: daily veya weekly.
- Time: 24 saat biçiminde HH:MM.
- Timezone: IANA saat dilimi; varsayılan Europe/Istanbul.
- Enabled: planın etkin olup olmadığını belirler.
- Next run: bir sonraki planlanan çalışma zamanı.
- Runs: her çalıştırma için durum, mesaj ve çıktı referansları saklanır.

Haftalık zamanlama uygulamada Pazartesi günü temel alınır. Bu nedenle haftalık seçeneğin gün seçici sunduğu varsayılmamalıdır.

## API operations

- GET /api/autopilot — planları listele
- POST /api/autopilot — plan oluştur
- PATCH /api/autopilot/{id} — planı güncelle
- DELETE /api/autopilot/{id} — planı sil
- POST /api/autopilot/{id}/run — hemen çalıştır

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

Autopilot planları içerik üretim akışını tetikler; bu, sosyal platformlarda otomatik ve koşulsuz yayın yapılacağı anlamına gelmez. Platforma yayınlama, ayrı OAuth bağlantısı, izinler, hesap uygunluğu ve açık kullanıcı onayı gerektirir.

## Safety checklist

- Kaynak videoların işleme haklarını doğrulayın.
- Çalışma saatini ve saat dilimini kontrol edin.
- Üretilen dosyaları ve maliyetli dış servis kullanımını gözden geçirin.
- Yayın öncesi video, başlık, açıklama ve platformu onaylayın.
- Otomatik tekrarların disk alanı tüketimini takip edin.
