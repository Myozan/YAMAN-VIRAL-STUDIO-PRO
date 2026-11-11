# Video Production Guide

Bu rehber, kaynak videodan sosyal medya için kısa dikey çıktı hazırlama sürecini açıklar.

## Production workflow

1. **Source intake:** Yalnızca kullanma ve işleme hakkınız olan videoyu seçin.
2. **Transcription:** Faster-Whisper ile konuşmayı zaman damgalarıyla metne dönüştürün.
3. **Moment discovery:** İçerikte bağlamı koruyan, tek başına anlaşılabilen güçlü anları belirleyin.
4. **Clip editing:** Başlangıç/bitiş noktalarını konuşma ve görsel bağlama göre düzenleyin.
5. **Captions:** Altyazıyı gözden geçirin; özel isimleri, sayıları ve teknik terimleri düzeltin.
6. **Vertical framing:** 9:16 kadrajı kontrol edin. Yüz, ürün ve önemli görsel unsurların kırpılmadığından emin olun.
7. **Render:** FFmpeg ile hedef çözünürlük ve kalite ayarlarında MP4 oluşturun.
8. **Quality review:** Ses seviyesi, senkronizasyon, altyazı, kesme noktaları ve görüntü kalitesini kontrol edin.
9. **Export:** Son dosyayı platforma göre adlandırın ve dışa aktarın.

## Editorial quality checklist

- [ ] Klip tek başına anlaşılabilir mi?
- [ ] İlk saniyelerde izleyicinin dikkatini çeken bir başlangıç var mı?
- [ ] Kesme noktaları doğal mı?
- [ ] Altyazılar doğru ve okunaklı mı?
- [ ] Dikey kadraj ana özneyi koruyor mu?
- [ ] Ses seviyesi tutarlı mı?
- [ ] Görsel ve müzik kullanım hakları uygun mu?
- [ ] Dışa aktarılan MP4 farklı bir oynatıcıda test edildi mi?

## Platform formats

9:16 dikey format Shorts, Reels ve TikTok için yaygın bir başlangıç formatıdır. Platformların güncel süre, boyut, codec ve içerik politikalarını yayın öncesinde ayrıca kontrol edin. Tek bir export profilinin tüm platformların güncel gereksinimlerini garanti ettiği varsayılmamalıdır.

## Rights and attribution

Kaynak videolar, müzikler, görseller, fontlar ve sesler için gerekli kullanım haklarını doğrulayın. yt-dlp ile erişilebilen her içeriğin indirilmesi veya yeniden kullanılması otomatik olarak izinli değildir.
