# Model kartı — günlük perakende ürün adedi

**Durum:** İlk deney çalıştırıldı; sonuçlar yalnızca 2024 örnek verisi içindir.

- **Amaç:** Günlük NovaPerakende toplam birim talebi için kısa vadeli 7 günlük gösterim tahmini.
- **Tahmin hedefi:** `retail_units_sold`.
- **Özellikler:** tahmin baz çizgisi için 1 ve 7 gün perakende gecikmesi; önceki 7/28 gün ortalamaları; haftanın günü, ay ve yılın günü. Ek deneyde aynı günlerden kaçınılarak Armut 1/7 gün gecikmeleri eklenir.
- **Algoritmalar:** Random Forest Regressor ve HistGradientBoosting Regressor; her ikisi için perakende-geçmişi baz çizgisi ve gecikmeli Armut değişkenleri eklenmiş deney karşılaştırılır. Canlı tahmin Armut değişkeni olmadan yapılır; bu karşılaştırma ek verinin faydasını keşifsel ölçer.
- **Bölme:** Tarihe göre sıralanmış gözlemlerin ilk %80'i eğitim, son %20'si test; rastgele karıştırma yok.
- **Metrikler:** MAE, RMSE ve WAPE. Test MAE'si düşük algoritma seçilir.
- **İlk test sonuçları (son %20, 1 adım ileri):**

  | Algoritma / özellikler | MAE (adet) | RMSE (adet) | WAPE |
  |---|---:|---:|---:|
  | HistGradientBoosting, perakende geçmişi | 9.872 | 13.560 | 38.19% |
  | Random Forest, perakende geçmişi | 9.974 | 13.939 | 38.58% |
  | HistGradientBoosting + gecikmeli Armut | 10.100 | 14.517 | 39.07% |
  | Random Forest + gecikmeli Armut | 10.323 | 14.687 | 39.93% |

  Bu test diliminde gecikmeli Armut sayımları tahmin hatasını düşürmedi. Günlük eşzamanlı korelasyon ayrı keşifsel analizdir; tek başına tahmin faydası veya nedensellik göstermez. Ayrıntılar `docs/analysis_summary.md` dosyasındadır.
- **Veri:** 2024 yılı, 2.000 kaynak perakende satırı; günlük agregalar.
- **Bilinen sınırlılıklar:** Tek yıllık kısa seri; stok/elde kalmama veya promosyon kayıtları yok; kaynak temsil gücü bilinmiyor; modelde Armut hizmet sayısı kullanılmıyor çünkü coğrafi ve anlamsal eşleşme kanıtı yok. Bu nedenle sonuçlar gerçek sipariş/stok kararlarında kullanılmamalıdır.
- **Etik/gizlilik:** Model anonim günlük agregalarda çalışır; kişi bazında tahmin yapmaz.
- **Yeniden değerlendirme:** Daha uzun ve temsil gücü doğrulanmış veri, ürün stok durumu ve dönemsel faktörler sağlandığında zaman serisi çapraz doğrulamasıyla yeniden değerlendirin.
