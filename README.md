# Proje: Armut Hizmet Talebi ve NovaPerakende Satışlarının Zaman Analizi ve Talep Tahmini

## Problem ve amaç

Bu projede, Armut hizmet talepleri ile NovaPerakende ürün satışlarının 2024 yılı içindeki değişimini günlük toplamlar üzerinden inceliyoruz. İki veri kaynağı arasında günlük bir ilişki olup olmadığını değerlendiriyor; NovaPerakende satış geçmişinden kısa vadeli ürün talebi tahmini üreterek stok planlamasına yönelik öneriler geliştirmeyi amaçlıyoruz. Ayrıca Armut hizmet talebi bilgilerinin ürün talebi tahminine ek katkı sağlayıp sağlamadığını test ediyoruz.

Armut ve perakende verilerinde ortak müşteri, bölge veya kategori eşleştirme alanı bulunmadığından kayıtları bu alanlarda doğrudan birleştirmiyoruz. Günlük ilişki analizini keşifsel olarak yorumluyoruz; korelasyon tek başına nedensellik veya tamamlayıcı ürün ilişkisi kanıtı değildir.

## Veri kaynakları ve hazırlama

Analizde iki kaynak kullanılmıştır:

- **Armut:** 2024 kapsamındaki 65.732 hizmet kaydı, günlük ve hizmet kategorisi kodu düzeyinde toplulaştırılmıştır.
- **NovaPerakende:** 2024’e ait 2.000 satış satırı, günlük ve ürün kategorisi düzeyinde toplulaştırılmıştır.

Ham kaynak dosyalarındaki kullanıcı, hizmet, müşteri ve sipariş kimlikleri analiz tablolarına alınmamıştır. Tarih ve sayısal alanlar kontrol edilmiş; veriler anonim günlük toplamlara dönüştürülmüştür. Kaynakta kayıt bulunmayan günler sıfır olarak gösterilmiştir; bunun gerçekten hiç talep olmadığı anlamına gelmeyebileceği dikkate alınmalıdır.

## Teknoloji ve veri akışı

Veri hazırlama adımları Python ile yürütülür. PostgreSQL veri ambarı Docker Compose ile çalıştırılır; dbt modelleri veriyi staging, ara model ve mart katmanlarından geçirir. dbt testleri temel veri kalitesi kontrollerini yapar. Temiz mart verileri dashboard ve tahmin çalışmasında kullanılır.

## Analiz ve ilk bulgular

Günlük Armut hizmet kayıtları ile NovaPerakende ürün satışları arasındaki eşzamanlı ilişki incelenmiştir. Talep tahmini için NovaPerakende’nin geçmiş satışları ve takvim özellikleri kullanılarak iki algoritma karşılaştırılmış; Armut’un gecikmeli günlük sayımlarının eklenmesinin etkisi ayrıca değerlendirilmiştir.

İlk kronolojik testte en düşük hata, yalnızca perakende geçmişi ve takvim özelliklerini kullanan HistGradientBoosting modelinde elde edilmiştir (MAE: 9,872 adet; WAPE: %38,19). Armut verisini eklemek bu testte tahmin hatasını düşürmemiştir. Bu nedenle mevcut model sonuçları bir ders prototipi olarak değerlendirilmelidir; gerçek satın alma veya stok kararlarında doğrudan kullanılmamalıdır.

## Ekip çalışması

Ekip üyelerinin sorumlulukları README’deki görev dağılımı bölümünde yer alır. Katkılar GitHub’da kişilerin kendi dallarında açtıkları Pull Request’ler ve commit’ler üzerinden takip edilir.



