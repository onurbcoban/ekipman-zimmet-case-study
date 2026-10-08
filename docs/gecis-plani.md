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
| Veritabanı kısıtları | Tamam (Faz C) |
| Güncel Talepler filtresi, zorunlu iptal nedeni, kapanış tarihi | Tamam (Faz C2) |

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
**Değişenler:** `zimmet.py`: `_sql_constraints` ile iki ertelenmiş `EXCLUDE` kısıtı; onay ve teslim sonunda `_kisitlari_simdi_denetle()`.
**Testler:** C/9, C/10, C/11 (`test_28`–`test_30`); G/2 elle.
**Kabul:** Doğrudan SQL ile yazılan çakışan kayıt reddedilir; `-u` iki kez hatasız; `btree_gist` kurulu değil.
**Faz notu:** Planlanan `init()` yerine Odoo'nun `_sql_constraints` mekanizması kullanıldı (tanımı saklar, yalnızca değişince yeniden kurar, ihlali kısıtın mesajıyla gösterir). İlk denemede anlık kısıt dört eski testi kırdı: Python kontrolünün `search()`'ü bekleyen yazmayı veritabanına gönderdiği için kısıt, ayrıntılı Python mesajından önce devreye giriyordu. Doğrudan SQL denendi ve geri alındı: aynı işlemdeki bekleyen değişiklikleri görmediği için olmayan çakışma buldu (test_10). Çözüm ertelenmiş kısıt ve geçiş sonunda `SET CONSTRAINTS ... IMMEDIATE` ile denetimi öne çekmek; `IMMEDIATE` modu işlem sonuna kadar kalıcı olduğu için ardından yeniden `DEFERRED`. İki ayrı bağlantıyla canlandırılan eşzamanlı onayda ikinci işlem `SerializationFailure` ile reddedildi; Odoo'nun tekrar denemesinde Python kontrolü ayrıntılı çakışma mesajını verdi. 30 test yeşil; demo verisi kısıtlara uyuyor.

## Faz C2 — Çekirdek ek: Güncel Talepler ve iptal nedeni (B3)
**Amaç:** Bildirim olmadan kullanıcıyı bilgisiz bırakmamak: kapanan talep bir hafta görünür kalır, her iptalin nedeni yazılır.
**Değişecek yerler:** `zimmet_views.xml` (Güncel Talepler ve Açık Talepler filtreleri aynı grupta, menünün varsayılanı Güncel Talepler; iptal nedeni alanı), `zimmet.py` (`iptal_nedeni`; `action_iptal`'de zorunluluk; `kapanis_tarihi` ve onu yazan kapanış geçişleri: iade, red, iptal; `write()` kuralları, B8 tablosu), demo (kapanış tarihleri ve kayıt 11'in iptal nedeni, H3).
**Testler:** B/36, F/15.
**Kabul:** Genel kabul; demoda yeni reddedilmiş 9 numaralı kayıt Güncel Talepler'de görünür, eski iptal edilmiş 11 numaralı kayıt görünmez.
**Tuzaklar:** "Son 7 gün" `write_date`'e değil kapanış anında bir kez yazılan `kapanis_tarihi`'ne bağlı (B3); filtre ifadesi bugünün tarihini `context_today()` ile almalı. Kayıp geçişi Faz E'de geldiğinde o da kapanış tarihini yazmalı ve "Açık Talepler" ile "Güncel Talepler"in kapalı durum listesine `kayip` eklenmeli.
**Faz notu:** Üç adım, üç kod commit'i, her biri önce kırmızı yanan bir testle (`test_31`–`test_33`); 33 test yeşil. Filtre testi, görünüm dosyasındaki filtre ifadesini okuyup web istemcisinin yaptığı gibi bugüne göre hesaplıyor; böylece testte yeniden yazılmış bir kopya değil, gerçek filtre sınanıyor. Aynı `context_today() - relativedelta(...)` kalıbını Odoo'nun kendi modülleri (`project`, `stock`) de kullanıyor. Demoda dün reddedilen 09 numaralı kayıt Güncel Talepler'de görünüyor, eski iade ve iptaller görünmüyor.

## Faz D — Süre uzatma (B9)
**Amaç:** Onaylı veya teslim edilmiş kayıtta ileri tarihli uzatma isteği; yetkili onaylarsa bitiş güncellenir.
**Değişenler:** `zimmet.py` (`istenen_bitis`; `_uzatma_istegini_denetle()` ile `write()` kuralları; `action_uzatmayi_onayla/reddet/geri_cek`; iade ve iptalde bekleyen isteğin temizlenmesi; tarih kilidinin yalnızca `sudo` dışına uygulanması; `create`'te yalnızca dolu süreç alanlarının reddi), `zimmet_views.xml` (butonlar, bilgi bandı, "İstenen Bitiş" alanı, Uzatma Bekleyenler filtresi), `menu_views.xml` (Uzatma Bekleyenler kuyruğu), demo kayıt 1 ve 7.
**Testler:** B/21–B/26, B/28 (`test_34`–`test_36`); B/27 elle.
**Kabul:** Demoda kayıt 7'nin uzatması onaylanır, kayıt 1'inki çakışma hatası verir.
**Faz notu:** "Uzatma İste" butonu kaldırıldı: Odoo formu butondan önce kaydı kaydettiği için buton, kuralları denetlemeden isteği oluşturmuş olurdu; istek alanın kaydedilmesidir ve kurallar `write()`'ta uygulanır. Tarih kilidi (B5) yalnızca `sudo` dışına uygulanacak şekilde düzeltildi; uzatma onayı tek istisna. Uzatma beklerken kayıt kapanırsa istek kuyrukta asılı kalıyordu; iade ve iptal artık isteği temizliyor. Forma "İstenen Bitiş" eklenince `test_17`'nin form kısmı kırıldı: web istemcisi formdaki boş alanları da gönderdiği için `create` kontrolü mühendisin normal yoldan talep açmasını engelliyordu; kontrol yalnızca dolu değerlere bakacak şekilde düzeltildi (ayrı commit). Eğitim dokümanındaki demo turunda uzatma adımı, iadeden önceye alındı (iade bekleyen isteği temizlediği için). 36 test yeşil.

## Faz E — Kullanılabilirlik, kontrol, kayıp ve hurda (A7, B10)
**Amaç:** Yalnızca kullanılabilir cihaz talep edilir; her iade cihazı kontrole alır; kullanılamaz duruma geçen cihazın mevcut talepleri korunur ve kullanıcıya gösterilir; hurda açık talepleri nedeniyle iptal eder; kayıp zimmet `kayip` durumuyla kapanır.
**Değişecek yerler:**
- `cihaz.py`: `mail.thread`; `kullanilabilirlik` (kullanilabilir, kontrolde, bakimda, kayip, hurda); "Kontrol Tamamlandı", "Bakıma Al", "Kullanılabilir Yap", "Hurdaya Ayır" metotları; zimmetteki cihazın kontrole/bakıma/hurdaya alınma engeli (`write()`); son iadenin bilgileri (saklanmayan hesaplanan alanlar).
- `zimmet.py`: `kayip` durumu ve `action_kayip`; `kullanici_geri_bildirimi`, `kapanis_notu` (İade / Kayıp Notu) kuralları; iade sonrası cihazı kontrole alma; oluşturma, gönderme, onay, teslim ve uzatma onayında kullanılabilirlik kontrolü; cihaz alanının seçim süzgeci; "Cihaz Durumu" alanı ve uyarı bandı.
- Görünümler: cihaz listesi (kullanımdaki cihazlar filtresi, kullanılabilirlik), cihaz formu (butonlar, son iade bilgileri), talep formu (uyarı bandı, cihaz durumu, notlar, kayıp butonu), Onay Bekleyenler'de kullanılabilirlik sütunu, soluk durumlar.
- Menüler: Kontrol Bekleyen Cihazlar, Kullanılamayan Cihaz Onayları.
- Demo: OSC-003 bakımda, LTP-003 kayıp, en az bir cihaz kontrolde; kayıt 15–16.
**Testler:** A/13–A/24, B/29, B/30–B/35, C/3, C/12, E/8, F/16.
**Kabul:** Demoda kontroldeki ve bakımdaki cihazlar talep formunda seçilemez; kayıt 15'in teslimi kullanılabilirlik hatası verir; bir iade sonrası cihaz Kontrol Bekleyen Cihazlar'da görünür; "Hurdaya Ayır" bir cihazın açık taleplerini aşamaya göre nedenleriyle iptal eder ve cihazı arşivler.
**Tuzaklar:**
- Demo verisinde kullanılabilirlik, zimmet kayıtlarından sonra güncellenmeli; aksi halde yeni kurallar demo kayıtlarını reddeder.
- `kayip` durumu bloklayan durumlara ve tek-teslim kısıtına girmemeli (C5).
- İadenin cihazı kontrole alması `test_12`'yi (erken iade sonrası yeni onay) değiştirir: araya "Kontrol Tamamlandı" adımı girer.
- "Hurdaya Ayır" taslakları da iptal eder; bu, kullanıcının taslağı iptal edememesi kuralını (B3) delmemeli — sistem geçişi `sudo` ile yazılır, `action_iptal` taslağı reddetmeye devam eder. İptallerden sonra aktif zimmet kalmadığı için arşivleme (A5) mümkün olur; sıra önemli.
- Cihaz alanının seçim süzgeci yalnızca arayüzü kapatır; sunucu kontrolü ayrıca gerekir (D5).
**Faz notu:** —

## Faz F — Toplu talep (A6)
**Amaç:** Aynı tarihler için birden çok cihazın tek seferde istenmesi; yetkilinin toplu görmesi ve onaylaması.
**Değişecek yerler:** `wizard/` (`ekipman.zimmet.toplu`), `zimmet.py` (`toplu_ref`), `data/sequence.xml` (`TPL/`), erişim dosyası, liste başlığında toplu onay butonu, arama gruplaması, demo kayıt 13–14.
**Testler:** A/7–A/12.
**Kabul:** Sihirbaz bir geçersiz cihazda hiçbir kayıt oluşturmaz; toplu onayda tek çakışma tüm seçimi geri alır.
**Tuzaklar:** Sihirbazın cihaz seçimi yalnızca kullanılabilir cihazları dolu tarihleriyle göstermeli (A7). Sihirbaz kayıtları `sudo` ile oluşturur; `uid` değişmediği için çalışan varsayılanı korunur, bu bir testle doğrulanmalı. Toplu talepten geri çekilip taslağa dönen kayıt, sahibi tarafından "Taslağı Sil" ile silinebilir (ek kural gerekmez).
**Faz notu:** —

## Faz G — Kapanış
**Amaç:** Teslime hazır v2.
**İşler:** README ve eğitim dokümanının v2'ye göre güncellenmesi; ekran görüntülerinin son arayüzden alınması; kurulum notlarının gözden geçirilmesi; `v2` → `main` ileri sarma; `v2.0` etiketi.
**Tuzaklar:** Süre yetmezse ve v2 bir faz ortasında bırakılırsa, `kararlar.md` ve README'de uygulanmayan genişletmeler "tasarlandı, uygulanmadı" olarak işaretlenir; ileri sarma son tamamlanan faza kadar yapılır.
**Faz notu:** —
