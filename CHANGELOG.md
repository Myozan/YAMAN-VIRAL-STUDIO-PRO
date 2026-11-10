# Changelog / S?r?m Ge?mi?i

Bu dosya tamamlanm?? de?i?iklikleri planlanan ?zelliklerden ayr? tutar.

## [1.3.0] - 2026-11-11

### Fixed
- T?rk?e aray?z metinlerindeki mojibake/karakter kodlama sorunlar? temizlendi; HTML UTF-8 ve g?venli metin g?sterimi standardize edildi.
- CPU g?sterge metinleri ve donan?m bilgileri k???k ekranlarda ta?ma yapmayacak ?ekilde yeniden d?zenlendi.
- K?sa kaynak videolarda minimum kesit penceresinin video s?resinden uzun kalmas? nedeniyle aday ?retiminin erken sonlanmas? d?zeltildi.
- Konu?ma az oldu?unda daha a??klay?c? hata mesaj? ve k?sa konu?ma i?in yedek aday ?retimi eklendi.
- Render i?leminde se?ilen kesit ba?lang?? zaman? FFmpeg'e do?ru aktar?l?r.

### Added
- Platform profili d?zenleme API'si: en-boy oran? (9:16, 1:1, 16:9), ??z?n?rl?k (720p/1080p) ve azami s?re.
- Platform profilleri yerel platform_profiles.json dosyas?na kaydedilir; render i?lemi bu ayarlar? kullan?r.
- Uzman ajan tak?m? 8'den 12'ye ??kar?ld?: izleyici tutma, kapak/g?rsel y?netimi, ?ok dilli yerelle?tirme ve eri?ilebilirlik denetimi.
- Ajan ilerlemesi toplam ajan say?s?na g?re dinamik hesaplan?r.
- Mobil gezinme, sistem g?stergeleri, donan?m kartlar? ve platform profilleri i?in responsive d?zen iyile?tirildi.
- ??lemci modeli, ?ekirdek/thread ve saat h?z? CPU telemetri sat?r?na eklendi.

### Research / Entegrasyon de?erlendirmesi
- AutoClip (MIT), CrewAI (MIT) ve LangGraph (MIT) GitHub depolar? mimari ve lisans a??s?ndan incelendi.
- A??r ajan framework'leri mevcut yerel Ollama/FastAPI uygulamas?na gereksiz ba??ml?l?k getirmesin diye runtime'a eklenmedi. Uygun yerel i? ak??? ve uzman g?revleri mevcut mimariye uyarland?; upstream kaynak kodu kopyalanmad?.

### Notes
- Platform profili, render ??kt?s?n? yap?land?r?r; OAuth tabanl? do?rudan sosyal medya yay?nlama bu s?r?mde etkin de?ildir.
- CPU s?cakl??? yaln?zca LibreHardwareMonitor/OpenHardwareMonitor gibi sens?r sa?lay?c?s? eri?ilebilirse g?sterilir.

## [1.2.1] - 2026-11-10
- Studio sayfas? iskeleti ve yerel video tarama alan? onar?ld?.
- Videodan ak?ll? ?zet MP4 ?retimi, ?zet raporu ve medya k?t?phanesi ba?lant?s? eklendi.
- CPU/GPU/RAM/VRAM dairesel g?stergeleri ve tema se?imi geli?tirildi.
- 8 uzman AI ajan? ve kesit rapor kartlar? eklendi.

## [1.2.0]
- Yerel-first video analiz hatt?, Faster-Whisper transkripsiyonu, Ollama i?erik analizi ve FFmpeg dikey render.
- YouTube Shorts, Instagram Reels ve TikTok hedef profilleri.
