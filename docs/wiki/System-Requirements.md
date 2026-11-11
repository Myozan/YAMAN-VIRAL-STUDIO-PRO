# System Requirements

## Desteklenen ortam

| Bileşen | Gereksinim |
|---|---|
| İşletim sistemi | Windows 10/11 |
| Python | 3.12 |
| Web/API | FastAPI + Uvicorn |
| Video işleme | FFmpeg + FFprobe |
| Konuşma tanıma | Faster-Whisper |
| Yerel LLM | Ollama (isteğe bağlı) |
| Tarayıcı | Güncel Chromium, Edge veya Firefox |

## Donanım önerileri

Gerçek kaynak ihtiyacı video çözünürlüğü, klip uzunluğu, Whisper modeli, Ollama modeli ve eşzamanlı iş sayısına göre değişir. Depoda doğrulanmış tek bir minimum RAM/GPU değeri bulunmadığından aşağıdaki tablo garanti edilen minimum sistem gereksinimi değildir.

| Kullanım | Öneri |
|---|---|
| Temel arayüz ve API | Modern 64-bit işlemci, 8 GB RAM |
| CPU ile transkripsiyon | 16 GB RAM ve hızlı SSD |
| Yerel LLM + video işleme | 16–32 GB RAM önerilir |
| GPU hızlandırma | Uyumlu GPU, sürücü ve desteklenen ML çalışma zamanı |

## Disk alanı

- Python sanal ortamı ve bağımlılıklar için boş alan ayırın.
- Whisper/Ollama modelleri ek disk alanı kullanır.
- Kaynak videolar ve render çıktıları büyük dosyalar olabilir.
- Çalışma alanı ve yedekler için yeterli SSD/NAS kapasitesi planlayın.

## Ağ gereksinimleri

Temel yerel API varsayılan olarak 127.0.0.1:8765 üzerinde çalışır. İlk kurulum, Python paketleri ve model indirmeleri internet gerektirebilir. Ollama yerel servisi varsayılan olarak 127.0.0.1:11434 adresinde beklenir.

İsteğe bağlı harici entegrasyonlar kendi internet ve kimlik doğrulama gereksinimlerine sahiptir.

## Performansı etkileyen faktörler

- Video çözünürlüğü, kare hızı ve süresi
- Whisper model boyutu ve CPU/GPU seçimi
- Ollama model boyutu ve bağlam uzunluğu
- FFmpeg filtreleri, altyazı ve yeniden kodlama ayarları
- Aynı anda çalışan iş sayısı ve depolama hızı

Kurulumdan önce depodaki requirements.txt, .env.example ve README dosyasını kontrol edin.
