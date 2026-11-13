# Proje: Armut Hizmet Talebi ve NovaPerakende Satışlarının Zaman Analizi ve Talep Tahmin
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


## Kurulum ve Çalıştırma

Bu proje Docker Compose kullanılarak PostgreSQL, dbt ve Metabase teknolojileriyle geliştirilmiştir. PostgreSQL veri ambarı olarak, dbt veri dönüşümleri ve kalite testleri için, Metabase ise analiz sonuçlarının görselleştirilmesi için kullanılmaktadır.

### 1. Docker Servislerinin Başlatılması

Proje klasörü VS Code üzerinden açılır. Terminalde aşağıdaki komutlar sırasıyla çalıştırılır:

```bash
docker compose up -d warehouse
docker compose up -d metabase
```

Çalışan servislerin durumunu kontrol etmek için:

```bash
docker compose ps
```

PostgreSQL servisinin `healthy`, Metabase servisinin ise `Up` durumunda olması beklenir.

### 2. dbt Veritabanı Bağlantısının Kontrol Edilmesi

dbt'nin PostgreSQL veritabanına bağlanabildiğini doğrulamak için:

```bash
docker compose run --rm project debug
```

Başarılı bağlantı sonucunda `Connection test: [OK connection ok]` ve `All checks passed!` mesajları görüntülenir.

### 3. dbt Modellerinin Çalıştırılması

Veri dönüşüm modellerini çalıştırmak için:

```bash
docker compose run --rm project run
```

Projede toplam 8 dbt dönüşüm modeli bulunmaktadır:

- 3 staging modeli: Ham verilerin temizlenmesi ve analize hazırlanması.
- 2 intermediate modeli: Günlük verilerin düzenlenmesi ve birleştirilmesi.
- 3 mart modeli: Analiz ve raporlama için günlük, aylık ve kategori bazında tabloların oluşturulması.

Yapılan çalıştırma sonucunda 8 modelin tamamı başarıyla oluşturulmuş veya güncellenmiştir.

**Çalıştırma sonucu:** PASS=8, WARN=0, ERROR=0, SKIP=0.

### 4. dbt Veri Kalitesi Testleri

Verilerin doğruluğunu ve tutarlılığını kontrol etmek için:

```bash
docker compose run --rm project test
```

Projede toplam 20 veri kalitesi testi bulunmaktadır.

Bu testler kapsamında:

- `not_null`: Gerekli alanların boş olmaması kontrol edilir.
- `unique`: Belirlenen alanlardaki değerlerin benzersizliği kontrol edilir.
- `assert_nonnegative_demand`: Talep değerlerinin negatif olmaması kontrol edilir.

Gerçekleştirilen testlerde 20 testin tamamı başarıyla geçmiştir.

**Test sonucu:** PASS=20, WARN=0, ERROR=0, SKIP=0.

### 5. dbt Dokümantasyonunun Oluşturulması

dbt modellerinin yapısını, alanlarını ve aralarındaki ilişkileri incelemek için dokümantasyon oluşturulur:

```bash
docker compose run --rm project docs generate
```

Bu işlem sonucunda `dbt/target` klasöründe aşağıdaki dosyalar oluşturulur:

- `index.html`
- `manifest.json`
- `catalog.json`

Dokümantasyonu yerel tarayıcıda görüntülemek için proje ana klasöründe aşağıdaki komut çalıştırılır:

```bash
python -m http.server 8080 --directory dbt/target
```

Dokümantasyon adresi: http://localhost:8080

dbt dokümantasyonundaki Lineage Graph üzerinden ham verilerin staging, intermediate ve mart modellerine dönüşüm süreci görselleştirilmiştir.

### 6. Metabase Dashboard

Projenin analiz ve görselleştirme işlemleri Metabase kullanılarak gerçekleştirilmiştir.

Metabase erişim adresi: http://localhost:3000

**Dashboard adı:** YBS305 - Talep Tahmini ve Satış Analizi

Dashboard üzerinde 2024 yılına ait Armut hizmet talepleri ve NovaPerakende satış verileri analiz edilmektedir.

Dashboard kapsamında 4 KPI göstergesi hazırlanmıştır:

1. Toplam Net Satış: 7.206.829 TL
2. Toplam Armut Hizmet Talebi: 65.732
3. Toplam Satılan Ürün Adedi: 6.046
4. Toplam Sipariş Satırı Sayısı: 2.000

Dashboard üzerinde 5 analiz grafiği bulunmaktadır:

1. 2024 Aylık Net Satış Trendi
2. 2024 Kategori Bazında Net Satışlar
3. 2024 Aylık Armut Hizmet Talebi Trendi
4. 2024 Kategori Bazında Net Satış Dağılımı (%)
5. 2024 Kategori Bazında Satılan Ürün Adetleri

Ayrıca aylık satış ve talep özeti ile aylık kategori bazında net satış analizi için 2 tablo oluşturulmuştur.

### 7. Dashboard Filtreleri

Dashboard üzerinde kullanıcıların verileri etkileşimli olarak inceleyebilmesi için 2 filtre oluşturulmuştur.

**Tarih Aralığı Filtresi:** Kullanıcının belirlediği tarih aralığındaki satış ve hizmet talebi verilerinin incelenmesini sağlar.

**Kategori Filtresi:** Ürün kategorilerine göre satış tutarlarının, satış dağılımının ve satılan ürün adetlerinin incelenmesini sağlar. Bu filtre, kategori alanını içeren ilgili grafik ve analiz tablolarına uygulanmaktadır.

Her iki filtre test edilmiş ve ilgili görsellerde doğru şekilde çalıştığı doğrulanmıştır.

### 8. Veri Akışı ve Sistem Mimarisi

Projenin veri işleme süreci aşağıdaki aşamalardan oluşmaktadır:

1. Armut ve NovaPerakende ham veri dosyalarının alınması.
2. Python ile verilerin temizlenmesi ve günlük toplamlara dönüştürülmesi.
3. Hazırlanan verilerin PostgreSQL veri ambarına aktarılması.
4. dbt staging modelleriyle verilerin analize hazırlanması.
5. dbt intermediate modelleriyle günlük talep bilgilerinin düzenlenmesi ve birleştirilmesi.
6. dbt mart modelleriyle analiz tablolarının oluşturulması.
7. Veri kalitesi testlerinin gerçekleştirilmesi.
8. Metabase dashboard üzerinden sonuçların görselleştirilmesi.
9. Hazırlanan verilerin talep tahmini ve ilişki analizi çalışmalarında kullanılması.

Bu mimari sayesinde veri hazırlama, dönüşüm, doğrulama ve görselleştirme süreçleri birbirinden ayrılmıştır.

### 9. Projenin Teknik Doğrulama Sonuçları

Projenin yerel geliştirme ortamında yapılan kontroller sonucunda:

- Docker Desktop başarıyla çalıştırılmıştır.
- PostgreSQL veri ambarı bağlantısı doğrulanmıştır.
- Metabase servisi çalışır duruma getirilmiştir.
- 8 dbt dönüşüm modeli başarıyla çalıştırılmıştır.
- 20 dbt veri testi başarıyla tamamlanmıştır.
- dbt dokümantasyonu oluşturulmuştur.
- Veri akış şeması görüntülenmiştir.
- Metabase dashboard oluşturulmuş ve filtreleri test edilmiştir.

Bu sonuçlar, projenin veri işleme ve görselleştirme bileşenlerinin yerel ortamda başarıyla çalıştığını göstermektedir.

## Ekip çalışması
Aidana Almas — Veri hazırlama.
Rümeysa Kocatürk ve Zeynep Taşdelen — dbt dönüşümleri ve veri kontrolleri.
Mercan Taşlıtlarla ve Helin Oğur — Dashboard çalışmaları.





