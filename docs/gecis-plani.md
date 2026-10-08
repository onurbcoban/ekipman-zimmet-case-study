# Geçiş Planı: v1.0 → v2

`v1.0`, `docs_ilk` kararlarına göre netleştirilmiş taban sürümdür. `v2` dalı, `docs/kararlar.md`'deki v2 kararlarını (genişletmeler ve çekirdek düzeltmeleri) faz faz uygular.

**Kurallar**
- Her faz sonunda: testler yeşil, modül demo verisiyle sıfırdan hatasız kurulur, art arda iki güncelleme (`-u`) hatasızdır, faz commit'leri atılır ve "Faz notu" doldurulur.
- Hata düzeltmelerinde test önce kırmızı yanar, düzeltmeyle aynı commit'te yeşile döner.
- Süre biterse son tamamlanan faza kadar olan kısım teslim edilir (bkz. Faz G).
- `main`'e v2 süresince dokunulmaz; v2 en sonda `main`'e ileri sarılır (fast-forward).

## 0. Başlangıç durumu (`main` = `v2` = `1724c3f`)

İlk geçiş planındaki maddelerin durumu:

| Madde | Durum |
|---|---|
| Testlerin gerçek kullanıcılarla çalışması, eksik çekirdek testler, OdooBot | Tamam (22 test) |
| Sapmalar S1–S7 (süresi geçmiş onay filtresi, `calisan_id` koruması, dolu tarihler, `create` koruması, C4 `sudo`, buton görünürlüğü, geçmiş sekmesi) | Tamam |
| Red gerekçesi koruması, demo kaydı 2, `base` bağımlılığı | Tamam |
| Açık talepler filtresi, "Taslağı Sil" (v1.0 sonrası eklendi) | Tamam |
| `int4range` ile eklentisiz `EXCLUDE` kısıtının doğrulanması | Tamam (geçici tabloda denendi) |
| Onayda bitiş koşulu, `calisan_id` kopyalanmaması, C6 sadeleşmesi, `musait` → `bosta` | Faz B |
| Veritabanı kısıtları | Faz C |

## Faz A — Belgelerin birleştirilmesi
**Amaç:** v2 kararları ve senaryoları, `main`'deki kodla doğrulanmış belgelerin üzerine işlenir.
**Değişenler:** `docs/kararlar.md`, `docs/test-senaryolari.md` (main numaraları sabit; v2 senaryoları sona eklendi, B/20 ve B/21–B/34 yeniden numaralandı), bu plan.
**Kabul:** Belgelerde eski adlar (menü, buton, alan) ve çelişki yok.
**Faz notu:** Birleştirme `docs_ilk` ortak ata alınarak bölüm bölüm yapıldı: yalnızca main'in değiştirdiği bölüm main'den, yalnızca v2'nin değiştirdiği v2'den alındı; ikisinin de değiştirdiği 17 bölümde main metnine v2 kararı işlendi.

## Faz B — Çekirdeğin kalanları
**Amaç:** v2'nin çekirdeğe getirdiği dört karar.
**Değişecek yerler:** `zimmet.py` (`action_onayla`'da bitiş koşulu; `calisan_id` `copy=False`; çakışma mesajında role göre dalın kaldırılması), `cihaz.py` ve `cihaz_views.xml` (`musait` → `bosta`, etiket "Zimmette değil", arama filtresi), `kurulum-notlari.md` (demo tarihlerinin sunucu saatiyle hesaplanması notu).
**Testler:** B/20, G/4, C/6, A/1.
**Kabul:** Yukarıdaki genel kabul; demoda çakışma mesajı yetkiliye referans ve tarihleri gösterir.
**Tuzaklar:** `bosta` dönüşümü saklanan bir seçim alanının anahtarını değiştirir; mevcut veritabanında eski değer kalır, doğrulama sıfırdan kurulumla yapılır. Mesajlardaki tarihler sabit biçimle değil, kullanıcının dil biçimiyle (`format_date`) yazılmalı; arayüzdeki tarih alanlarıyla aynı görünür.
**Faz notu:** Dört değişiklik ayrı commit'lerde, her biri önce kırmızı yanan bir testle (`test_23`–`test_27`); 27 test yeşil. Onaydaki bitiş koşulu `@api.constrains` değil `action_onayla` içinde, çünkü kural kaydın her zaman sağlaması gereken bir şey değil, onay anının ön koşulu (onaylı kaydın bitişi zamanla geçebilir). Kopyalama testi, kopyalanan `calisan_id`'nin K2'deki `create` kuralına takıldığını gösterdi; `copy=False` ile kopya, kopyalayanın varsayılan çalışanını alıyor. Çakışma mesajı ve dolu tarihler alanı `format_date` ile kullanıcının dil biçimine bağlandı (Türkçe kullanıcıda gün-ay-yıl, `test_25`, `test_27`). C6'daki mühendis dalı tetiklenemediği (bloklayan geçişleri yalnızca yetkili yapar) için test edilemiyordu; kaldırıldı. Demo tarihlerinin UTC ile hesaplandığı Odoo kaynağında doğrulandı ve kurulum notlarına yazıldı.

## Faz C — Veritabanı kısıtları (C5)
**Amaç:** Eşzamanlı onay ve teslime karşı kesin garanti.
**Değişecek yerler:** `zimmet.py` `init()`: kısmi benzersiz indeks (`IF NOT EXISTS`) ve `pg_constraint` kontrollü `EXCLUDE` kısıtı.
**Testler:** C/9, C/10, C/11, G/2.
**Kabul:** Doğrudan SQL ile yazılan çakışan kayıt reddedilir; `-u` iki kez hatasız; `btree_gist` kurulu değil.
**Tuzaklar:** Testte bütünlük hatası işlemi bozar; SQL denemesi `savepoint` içinde ve `mute_logger('odoo.sql_db')` ile yapılmalı. Demo verisi kısıtlara uymalı (bloklayan kayıtlar çakışmıyor; doğrulanacak).
**Faz notu:** —

## Faz D — Süre uzatma (B9)
**Amaç:** Onaylı veya teslim edilmiş kayıtta ileri tarihli uzatma isteği; yetkili onaylarsa bitiş güncellenir.
**Değişecek yerler:** `zimmet.py` (`istenen_bitis`; `action_uzatma_iste/onayla/reddet/geri_cek`; `write()` kuralları), `zimmet_views.xml` (butonlar, alan, filtre), `menu_views.xml` (Uzatma Bekleyenler), demo kayıt 1 ve 7.
**Testler:** B/21–B/28.
**Kabul:** Demoda kayıt 7'nin uzatması onaylanır, kayıt 1'inki çakışma hatası verir.
**Tuzaklar:** Bugünkü `write()` taslak dışında tarih değişikliğini `sudo`'da da engelliyor; uzatma onayı bu yüzden takılır, kontrol `sudo` dışına alınmalı. Uzatma onayı C2 kısıtını ve Faz C'deki `EXCLUDE` kısıtını tetikler.
**Faz notu:** —

## Faz E — Kullanılabilirlik ve kayıp (A7, B10)
**Amaç:** Bakım, kayıp ve hurda cihazların verilememesi; zimmetteyken kaybın `kayip` durumuyla kapatılması.
**Değişecek yerler:** `cihaz.py` (`mail.thread`, `kullanilabilirlik`, `write()` engeli, onchange uyarısı), `zimmet.py` (`kayip` durumu, `kapanis_notu`, `action_kayip`, kullanılabilirlik kısıtı, `create`/`action_gonder` engeli), görünümler (cihaz listesi ve formu, kayıp butonu, Kullanılamayan Cihaz Onayları menüsü, soluk durumlar), demo (OSC-003, LTP-003, kayıt 15–16).
**Testler:** A/13–A/20, B/29, B/30–B/34, C/12.
**Kabul:** Demoda kayıt 15'in teslimi kullanılabilirlik hatası verir; LTP-003 geçmişinde kayıp kaydı görünür.
**Tuzaklar:** Demo verisinde kullanılabilirlik, zimmet kayıtlarından sonra güncellenmeli; aksi halde yeni kurallar demo kayıtlarını reddeder. `kayip` durumu C4 indeksine ve bloklayan durumlara girmemeli.
**Faz notu:** —

## Faz F — Toplu talep (A6)
**Amaç:** Aynı tarihler için birden çok cihazın tek seferde istenmesi; yetkilinin toplu görmesi ve onaylaması.
**Değişecek yerler:** `wizard/` (`ekipman.zimmet.toplu`), `zimmet.py` (`toplu_ref`), `data/sequence.xml` (`TPL/`), erişim dosyası, liste başlığında toplu onay butonu, arama gruplaması, demo kayıt 13–14.
**Testler:** A/7–A/12.
**Kabul:** Sihirbaz bir geçersiz cihazda hiçbir kayıt oluşturmaz; toplu onayda tek çakışma tüm seçimi geri alır.
**Tuzaklar:** Sihirbaz kayıtları `sudo` ile oluşturur; `uid` değişmediği için çalışan varsayılanı korunur, bu bir testle doğrulanmalı. Toplu talepten geri çekilip taslağa dönen kayıt, sahibi tarafından "Taslağı Sil" ile silinebilir (ek kural gerekmez).
**Faz notu:** —

## Faz G — Kapanış
**Amaç:** Teslime hazır v2.
**İşler:** README ve eğitim dokümanının v2'ye göre güncellenmesi; ekran görüntülerinin son arayüzden alınması; kurulum notlarının gözden geçirilmesi; `v2` → `main` ileri sarma; `v2.0` etiketi.
**Tuzaklar:** Süre yetmezse ve v2 bir faz ortasında bırakılırsa, `kararlar.md` ve README'de uygulanmayan genişletmeler "tasarlandı, uygulanmadı" olarak işaretlenir; ileri sarma son tamamlanan faza kadar yapılır.
**Faz notu:** —
