# Model kartı — günlük perakende ürün adedi

**Durum:** Başlangıç taslağı; model çalıştırıldıktan sonra ölçümler güncellenecek.

- **Amaç:** Günlük NovaPerakende toplam birim talebi için kısa vadeli 7 günlük gösterim tahmini.
- **Tahmin hedefi:** `retail_units_sold`.
- **Özellikler:** tahmin baz çizgisi için 1 ve 7 gün perakende gecikmesi; önceki 7/28 gün ortalamaları; haftanın günü, ay ve yılın günü. Ek deneyde aynı günlerden kaçınılarak Armut 1/7 gün gecikmeleri eklenir.
- **Algoritmalar:** Random Forest Regressor ve HistGradientBoosting Regressor; her ikisi için perakende-geçmişi baz çizgisi ve gecikmeli Armut değişkenleri eklenmiş deney karşılaştırılır. Canlı tahmin Armut değişkeni olmadan yapılır; bu karşılaştırma ek verinin faydasını keşifsel ölçer.
- **Bölme:** Tarihe göre sıralanmış gözlemlerin ilk %80'i eğitim, son %20'si test; rastgele karıştırma yok.
- **Metrikler:** MAE, RMSE ve WAPE. Test MAE'si düşük algoritma seçilir.
- **Veri:** 2024 yılı, 2.000 kaynak perakende satırı; günlük agregalar.
- **Bilinen sınırlılıklar:** Tek yıllık kısa seri; stok/elde kalmama veya promosyon kayıtları yok; kaynak temsil gücü bilinmiyor; modelde Armut hizmet sayısı kullanılmıyor çünkü coğrafi ve anlamsal eşleşme kanıtı yok. Bu nedenle sonuçlar gerçek sipariş/stok kararlarında kullanılmamalıdır.
- **Etik/gizlilik:** Model anonim günlük agregalarda çalışır; kişi bazında tahmin yapmaz.
- **Yeniden değerlendirme:** Daha uzun ve temsil gücü doğrulanmış veri, ürün stok durumu ve dönemsel faktörler sağlandığında zaman serisi çapraz doğrulamasıyla yeniden değerlendirin.
