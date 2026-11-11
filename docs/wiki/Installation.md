# Installation Guide

Bu rehber, YAMAN VIRAL STUDIO PRO uygulamasını Windows 10/11 üzerinde yerel olarak kurmak içindir.

## 1. Gereksinimleri hazırlayın

- Windows 10 veya Windows 11 (64-bit önerilir)
- Python 3.12
- Git
- FFmpeg ve FFprobe
- Ollama (yerel AI özellikleri için; isteğe bağlı)

## 2. Depoyu indirin

    git clone https://github.com/Myozan/YAMAN-VIRAL-STUDIO-PRO.git
    cd YAMAN-VIRAL-STUDIO-PRO

## 3. Sanal ortamı oluşturun

    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1

PowerShell betik çalıştırma ilkesi aktivasyonu engellerse yalnızca mevcut kullanıcı için:

    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Ardından sanal ortamı yeniden etkinleştirin.

## 4. Python bağımlılıklarını kurun

    python -m pip install --upgrade pip
    pip install -r requirements.txt

## 5. Ortam ayarlarını oluşturun

    Copy-Item .env.example .env

Örnek yapılandırma:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| OLLAMA_URL | http://127.0.0.1:11434 | Yerel Ollama servisi |
| OLLAMA_MODEL | qwen3:1.7b | Kullanılacak Ollama modeli |
| WHISPER_MODEL | tiny | Whisper model boyutu |
| WHISPER_DEVICE | cpu | Whisper işlem aygıtı |
| MAX_DOWNLOAD_MB | 2048 | İndirme boyutu üst sınırı (MB) |

Gizli anahtarları Git deposuna göndermeyin.

## 6. FFmpeg kontrolü

    ffmpeg -version
    ffprobe -version

Komutlar bulunamıyorsa FFmpeg'in bin klasörünü Windows PATH değişkenine ekleyin ve terminali yeniden açın.

## 7. Ollama'yı hazırlayın (isteğe bağlı)

Ollama'yı resmi Windows kurulumundan yükleyin. Ardından:

    ollama --version
    ollama pull qwen3:1.7b
    ollama list

Model seçimini sistem belleği ve işlemci/GPU kapasitesine göre yapın.

## 8. Uygulamayı başlatın

    .\run_windows.bat

Başlatıcı gerekli sanal ortamı oluşturur, bağımlılıkları kontrol eder ve FastAPI sunucusunu açar:

**http://127.0.0.1:8765**

## 9. İlk açılış kontrol listesi

- [ ] Studio arayüzü açılıyor.
- [ ] FFmpeg ve FFprobe komutları çalışıyor.
- [ ] Ollama kullanılıyorsa servis erişilebilir.
- [ ] Whisper modeli ilk transkripsiyon için hazır.
- [ ] Kaynak video içe aktarımı ve çıktı klasörü kontrol edildi.

## Güvenlik ve veri

Varsayılan sunucu adresi 127.0.0.1 olduğundan servis yerel makineye bağlanır. LAN veya internet erişimi açmadan önce kimlik doğrulama, erişim kontrolü, güvenlik duvarı ve HTTPS gereksinimlerini değerlendirin.

İlk model indirmeleri internet bağlantısı gerektirebilir. Modeller ve bağımlılıklar indirildikten sonra desteklenen işleme adımları yerel çalışabilir.
