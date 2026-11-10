# Changelog / Sürüm Geçmişi

## [1.4.0] - 2026-11-11

### Added
- SQLite tabanlı kalıcı görev ve olay günlüğü.
- Ajan görevlerini iptal etme, başarısız/kesintiye uğramış görevleri yeniden deneme ve uygulama yeniden başladığında görev durumunu kurtarma.
- Yerel AI ajan çağrılarında sınırlı yeniden deneme politikası.
- YouTube, TikTok ve Instagram için resmî OAuth bağlantı akışları.
- OAuth istemci kimlik bilgileri ve kullanıcı tokenları Fernet ile şifrelenerek yerel kasada saklanır.
- YouTube Data API ile kullanıcı onaylı resumable MP4 yükleme.
- TikTok Content Posting API ile kullanıcı onaylı Direct Post dosya yükleme ve AI-generated etiket tercihi.
- Instagram Graph API ile Reels container ve yayınlama akışı; profesyonel hesap/Page bağlantısı keşfi.
- Platform Profilleri ekranına geliştirici Client ID/Secret kaydı, bağlantı durumu, bağlan/kes kontrolleri eklendi.
- Medya kütüphanesine kullanıcı onaylı platform yayınlama eylemi eklendi.
- Türkçe/İngilizce arayüz dil seçici eklendi.
- README belgeleri dil başına ayrı dosyalara ayrıldı: README.md, README.en.md, README.de.md, README.es.md.

### Changed
- CPU kartında yalnızca işlemci modeli ve işlemci kullanımı gösterilir.
- CPU sıcaklığı, çekirdek/thread, saat hızı ve GPU sıcaklığı arayüzden ve telemetri yanıtından kaldırıldı.
- Türkçe gezinme menüsü ve görünür metinler UTF-8/HTML entity tabanlı olarak yeniden düzenlendi.
- Sürüm 1.4.0 olarak güncellendi.

### OAuth limitations and requirements
- Gerçek hesap bağlantısı için platform geliştirici uygulaması, Client ID/Secret, doğru callback adresi ve platform tarafından onaylanmış kapsamlar gerekir.
- TikTok'un denetlenmemiş istemcileri yalnızca özel gönderi yayınlayabilir.
- Instagram Reels, Meta'nın erişebildiği genel HTTPS medya URL'si gerektirir; localhost dosyaları kullanılamaz.
- Her yayın isteği kullanıcı onayı gerektirir; arka planda sessiz yayın yapılmaz.

## [1.3.0] - 2026-11-11
- Dört uzman ajan eklendi; toplam ajan sayısı 12'ye çıkarıldı.
- Mobil düzen, platform profilleri ve kısa video kesit seçimi iyileştirildi.
- Videodan akıllı özet MP4 üretimi ve rapor kartları eklendi.

## [1.2.1] - 2026-11-10
- Studio sayfası onarıldı; yerel video tarama, transkripsiyon ve sistem göstergeleri geliştirildi.
