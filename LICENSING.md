# Lisanslama modeli

YAMAN VIRAL STUDIO PRO iki ayrı dağıtım kanalına sahip olabilir; ancak lisans sınırı dosya ve bileşen bazında açıkça belirlenir.

## 1. Community Edition

- Depodaki mevcut kaynak kodu, kök dizindeki `LICENSE` dosyasında bulunan MIT Lisansı kapsamındadır.
- MIT lisansı; kullanım, değiştirme, dağıtma, alt lisanslama ve ticari kullanım hakları verir.
- Dağıtılan kopyalarda telif ve izin bildirimi korunmalıdır.
- Bu haklar, ilgili MIT kapsamındaki sürümler için sonradan yayımlanacak bir ticari lisans metniyle geriye dönük olarak kaldırılamaz.

## 2. Enterprise / Commercial Edition

Ticari lisans yalnızca açıkça tanımlanmış, ayrı tutulan ve ticari lisans bildirimi taşıyan ilave bileşenler için uygulanır. Örnekler:

- Kurumsal SSO / merkezi kimlik ve erişim yönetimi eklentileri
- Çok kullanıcılı yönetim, gelişmiş rol ve denetim modülleri
- Kurumsal dağıtım, yönetim ve raporlama eklentileri
- Ücretli destek, SLA, kurulum ve bakım hizmetleri

Bu örnekler ürün yol haritası önerisidir; mevcut depoda bu özelliklerin bulunduğu veya ticari lisansla korunduğu anlamına gelmez.

### Kod ve depo sınırı

1. Community çekirdeği MIT olarak kalır.
2. Yeni ticari kaynak kodu `enterprise/` gibi ayrı bir dizinde tutulur.
3. Ticari dosyaların başında `SPDX-License-Identifier: LicenseRef-Yaman-Commercial` ve `Copyright` bildirimi bulunur.
4. Ticari modüller, Community paketine yanlışlıkla dahil edilmemeleri için ayrı paketleme/derleme adımından geçirilir.
5. Ticari modül MIT kapsamındaki Community koduna bağımlıysa, bu bağımlılık ve dağıtım biçimi ayrıca incelenir. MIT kodunun kendisi MIT koşullarıyla kalır.
6. Her üçüncü taraf bağımlılığın kendi lisansı geçerlidir; bu model üçüncü taraf lisanslarını değiştirmez.

## 3. Marka ve varlıklar

MIT lisansı, YAMAN VIRAL STUDIO PRO adını, logosunu, ticari markalarını veya alan adlarını kullanma hakkını kendiliğinden vermez. Marka kullanımı ayrıca yazılı izin gerektirebilir. Logolar ve marka varlıkları için ayrı bir marka politikası yayımlanmalıdır.

## 4. Ticari lisans süreci

Kurumsal kullanım için taraflar arasında yazılı ve imzalı bir sözleşme yapılmalıdır. `LICENSE-COMMERCIAL-TEMPLATE.md` yalnızca müzakere ve hukuk incelemesi için taslak şablondur; doldurulup imzalanmadıkça lisans vermez.

Sözleşmede en az şu konular netleştirilmelidir:

- Lisans veren ve lisans alanın tam tüzel kişi bilgileri
- Lisanslanan ürün, modül, sürüm ve teslimat kapsamı
- Kullanıcı, cihaz, sunucu, tenant veya lokasyon sınırları
- Süre, yenileme, ücret, vergi ve ödeme koşulları
- Kurulum, destek, bakım ve SLA kapsamı
- Veri koruma, gizlilik, güvenlik ve olay bildirimi
- Fikri mülkiyet, türev çalışmalar ve üçüncü taraf bileşenler
- Fesih, lisans sona ermesi ve verilerin iadesi/silinmesi
- Uygulanacak hukuk, yetkili mahkeme ve uyuşmazlık çözümü

## 5. Sürüm etiketi ve lisans beyanı

| Dağıtım | Lisans |
|---|---|
| Community kaynak kodu ve MIT kapsamındaki dosyalar | MIT — `LICENSE` |
| Ayrı ticari modüller | İmzalı ticari sözleşme — ilgili dosya bildirimi |
| Üçüncü taraf bağımlılıklar | Her bağımlılığın kendi lisansı |
| Marka, logo ve ticari isim | Ayrı marka izni/politikası |

Bir dosyada lisans bildirimi yoksa otomatik olarak ticari lisans kapsamına girdiği varsayılmamalıdır. Yayın öncesinde her dağıtım paketinin içerik listesi ve lisans envanteri kontrol edilmelidir.

> Bu doküman operasyonel lisanslama politikasıdır; hukuki görüş veya imzalı sözleşme yerine geçmez.
