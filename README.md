# Armut Hizmet Talebi ve NovaPerakende Satış Analizi

Bu projede Armut hizmet kayıtları ile NovaPerakende satışlarını 2024 yılı için inceliyoruz. İlk teslimde iki kaynağın günlük toplamları arasındaki ilişkiye odaklanıyoruz. Talep tahmin modeli ve model kartı final çalışmasında ele alınacak.

## Araştırma sorusu

2024 yılında günlük Armut hizmet kaydı sayısı ile aynı gündeki NovaPerakende satış adedi birlikte değişiyor mu?

İki veri kümesinde ortak müşteri, şehir/bölge veya kategori anahtarı yok. Bu nedenle kayıtları kişi, bölge ya da kategori bazında eşleştirmiyoruz; karşılaştırmayı günlük toplamlar üzerinden yapıyoruz.

## Veri ve hazırlık

Kullandığımız dosyalar 2018 ve 2024 yıllarını kapsayan Armut kayıtları ile 2024 NovaPerakende satışlarıdır. Analizi yalnızca 2024 verileriyle yaptık.

- Armut dosyasındaki 162.523 satırın 65.732’si 2024 yılına ait. Temizleme sonrasında kayıtlar gün ve kategori koduna göre toplandı; 1.970 anonim satır elde edildi.
- NovaPerakende dosyasında 2.000 satış satırı bulunuyor. Bunlar gün bazında toplandığında 366 satırlık bir seri oluşuyor.
- Temizleme raporunda yinelenen veya geçersiz satır çıkarılmadı. Kimlik alanları ve analize girmeyen ayrıntılar çıktı dosyalarına taşınmadı.
- Kaynakta satır bulunmayan günler sıfır olarak yazıldı. Bu değerler gerçek sıfır talep anlamına gelmeyebilir; veri kapsamı hakkında bir varsayımdır.
- Armut kategori kodlarının ad karşılığı verilmediği için kodları olduğu gibi koruduk.

Temizleme ayrıntıları [veri sözlüğünde](docs/data_dictionary.md), günlük ilişki sonuçları ise [analiz özetinde](docs/analysis_summary.md) yer alıyor.

## İlk teslim: günlük ilişki

Günlük Armut hizmet kayıtları ile NovaPerakende ürün adedi arasındaki Pearson korelasyonu **0,4028**, Spearman korelasyonu **0,3981** olarak hesaplandı. Bu değerler, 2024 günlük toplamlarında orta düzeyde pozitif bir eşzamanlı hareket olduğunu gösteriyor.

Bu sonuç iki verinin birbiriyle ilişkili olduğunu tek başına kanıtlamaz. Ortak müşteri, bölge veya kategori bilgisi bulunmuyor; mevsim, haftanın günü ve genel zaman eğilimleri sonucu etkilemiş olabilir. Bu yüzden korelasyonu keşifsel bir bulgu olarak değerlendiriyoruz; nedensellik ya da tamamlayıcı ürün ilişkisi iddiasında bulunmuyoruz.

## Veri akışı

Kaynak dosyalar yerel `data/raw/` klasöründe tutulur. `scripts/clean_data.py` dosyaları temizleyip anonim toplamlara dönüştürür. Bu çıktılar dbt seed’lerine yüklenir; PostgreSQL üzerinde staging, ara model ve mart katmanlarından geçer. Dashboard günlük ve kategori martlarını kullanır.

Ham dosyalar GitHub’a eklenmez. Dashboard’ın son teslimi, çalışan bir `.pbix` dosyası veya paylaşılabilir yayımlanmış bağlantı olmalıdır.

## Görev paylaşımı

Aşağıdaki dağılım, 13 Kasım teslimi için önerilen sorumlulukları gösteriyor. Bir dosyanın depoda bulunması, listedeki kişinin o işi tamamladığını tek başına göstermez; katkılar kişisel dal, Pull Request ve commit’lerle takip edilir.

- **Aidana Almas — Problem ve veri hazırlığı:** Araştırma sorusunu netleştirir; kaynak alanları ve veri kalitesini inceler; ham veriyi temizleyip kimlik bilgilerini analiz çıktılarından çıkarır. Temizleme raporunu ve veri sınırlılıklarını açıklar.
- **Zeynep Taşdelen — dbt ve veri kontrolleri:** Staging, ara model ve mart dönüşümlerini yürütür; veri testlerini ve dbt belgelerini kontrol eder.
- **Rümeysa Kocatürk — Dashboard:** Martları kullanarak hizmet kaydı sayısı, satılan ürün adedi ve net satış KPI’larını; en az üç grafik ve tarih filtresini hazırlar. Çıktı olarak `.pbix` dosyası veya yayımlanmış bağlantı sunar.
- **Mercan Taşlıtarla — İlişki analizi:** Günlük ilişki bulgusunu ve sınırlarını doğrular, anlaşılır biçimde raporlar. Tahmin modeli ve model kartı final çalışmasına kalır.
- **Helin Oğur — Kurulum ve ortak dokümantasyon:** Docker ve GitHub Actions kurulumunu ekipte doğrular; README’yi, veri sözlüğünü ve GitHub katkı akışını düzenler.

