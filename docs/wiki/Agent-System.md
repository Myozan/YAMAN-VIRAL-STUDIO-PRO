# Agent System

YAMAN VIRAL STUDIO PRO, görev odaklı küçük ajanlardan oluşan yerel bir uzman takımına sahiptir. Ajan kataloğu `app/agents.py` içinde tanımlıdır ve mevcut uygulamanın Ollama JSON çağrısı ile deterministik doğrulayıcılarını kullanır.

## Agent catalog

| Agent ID | Role | Mode |
|---|---|---|
| viral-strategist | Kesitin hook, açıklık, merak, duygu ve sonuç gücünü değerlendirir | AI |
| hook-writer | Açılış cümleleri ve CTA önerir | AI |
| editor-director | Tempo, altyazı, kadraj ve B-roll planı önerir | AI |
| seo-specialist | Platform bazlı metaveri üretir | AI |
| claim-reviewer | Doğrulanması gereken iddiaları ve yayın risklerini işaretler | AI |
| caption-qa | Altyazı okunabilirliği ve uzunluğunu denetler | RULES |
| clip-qa | Süre, zaman aralığı ve platform sınırlarını denetler | RULES |
| publishing-coordinator | Yayın hazırlık listesini oluşturur; izinsiz paylaşım yapmaz | RULES |
| audience-retention | Anlatı akışı ve izleyici kaybı risklerini inceler | AI |
| thumbnail-director | Kapak fikri ve görsel brief hazırlar | AI |
| localization-specialist | Metaveriyi farklı dillere uyarlar | AI |
| accessibility-reviewer | Altyazı ve erişilebilirlik sunumunu inceler | AI |

## Execution

1. UI, job_id ve clip_id ile ajan takımını çağırır.
2. Sunucu ilgili analiz işini ve klibi bulur.
3. Seçilen platformlar doğrulanır.
4. Ajanlar kendi görev tanımlarıyla çalışır.
5. AI ajanları JSON biçimli yanıt bekler; hata durumunda fallback yanıtı kullanabilir.
6. Kural tabanlı ajanlar deterministik kontroller gerçekleştirir.
7. Sonuçlar UI raporunda gösterilir.

Endpoint: `POST /api/agents/run`  
Rapor endpoint'i: `GET /api/agents/report/{job_id}/{clip_id}`

## Reliability and trust

- Ajan çıktıları öneridir; doğrulanmış gerçek veya yayın izni değildir.
- Model yanıtı JSON şemasına uymayabilir; fallback veya başarısız durum görülebilir.
- Ajanların doğrudan shell komutu çalıştırmasına veya sınırsız dosya/ağ erişimine izin verilmemelidir.
- Yayınlama işlemi ayrı platform API'si ve açık kullanıcı onayı gerektirir.
- İçerik iddiaları, telif hakları ve marka kullanımı insan tarafından gözden geçirilmelidir.

## Extending an agent

1. `AGENT_CATALOG` içine sabit ID, ad, rol ve mod tanımlayın.
2. Çalıştırma fonksiyonuna dar kapsamlı görev ve beklenen JSON alanlarını ekleyin.
3. Model çıktısını doğrulayın; fallback üretin.
4. İlerleme callback'lerini ve hata durumlarını ekleyin.
5. UI raporunda ajan durumunu ve süresini gösterin.
6. Hatalı JSON, boş transkript, Ollama kapalı ve iptal senaryolarını test edin.
