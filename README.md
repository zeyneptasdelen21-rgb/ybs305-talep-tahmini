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

## Bölüm 1: İlişki analizi

Bu bölümde günlük Armut hizmet kayıtları ile NovaPerakende ürün satışları arasındaki eşzamanlı ilişki incelenir. Bulgular keşifsel olarak yorumlanır; korelasyon nedensellik veya tamamlayıcı ürün ilişkisi kanıtı sayılmaz. Talep tahmin modeli ve model kartı final çalışmasına bırakılmıştır.

## Ekip çalışması

Ekip üyelerinin sorumlulukları README’deki görev dağılımı bölümünde yer alır. Katkılar GitHub’da kişilerin kendi dallarında açtıkları Pull Request’ler ve commit’ler üzerinden takip edilir.
