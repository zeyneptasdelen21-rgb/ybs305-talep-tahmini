# Armut Hizmet Talebi ve NovaPerakende Satışlarının Zaman Analizi ve Talep Tahmini

**Ders:** YBS305 İş Zekâsı ve Veri Madenciliği · 2026–2027 Güz  
**Ekip:** Aidana Almas, Zeynep Taşdelen, Rümeysa Kocatürk, Mercan Taşlıtarla, Helin Oğur  
**Durum:** Yerel çalışan prototip — GitHub yayını ve hocanın ara teslim biçimine göre son paketleme bekliyor.

## 1. İş problemi

Armut hizmet talebi ve NovaPerakende ürün satışlarının zaman içindeki değişimini inceleyerek aralarındaki günlük ilişkiyi değerlendirmek; ayrıca perakende talebini tahmin ederek stok planlamasına yönelik öneriler geliştirmek.

**Araştırma soruları:** (1) 2024'te günlük Armut hizmet kayıt sayısı ile aynı gündeki NovaPerakende ürün satış adedi birlikte değişiyor mu? (2) Armut'un geçmiş günlük hizmet sayıları, takvim ve perakende satış geçmişinin ötesinde ürün talebi tahminine katkı sağlıyor mu? (3) NovaPerakende satış örüntüleri stok planlaması için hangi ölçülü önerileri destekliyor?

> **Yorum sınırı:** Armut dosyasında şehir/bölge ve kategori adları yok; ortak müşteri anahtarı da bulunmuyor. Bu nedenle kayıtları müşteri veya kategori bazında birleştirmiyoruz. İki kaynağı yalnızca günlük toplamlar üzerinden keşifsel olarak karşılaştırıyoruz. İlişki bulgusu nedensellik veya tamamlayıcı ürün kanıtı değildir; Armut özelliğinin tahmine katkısı ayrıca test edilir ve ilk testte iyileşme görülmemiştir. Armut verisinin temsil ettiği coğrafya ve kaynağın kullanım koşulları eğitmenle doğrulanmalıdır.

## 2. El kitabı ve teknoloji kararı

El kitabı dbt Core + dbt-duckdb öneriyor; proje talebi PostgreSQL ve Docker kullanılmasını istiyor. Bu başlangıç sürümü PostgreSQL 16 + dbt-postgres'i Docker içinde çalıştırır. Bu, el kitabındaki örnek depodan bilinçli bir teknoloji sapmasıdır; PostgreSQL kullanımını eğitmenle teyit edin. Dashboard için el kitabındaki alternatiflerden Metabase kullanılır; son entegre ürün için Streamlit uygulaması da bulunur.

## 3. Veri ve temizleme

Girdi dosyalarını `data/raw/` içine koyun. Kaynaklar Git tarafından yok sayılır. `scripts/clean_data.py` yalnızca 2024 kayıtlarını işler; tam satır tekrarlarını ve geçersiz kayıtları eler, tarih ve sayısal alanları doğrular, Armut'u gün+kategori koduna, perakendeyi gün ve gün+kategori düzeyine toplulaştırır. Kullanıcı/müşteri/sipariş kimlikleri ve şehir, ürün, maliyet gibi gereksiz detaylar dbt seed dosyalarına alınmaz. Çıktı `dbt/seeds/` altındaki anonim toplamlardır. Bu anonim seed CSV dosyaları yeniden üretilebilir oldukları için GitHub deposunda tutulur; yeni kaynak veriyi temizledikten sonra seed değişikliklerini commit edin. Özet temizleme sayıları `data/processed/cleaning_report.json` dosyasındadır.

- Kaynak: `armut_data.csv` (162.523 satır; 2018 ve 2024 yılları; 2024 kapsamı 65.732 hizmet kaydı).
- Kaynak: `perakende_satis.xlsx` (2.000 satır; 2024 yılı).
- Temizleme özeti: yinelenen/tarih/satış değeri hatalı satır bulunmadı; Armut 2024 toplamlara 1.970 kategori-gün satırı, perakende 366 takvim-gün satırı üretti.
- **Sıfır günler:** kaynakta satır olmayan günler günlük seriye sıfır olarak eklenir. Bu, gerçekten talep olmadığı anlamına gelmeyebilir; veri kapsamı doğrulanana dek bir varsayımdır.
- Armut kategori kodları sayısal kaynak kodları olarak korunur; isim eşlemesi uydurulmaz.


