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

## 4. Başlangıç kurulumu (VS Code + Docker + dbt)

Önkoşul: Git, Docker Desktop ve VS Code. VS Code'da önerilen eklentiler `.vscode/extensions.json` içindedir.

1. Depoyu klonlayın ve VS Code ile açın. Ekipte bir kişi GitHub'da depoyu oluşturur; diğerleri `git clone <repo-url>` ile kendi bilgisayarına alır.
2. İki verilen kaynak dosyayı yerel `data/raw/` klasörüne koyun. Ham dosyalar `.gitignore` nedeniyle GitHub'a gitmez.
3. Docker imajını hazırlayın; PostgreSQL ve Metabase'i açın:

   ```bash
   docker compose build project
   docker compose up -d warehouse metabase
   ```

4. Kaynakları temizleyip anonim dbt seed'lerini oluşturun:

   ```bash
   docker compose run --rm --entrypoint python project /workspace/scripts/clean_data.py
   ```

5. dbt projesini çalıştırın. `dbt seed` CSV toplulaştırmalarını PostgreSQL'e yükler; `dbt build` seed, modeller ve dbt testlerini çalıştırır:

   ```bash
   docker compose run --rm project debug
   docker compose run --rm project seed --full-refresh
   docker compose run --rm project build
   docker compose run --rm project docs generate
   ```

6. Metabase'i tarayıcıda açın: `http://localhost:3000`. İlk kurulum sihirbazında yerel kullanıcı oluşturun. **Add database → PostgreSQL** ile bağlanın: host `warehouse`, port `5432`, database `retail_analytics`, username `analyst`, password `local_dev_only`. Bağlantıdan sonra `analytics` şemasını seçin. `mart_monthly_demand` ve `mart_retail_category_daily` üzerinden en az 3 KPI (hizmet talebi, ürün adedi, net satış), 3 grafik (aylık talep karşılaştırması, kategori bazında satış, net satış eğilimi) ve tarih filtresi ekleyip bir dashboard olarak kaydedin. Bu yerel kurulum Metabase'in geliştirme amaçlı H2 uygulama deposunu kullanır; sunucuda canlı kullanım için üretim veritabanına taşınmalıdır.

7. Mart tablosunu Streamlit entegre uygulamasının okuyacağı anonim CSV'ye dışa aktarın:

   ```bash
   docker compose run --rm --entrypoint python project /workspace/scripts/export_marts.py
   ```

8. Model karşılaştırmasını ve entegre Streamlit uygulamasını çalıştırın:

   ```bash
   docker compose run --rm --entrypoint python project /workspace/model/train.py
   docker compose run --rm -p 8501:8501 --entrypoint streamlit project run /workspace/app/app.py --server.address 0.0.0.0
   ```

   Tarayıcı: `http://localhost:8501`. dbt docs için `docker compose run --rm -p 8080:8080 project docs serve --host 0.0.0.0 --port 8080` komutu kullanılabilir.

9. İş bitince `docker compose down` ile servisleri kapatın. Yerel veritabanlarını ve Metabase dashboard ayarlarını da silmek isterseniz `docker compose down -v` kullanın; bu komut veritabanı hacimlerini kalıcı olarak kaldırır.

### PostgreSQL kimlik bilgileri

Yerel geliştirme için Compose dosyasındaki `analyst/local_dev_only` kullanılır; internete açık veritabanına açmayın. GitHub Actions ayrı geçici test kimlik bilgileri kullanır. Gerçek bir sunucuya geçerken parolayı ortam değişkeni/secret ile yönetin.
Host makineden pgAdmin gibi bir araçla bağlanırken `localhost:5434` kullanılır; Docker içindeki dbt ve Metabase `warehouse:5432` adresini kullanır. Bu port ayrımı, bilgisayarda 5432 ve 5433'ü kullanan mevcut servis/container'lara dokunmamak içindir.

## 5. dbt katmanları

- `dbt/seeds/`: temizlenmiş, anonim CSV agregaları.
- `models/staging/`: kaynak tip dönüşümleri ve staging isimleri.
- `models/intermediate/`: Armut günlük toplaması ve iki veri akışının takvim tarihiyle tam dış birleştirmesi.
- `models/marts/`: dashboard/model için günlük, aylık ve perakende kategori martları.
- `tests/`: benzersizlik, null ve negatif talep kontrolleri.

Bu yapı en az üç dönüşüm modelini ve birden çok dbt testini içerir. Mart çıktıları `analytics` şemasında oluşur.

## 6. Dashboard ve tahmin

Metabase ara teslim panosunda üç KPI (hizmet kaydı, ürün adedi, net satış), üç grafik ve tarih filtresi kurulur. Streamlit son uygulamasında bunlara ek olarak günlük perakende talep modeli bulunur. Tahmin hedefi ürün adedidir; baz model önceki 1/7/28 gün satışları ve takvim alanlarını kullanır. Random Forest ve HistGradientBoosting kronolojik test aralığında MAE, RMSE ve WAPE ile karşılaştırılır; ayrıca gecikmeli Armut sayımlarının ek faydası denenir. İlk ölçümde en düşük MAE, HistGradientBoosting perakende-geçmişi baz modelindeydi (MAE 9,872; RMSE 13,560; WAPE %38,19). Armut gecikmelerini eklemek hatayı düşürmedi. Bu sonuçlar ve veri sınırları [analiz özetinde](docs/analysis_summary.md); model amacı ve kartı [model kartında](docs/model_card.md). Eğitim verisi yalnızca 2024 ve 2.000 kaynak satış satırı olduğu için tahmin bir ders prototipidir; güncel satın alma/stok kararı olarak kullanılmamalıdır.

## 7. GitHub'da grup çalışması ve raporlama

1. Bir ekip üyesi GitHub'da **Public** depo oluşturur (ders el kitabı herkese açık repo istiyor); oluştururken README, `.gitignore` veya lisans ekletmeyin, çünkü bunlar bu başlangıç klasöründe zaten var. Bu klasörü GitHub'a ilk kez gönderecek kişi terminalde proje klasöründeyken şu komutları çalıştırır:

   ```bash
   git init -b main
   git add .
   git status --short
   git commit -m "chore: initialize YBS305 project"
   git remote add origin https://github.com/<kullanici-adi>/<repo-adi>.git
   git push -u origin main
   ```

   `git status --short` çıktısında ham dosya veya müşteri/sipariş kimliği olan dosya görünürse durun ve `.gitignore` düzeltin. Diğer ekip üyeleri bu repoyu `git clone <repo-url>` ile indirir. `.gitignore` ham dosyaları dışarıda tutar.
2. Beş kişilik ekipte depo sahibi kendi hesabıyla birlikte toplam beş kişi olur. Depo sahibi **Settings → Collaborators → Add people** bölümünden diğer dört kişiyi GitHub kullanıcı adlarıyla tek tek davet eder. Davetlilerin her biri e-posta/GitHub bildirimindeki daveti kabul eder; kabul ettikten sonra repoya yazma erişimiyle katkı yapabilir. Ayrı bir GitHub Organization açmak zorunlu değildir.
3. Her iş `feature/<kisa-ad>` dalında yapılır. Küçük ve açıklayıcı commit'ler atılır; ör. `feat(dbt): add daily demand mart`. Değişiklikler Pull Request ile `main` dalına alınır. En az bir ekip arkadaşı PR'ı inceler; herkeste ayrı ve görünür katkı geçmişi kalır.
4. İlk kurulumdan sonra GitHub Actions PR üzerinde PostgreSQL açıp `dbt seed` ve `dbt build` çalıştırır. Yeşil kontrol, model ve dbt testlerinin geçmesi demektir.
5. Ara rapor için GitHub Releases/etiket (`v0.1-section-1`), README'deki kurulum ve dashboard ekran görüntüsü; final rapor için model kartı, metrikler, sınırlılıklar ve canlı uygulama bağlantısı eklenir.
6. Ham kaynak veriyi, müşteri/sipariş kimliklerini, parola veya `.env` dosyasını GitHub'a yüklemeyin. Kaynak atıflarını ve verinin izin/lisans bilgisini `docs/data_dictionary.md` içinde tamamlayın.

### Canlı Streamlit yayını

GitHub deposu hazır ve anonim `app/data/mart_daily_demand.csv` dosyası eklendikten sonra Streamlit Community Cloud'da **New app** ile bu repoyu, `main` dalını ve `app/app.py` giriş dosyasını seçin. Yayınlanan URL'yi README'ye yazın. Ham kaynak dosyaları bu yayına veya GitHub'a eklenmez.

### Ekip sorumlulukları (öneri)

| Kişi | Birincil sorumluluk | Kanıt/teslim |
|---|---|---|
| Aidana Almas | Ürün sorumlusu, kaynak/veri temizleme | Problem tanımı, veri kalite özeti, PR incelemesi |
| Zeynep Taşdelen | dbt staging ve kalite testleri | staging modelleri, schema testleri, dbt docs |
| Rümeysa Kocatürk | Martlar ve dashboard | mart SQL'leri, KPI/grafikler, filtre |
| Mercan Taşlıtarla | Tahmin ve model kartı | iki algoritma, zaman sıralı değerlendirme, sınırlılıklar |
| Helin Oğur | Docker/GitHub Actions, entegrasyon ve rapor | kurulum, CI, README ve final yayın kontrolü |

**Grup:** Eğitmen beş kişilik ekibi onayladı. Beş kişi aynı GitHub reposunda çalışacak; repo sahibi diğer dört ekip üyesini collaborator olarak davet edecek.

## 8. Teslim takvimi ve kontrol listesi

- **Bölüm 1 — 13 Kasım 2026:** kaynak ve iş problemi; en az üç dönüşüm modeli ve üç dbt testi; etkileşimli pano (3 KPI, 3 görsel, filtre); README, veri sözlüğü ve dbt docs.
- **Bölüm 2 — 25 Aralık 2026:** dbt martından özellik üretimi; en az iki algoritma ve uygun metriklerle değerlendirme; çalışan herkese açık uygulama; model kartı ve entegre ürün.
- Kaynak kapsamı/kullanım izni teyit edildi.
- Ham veri GitHub dışında, anonim martlar tekrar üretilebilir.
- `dbt build` ve Actions başarılı.
- Dashboard/filtre ve iki model metrikleri gösteriliyor.
- Uygulama canlı bağlantısı README'de; canlı yayın ve hesap bağlantısı ekip tarafından tamamlandı.

## 9. Sonraki yapılacaklar

- El kitabının DuckDB önerisi yerine PostgreSQL kullanımı için eğitmen onayı alın.
- Armut kaynağının coğrafi kapsamını, kategori sözlüğünü ve lisansını belgeleyin.
- NovaPerakende satış verisinin sentetik mi/gerçek mi olduğunu ve her satırın satış satırı mı sipariş mi olduğunu doğrulayın.
- Gerçek stok planlamasına geçmeden önce daha uzun satış geçmişi, ürün bazında stok/elde kalmama bilgisi ve iş birimi onayı alın. Streamlit Community Cloud için `app/data/mart_daily_demand.csv` anonim mart çıktısını ürettikten sonra repoya ekleyin; ham dosyaları hiçbir aşamada eklemeyin.
