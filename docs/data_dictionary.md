# Veri sözlüğü ve kaynak kaydı

## Kaynaklar

| Kaynak | Gelen dosya | Zaman aralığı | Başlangıçta gözlenen kapsam | Anonimleştirme |
|---|---|---|---|---|
| Armut hizmet kayıtları | `armut_data.csv` | 2018 ve 2024; analiz 2024 | UserId, ServiceId, CategoryId, CreateDate; 2024 içinde 65.732 kayıt | Kullanıcı/hizmet kimliği çıkarılır; gün-kategori sayımı tutulur |
| NovaPerakende | `perakende_satis.xlsx` | 2024 | 2.000 satır; 12 sütun, 5 ürün kategorisi | Sipariş/müşteri kimlikleri ve ayrıntılı lokasyon/ürün/maliyet alanları çıkarılır; günlük toplama tutulur |

**Atıf/lisans alanı:** Veriyi sağlayan sayfa/kurum, URL, erişim tarihi ve yeniden dağıtım izni ekip tarafından eklenmelidir. Bu bilgiler eklenmeden ham dosyaları yayımlamayın.

## Seed alanları

### `armut_daily.csv`

| Alan | Tür | Anlam |
|---|---|---|
| event_date | date | Hizmet kaydının takvim günü |
| category_id | metin | Kaynaktaki kategori kodu; adı bilinmiyor |
| service_requests | integer | O gün ve kategori kodunda hizmet kayıt sayısı |

### `retail_daily.csv`

| Alan | Tür | Anlam |
|---|---|---|
| sale_date | date | Satış günü |
| order_lines | integer | Kaynak satırı sayısı; sipariş sayısı olarak yorumlanmamalı |
| units_sold | integer | Günlük satılan toplam birim |
| gross_sales | decimal | İndirim öncesi miktar × birim fiyat toplamı |
| net_sales | decimal | Satır miktarı × birim fiyat × (1 - indirim oranı) toplamı |

### `retail_category_daily.csv`

Gün, kategori, `order_lines`, `units_sold` ve `net_sales` alanları. Armut kategori kodlarıyla ilişkilendirilmez.

## Analitik notları

- Her iki kaynak yalnızca 2024 yılında ortak takvim kapsamına sahiptir.
- Armut günlük kategori toplamında kaynakta hiç satır olmayan gün için `unknown` kategori kodlu sıfır satırı üretilir; bu kod gerçek bir kategori değildir.
- Perakende günlük serisinde 366 gün bulunur. Kaynakta satır olmayan günlere sıfır yazılır; sıfır ile eksik veri ayrımı doğrulanmalıdır.
- `order_lines` kaynak satır sayısıdır, sipariş kimlikleri temizleme öncesinde tekil olsa dahi birden çok satırın aynı siparişe ait olup olmadığı semantik olarak doğrulanmamıştır.
- Günlük gözlemler bağımsız değildir. İstatistiksel karşılaştırmada mevsimsellik, haftanın günü, trend ve otokorelasyon dikkate alınmalıdır.
- Veri hacmi ve kapsamı nedeniyle sonuçlar keşifsel/prototip olarak raporlanır.
