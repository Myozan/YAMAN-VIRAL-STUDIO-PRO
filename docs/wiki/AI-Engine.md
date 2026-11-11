# AI Engine Configuration

Bu sayfa, YAMAN VIRAL STUDIO PRO içindeki yerel AI bileşenlerinin yapılandırmasını açıklar.

## Ollama

Ollama, yerel dil modeli servisidir. Örnek yapılandırma:

    OLLAMA_URL=http://127.0.0.1:11434
    OLLAMA_MODEL=qwen3:1.7b

Ollama kurulduktan sonra:

    ollama --version
    ollama pull qwen3:1.7b
    ollama list

Servis erişimini kontrol edin. Uygulamanın kullandığı model adı ile yerel olarak indirilen model adı aynı olmalıdır.

## Faster-Whisper

Örnek yapılandırma:

    WHISPER_MODEL=tiny
    WHISPER_DEVICE=cpu

Model seçenekleri donanım ve doğruluk/hız ihtiyacına göre değerlendirilmelidir. Daha büyük modeller genellikle daha fazla bellek ve işlem gücü kullanır. İlk kullanımda model dosyalarının indirilmesi gerekebilir.

## Yerel çalışma ve dış servisler

Yerel Ollama ve Faster-Whisper kullanımı, desteklenen analiz ve transkripsiyon adımlarının bilgisayarda yürütülmesini sağlar. Ancak isteğe bağlı bazı servisler internet bağlantısı veya harici hesap gerektirebilir. Yerel öncelikli mimari, bütün özelliklerin otomatik olarak çevrimdışı çalıştığı anlamına gelmez.

## Troubleshooting

- **Ollama bulunamıyor:** Ollama servisinin açık olduğunu doğrulayın.
- **Model bulunamadı:** ollama list ile model adını kontrol edin.
- **Bağlantı hatası:** OLLAMA_URL değerini ve yerel servis portunu doğrulayın.
- **Transkripsiyon yavaş:** Daha küçük Whisper modeli veya desteklenen hızlandırma seçeneklerini değerlendirin.
- **İlk açılış uzun:** Model indirme ve ilk yükleme sürelerini hesaba katın.

Gizli anahtarları veya özel erişim bilgilerini issue ve log kayıtlarına eklemeyin.
