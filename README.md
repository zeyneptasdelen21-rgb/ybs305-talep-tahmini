# Armut Hizmet Talebi ve NovaPerakende Satış Analizi

## Problem ve amaç

Perakendecinin hangi dönemlerde ürün talebinin arttığını veya azaldığını görebilmesi, stok planlamasını geçmiş satışlara göre yapmasına yardımcı olur. Projede Armut hizmet talepleri ile NovaPerakende ürün satışlarının zaman içindeki değişimini inceliyor, aralarındaki günlük ilişkiyi değerlendiriyoruz. Perakende talep tahmini ve stok önerileri de projenin genel hedefleri arasında.

**Proje problemimiz:** Armut hizmet talebi ile NovaPerakende ürün satışlarının zaman içindeki değişimini inceleyerek aralarındaki günlük ilişkiyi değerlendirmek; perakende talebini tahmin edip stok planlamasına yönelik öneriler geliştirmek.

## Araştırma sorusu

2024 yılında günlük Armut hizmet kaydı sayısı ile aynı gündeki NovaPerakende satış adedi birlikte değişiyor mu?

İki veri kümesinde ortak müşteri, şehir/bölge veya kategori anahtarı yok. Bu nedenle kayıtları kişi, bölge ya da kategori bazında eşleştirmiyoruz; karşılaştırmayı günlük toplamlar üzerinden yapıyoruz.

## Veri ve hazırlık

Analizde kullandığımız Armut verisi 2024 yılını kapsıyor. Bu döneme ait 65.732 hizmet kaydı gün ve kategori koduna göre toplandığında 1.970 anonim satır elde edildi. NovaPerakende verisi 2024 yılına ait 2.000 satış satırından oluşuyor; günlük toplandığında 366 satırlık bir seri elde ediliyor.

- Temizleme raporunda yinelenen veya geçersiz satır çıkarılmadı. Kimlik alanları ve analize girmeyen ayrıntılar çıktı dosyalarına taşınmadı.
- Kaynakta satır bulunmayan günler sıfır olarak yazıldı. Bu değerler gerçek sıfır talep anlamına gelmeyebilir; veri kapsamı hakkında bir varsayımdır.
- Armut kategori kodlarının ad karşılığı verilmediği için kodları olduğu gibi koruduk.

Temizleme ayrıntıları [veri sözlüğünde](docs/data_dictionary.md), günlük ilişki sonuçları ise [analiz özetinde](docs/analysis_summary.md) yer alıyor.

## Günlük ilişki analizi

Günlük Armut hizmet kayıtları ile NovaPerakende ürün adedi arasındaki Pearson korelasyonu **0,4028**, Spearman korelasyonu **0,3981** olarak hesaplandı. Bu değerler, 2024 günlük toplamlarında orta düzeyde pozitif bir eşzamanlı hareket olduğunu gösteriyor.

Bu sonuç iki verinin birbiriyle ilişkili olduğunu tek başına kanıtlamaz. Ortak müşteri, bölge veya kategori bilgisi bulunmuyor; mevsim, haftanın günü ve genel zaman eğilimleri sonucu etkilemiş olabilir. Bu yüzden korelasyonu keşifsel bir bulgu olarak değerlendiriyoruz; nedensellik ya da tamamlayıcı ürün ilişkisi iddiasında bulunmuyoruz.

## Görev paylaşımı

- **Aidana Almas — Problem ve veri hazırlığı:** Araştırma sorusunu netleştirir; kaynak alanları ve veri kalitesini inceler; ham veriyi temizleyip kimlik bilgilerini analiz çıktılarından çıkarır. Temizleme raporunu ve veri sınırlılıklarını açıklar.
- **Zeynep Taşdelen — dbt ve veri kontrolleri:** Staging, ara model ve mart dönüşümlerini yürütür; en az üç veri testini ve dbt belgelerini kontrol eder.
- **Rümeysa Kocatürk — Dashboard:** Martları kullanarak hizmet kaydı sayısı, satılan ürün adedi ve net satış KPI’larını; en az üç grafik ve tarih filtresini hazırlar. Grafiklerin ne gösterdiğini açıklar. Çıktı olarak `.pbix` dosyası veya yayımlanmış bağlantı sunar.
- **Mercan Taşlıtarla — İlişki analizi:** Günlük ilişki bulgusunu ve sınırlarını doğrular, anlaşılır biçimde raporlar. Tahmin modeli ve model kartı final çalışmasına kalır.
- **Helin Oğur — Kurulum ve ortak dokümantasyon:** Docker ve GitHub Actions kurulumunu ekipte doğrular; README’yi, veri sözlüğünü ve GitHub katkı akışını düzenler.

