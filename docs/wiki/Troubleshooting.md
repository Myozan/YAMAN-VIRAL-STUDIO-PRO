# Troubleshooting

## Uygulama açılmıyor

- Python 3.12 kurulumunu doğrulayın.
- Sanal ortamın etkin olduğundan emin olun.
- Bağımlılıkları yeniden kurun:

      python -m pip install --upgrade pip
      pip install -r requirements.txt

- Başlatıcı penceresindeki ilk hata mesajını inceleyin.

## Port 8765 kullanımda

Başka bir uygulama aynı portu kullanıyor olabilir. Windows'ta PID'yi bulmak için:

    netstat -ano | findstr :8765

İşlemi sonlandırmadan önce PID'nin hangi uygulamaya ait olduğunu doğrulayın. Uygulamanın portu değiştirilmişse tarayıcı adresini de buna göre güncelleyin.

## FFmpeg veya FFprobe bulunamıyor

    ffmpeg -version
    ffprobe -version

Komutlar bulunamıyorsa FFmpeg bin klasörünü PATH'e ekleyin ve terminali yeniden açın.

## Ollama bağlantı hatası

- Ollama'nın kurulu ve çalışır durumda olduğunu kontrol edin.
- Yerel servis adresini doğrulayın: http://127.0.0.1:11434
- Modeli kontrol edin:

      ollama list

- .env içindeki OLLAMA_URL ve OLLAMA_MODEL değerlerini kontrol edin.

## Whisper ilk çalıştırmada yavaş

İlk kullanımda model indirilebilir ve yüklenebilir. Model boyutu, işlemci, bellek ve disk hızı süreyi etkiler. Daha küçük bir modelle test edin.

## Video indirme veya işleme başarısız

- Kaynak URL'nin erişilebilir ve desteklenen biçimde olduğunu doğrulayın.
- İndirme boyutu sınırını ve boş disk alanını kontrol edin.
- Kaynak içeriği indirme ve yeniden kullanma hakkınız olduğundan emin olun.
- FFmpeg/FFprobe sürümünü ve uygulama loglarını kontrol edin.

## Güvenli hata raporu hazırlama

Hata bildirirken işletim sistemi, Python sürümü, uygulama sürümü, hata adımları ve kişisel verilerden arındırılmış log parçalarını ekleyin. Token, API anahtarı, parola, özel URL veya kişisel medya paylaşmayın.
