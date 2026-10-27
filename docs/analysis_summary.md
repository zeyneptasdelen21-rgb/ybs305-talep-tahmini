# 2024 Günlük İlişki Analizi

Bu not, 13 Kasım’daki ilk teslim için Armut hizmet kayıtları ile NovaPerakende satışlarının günlük karşılaştırmasını özetler.

## Veri kapsamı

- Armut dosyasında 162.523 satır var; bunların 65.732’si 2024 yılına ait. Gün ve kategori koduna göre toplandığında 1.970 anonim satır oluştu.
- NovaPerakende dosyasında 2024’e ait 2.000 satış satırı bulunuyor. Toplam 6.046 ürün birimi ve 7.206.829,00 TL net satış hesaplandı.
- Karşılaştırma 1 Ocak–31 Aralık 2024 tarihlerini kapsayan 366 günlük takvim üzerinden yapıldı. Perakende dosyasında üç gün için satış satırı yoktu; bu günler seride sıfır olarak yer aldı.
- Temizleme raporunda yinelenen veya geçersiz satır çıkarılmadı.

## Aynı gün hizmet kaydı ve ürün satışı

| Ölçü | Sonuç |
|---|---:|
| Pearson korelasyonu | 0,4028 |
| Spearman korelasyonu | 0,3981 |
| Günlük ortalama Armut kaydı | 179,596 |
| Günlük ortalama satılan ürün | 16,519 |

İki katsayı da 2024 günlük toplamlarında orta düzeyde pozitif eşzamanlı hareket olduğunu gösteriyor. Hesaplama yalnızca aynı günün toplamlarını karşılaştırıyor; mevsim, haftanın günü, genel zaman eğilimi ve günlük gözlemlerin birbirine bağlı olması ayrıca kontrol edilmedi.

Kaynaklarda ortak müşteri, şehir/bölge veya kategori anahtarı yok. Bu yüzden sonuç, hizmet talebinin ürün satışına yol açtığını ya da iki ürün grubunun tamamlayıcı olduğunu göstermez. Bulguyu keşifsel bir ilişki olarak yorumluyoruz.

## Dashboard için satış görünümü

- Satılan birim sayısında ilk üç kategori Elektronik (1.821), Giyim (1.532) ve Ev & Yaşam (1.356).
- Aylık toplamda en yüksek satış Kasımda (847); ardından Aralık (789) ve Ekim (622) geliyor.

Bu sayılar yalnızca elimizdeki 2.000 satış satırını özetliyor. Stokta bulunmayan ürünler, stok miktarı ve tedarik süresi verisi olmadığı için bu sonuçlardan yeniden sipariş miktarı çıkarmıyoruz. Satış satırlarının işletmenin tüm talebini temsil edip etmediği de doğrulanmalı.

## Kaynak ve yeniden üretim

Temizleme sayıları `data/processed/cleaning_report.json` dosyasından alınmıştır. Alan tanımları ve veriyle ilgili diğer uyarılar [veri sözlüğünde](data_dictionary.md) bulunur.

