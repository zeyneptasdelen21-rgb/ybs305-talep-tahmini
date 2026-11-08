# Veri sözlüğü ve kaynak kaydı

## Kaynaklar

| Kaynak | Gelen dosya | Zaman aralığı | Başlangıçta gözlenen kapsam | Anonimleştirme |
|---|---|---|---|---|
| Armut hizmet kayıtları | `armut_data.csv` | 2018 ve 2024; analiz 2024 | UserId, ServiceId, CategoryId, CreateDate; 2024 içinde 65.732 kayıt | Kullanıcı/hizmet kimliği çıkarılır; gün-kategori sayımı tutulur |
| NovaPerakende | `perakende_satis.xlsx` | 2024 | 2.000 satır; 12 sütun, 5 ürün kategorisi | Sipariş/müşteri kimlikleri ve ayrıntılı lokasyon/ürün/maliyet alanları çıkarılır; günlük toplama tutulur |

### Kaynak ve kullanım notu

- **NovaPerakende:** `perakende_satis.xlsx`, YBS305 dersi kapsamında Ece hocamız tarafından Teams üzerinden paylaşılmıştır. Ayrı bir lisans veya yeniden dağıtım izni belirtilmemiştir; ham dosya GitHub'a yüklenmemiştir.
- **Armut:** `armut_data.csv` ekipteki dosya olarak dersin Teams/SharePoint alanından alınmıştır. Dosyanın asıl yayımlayıcısı, kaynak sayfası ve lisans/yeniden dağıtım koşulları henüz doğrulanmamıştır. Bu nedenle ham dosya GitHub'a yüklenmemiştir. Özel Teams/SharePoint bağlantısı herkese açık depoya eklenmemelidir.

Kaynakların asıl URL'si, erişim tarihi ve yeniden dağıtım koşulları ekip tarafından doğrulanınca bu kayıt güncellenmelidir. Bu bilgiler doğrulanana kadar analiz yalnızca anonim toplulaştırılmış çıktılarla paylaşılır.

## Temizleme özeti

Temizleme betiği her iki kaynakta tam yinelenen veya geçersiz kayıt bulmadı. Analiz 2024 takvim yılıyla sınırlandırıldı; kişisel/sipariş kimlikleri ve gerekli olmayan ayrıntı alanları çıktıdan çıkarıldı.

| Kaynak | Girdi | 2024 kaydı | Temizleme çıktısı |
|---|---:|---:|---:|
| Armut | 162.523 satır (2018 ve 2024) | 65.732 hizmet kaydı | 1.970 gün-kategori toplam satırı; `UserId` ve `ServiceId` çıkarıldı |
| NovaPerakende | 2.000 satır | 2.000 satış satırı | 366 günlük toplam; sipariş/müşteri kimlikleri ile konum, ürün ve maliyet ayrıntıları çıkarıldı |

Bu sayılar `data/processed/cleaning_report.json` raporuyla aynıdır. Kaynakta satır bulunmayan günler sıfırla temsil edilmiştir; bu, o gün kesinlikle talep olmadığı anlamına gelmeyebilir.

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

## dbt Mart Modelleri Veri Sözlüğü

Bu bölümde, PostgreSQL veri ambarındaki `analytics` şemasında bulunan ve Metabase dashboard ile analiz çalışmalarında kullanılan üç mart modelinin alanları açıklanmaktadır.

Sütun adları ve veri türleri PostgreSQL `information_schema.columns` üzerinden doğrulanmıştır.

### 1. mart_daily_demand — Günlük Talep ve Satış Analizi

Armut hizmet talepleri ile NovaPerakende satış verilerinin günlük düzeyde birlikte incelenmesi için hazırlanmış analiz tablosudur.

| Sütun adı | Veri türü | Açıklama |
|---|---|---|
| demand_date | date | Analizin gerçekleştirildiği takvim günü |
| demand_month | date | İlgili günün ait olduğu ayı temsil eden tarih |
| day_of_week | integer | Haftanın gününü belirten sayısal değer |
| armut_service_requests | integer | İlgili gündeki Armut hizmet talebi sayısı |
| armut_data_available | boolean | İlgili gün için Armut kaynak verisinin bulunup bulunmadığını gösteren alan |
| retail_order_lines | integer | İlgili gündeki perakende satış satırı sayısı |
| retail_units_sold | integer | İlgili günde satılan toplam ürün adedi |
| retail_gross_sales | numeric | İndirim uygulanmadan önceki toplam satış tutarı |
| retail_net_sales | numeric | İndirimler sonrasındaki toplam net satış tutarı |

Bu tablo, günlük satış ve hizmet talebi eğilimlerinin incelenmesinde kullanılmaktadır.

### 2. mart_monthly_demand — Aylık Talep ve Satış Analizi

Günlük verilerin aylık düzeyde özetlenmesiyle oluşturulan analiz tablosudur. Aylık satış trendleri, hizmet talebi değişimleri ve temel performans göstergelerinin incelenmesinde kullanılmaktadır.

| Sütun adı | Veri türü | Açıklama |
|---|---|---|
| demand_month | date | Analizin ait olduğu ayı temsil eden tarih |
| armut_service_requests | integer | İlgili ayda kaydedilen toplam Armut hizmet talebi |
| armut_observed_days | integer | İlgili ayda Armut verisinin mevcut olduğu gün sayısı |
| retail_order_lines | integer | İlgili aydaki toplam perakende satış satırı sayısı |
| retail_units_sold | integer | İlgili ayda satılan toplam ürün adedi |
| retail_gross_sales | numeric | İlgili ayın indirim öncesi toplam satış tutarı |
| retail_net_sales | numeric | İlgili ayın indirim sonrası toplam net satış tutarı |
| calendar_days | integer | İlgili takvim ayındaki toplam gün sayısı |

Bu tablo, Metabase dashboard üzerinde aylık net satış ve Armut hizmet talebi trendleri ile toplam satış, ürün adedi ve satış satırı KPI'larının hesaplanmasında kullanılmaktadır.

### 3. mart_retail_category_daily — Günlük Kategori Bazında Satış Analizi

NovaPerakende satışlarının ürün kategorilerine göre günlük düzeyde incelenmesi için hazırlanmış analiz tablosudur.

| Sütun adı | Veri türü | Açıklama |
|---|---|---|
| sale_date | date | Satışın gerçekleştiği takvim günü |
| category | character varying | Ürünün ait olduğu perakende kategorisi |
| order_lines | integer | İlgili gün ve kategorideki satış satırı sayısı |
| units_sold | integer | İlgili gün ve kategoride satılan toplam ürün adedi |
| net_sales | numeric | İlgili gün ve kategoride gerçekleşen indirim sonrası net satış tutarı |

Bu tablo, Metabase dashboard üzerinde kategori bazında net satışların, kategori satış paylarının ve satılan ürün adetlerinin görselleştirilmesinde kullanılmaktadır.

### 4. Veri Türleri ve Yorumlama Notları

- `date`: Takvim tarihini ifade eder.
- `integer`: Tam sayı türündeki değerleri ifade eder.
- `numeric`: Satış tutarları gibi sayısal değerleri ifade eder.
- `boolean`: Doğru veya yanlış değerlerini ifade eder.
- `character varying`: Metin türündeki değerleri ifade eder.

**Önemli analitik notlar:**

- `order_lines` alanı satış satırı sayısını gösterir; doğrudan benzersiz sipariş sayısı olarak yorumlanmamalıdır.
- `gross_sales` indirim öncesi, `net_sales` ise indirim sonrası satış tutarını ifade eder.
- Armut hizmet kategorileri ile perakende ürün kategorileri arasında doğrudan eşleştirme yapılmamıştır.
- Kaynakta kayıt bulunm
