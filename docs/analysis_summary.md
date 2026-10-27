# İlk analiz özeti — 2024

## Veri kapsamı

- Armut: 2024'e ait 65.732 hizmet kaydı; gün toplamları üzerinden analiz edildi.
- NovaPerakende: 2.000 kaynak satırı; 6.046 ürün birimi ve 7.206.829,00 TL net satış.
- Tarihler: 1 Ocak–31 Aralık 2024; ortak günlük mart 366 gün.
- Perakendede kaynakta satır olmayan 3 gün günlük seride sıfır satış olarak gösterildi.

## Hizmet talebi ile aynı gün perakende satışı

| Gösterge | Değer |
|---|---:|
| Pearson günlük korelasyonu | 0,4028 |
| Spearman günlük korelasyonu | 0,3981 |
| Günlük ortalama Armut kayıt sayısı | 179,596 |
| Günlük ortalama perakende ürün adedi | 16,519 |

Bu değerler 2024 günlük toplamlarında orta düzeyde pozitif eşzamanlı hareket gösteriyor. Ancak iki veri kaynağı ortak müşteri, şehir/bölge veya kategori anahtarı taşımıyor. Aynı gün korelasyonu; mevsim, haftanın günü, kaynak kapsamı ve ortak zaman örüntülerinden kaynaklanabilir. Bu nedenle sonuç nedensellik veya ürünlerin tamamlayıcı olduğuna dair kanıt değildir.

## Tahmin deneyi

Günlük ürün adedi hedefi, kronolojik olarak eğitim (%80) ve son test dönemi (%20) olarak ayrıldı. Bu ilk karşılaştırma bir gün sonrası tahmin içindir; 7 günlük uygulama tahmini son modelle yinelemeli üretilir.

| Model | MAE (adet) | RMSE (adet) | WAPE |
|---|---:|---:|---:|
| HistGradientBoosting, perakende geçmişi | 9,872 | 13,560 | 38,19% |
| Random Forest, perakende geçmişi | 9,974 | 13,939 | 38,58% |
| HistGradientBoosting + gecikmeli Armut | 10,100 | 14,517 | 39,07% |
| Random Forest + gecikmeli Armut | 10,323 | 14,687 | 39,93% |

Bu test diliminde Armut'un 1 ve 7 gün gecikmeli sayımlarını eklemek iki algoritmanın da hatasını artırdı. Mevcut deney, Armut özelliğinin ürün tahminine fayda sağladığını göstermiyor. Modelin WAPE değeri yaklaşık %38 olduğundan stok kararı için yeterli doğruluk varsayılmamalıdır.

## Kategori ve dönem görünümü

- Satılan birim adedinde Elektronik (1.821), Giyim (1.532) ve Ev & Yaşam (1.356) ilk üç kategoridir.
- 2024 aylık toplamında en yüksek birim Kasım (847), ardından Aralık (789) ve Ekim'de (622) görülmüştür.

Bunlar yalnızca dosyadaki 2.000 satış satırının dağılımıdır. Satış kaydının tüm NovaPerakende talebini temsil edip etmediği bilinmiyor; stok miktarı, stokta yok bilgisi, ürün bazlı geçmiş ve tedarik süresi de yok. Şimdilik gerçek yeniden sipariş miktarı önermeyin. Daha uzun ve temsil gücü doğrulanmış veriyle, ürün ve stok durumu düzeyinde yeniden test edin.

## Yeniden üretme

- Temizleme: `docker compose run --rm --entrypoint python project /workspace/scripts/clean_data.py`
- dbt: `docker compose run --rm project seed --full-refresh` ve `docker compose run --rm project build`
- Mart aktarımı ve modeller: README'deki export ve train komutları.
