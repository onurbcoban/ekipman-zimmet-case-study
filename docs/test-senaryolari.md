# Ekipman Zimmet Modülü Test Senaryoları

## A Bölümü - Veri Modeli
1. **Fiziksel durum hesaplaması:** Cihaz teslim edilince durum "Zimmette", iade alınınca "Şu an müsait" olur. Yalnızca `onaylandi` durumundaki kayıt fiziksel durumu değiştirmez (A3).
2. **Çalışanı olmayan kullanıcı:** Bağlı çalışan kaydı olmayan kullanıcı talep açmaya çalışırsa `UserError` alır (A4).
3. **Başkası adına talep:** Mühendis RPC ile başka bir çalışanı `calisan_id` olarak vererek talep oluşturmaya çalışırsa hata verir; kendi çalışanını açıkça vererek oluşturursa kayıt oluşur. Oluşmuş kaydın `calisan_id` alanı RPC ile değiştirilemez (A4, D3, B8).
4. **Silme kısıtı:** Geçmiş zimmet kaydı olan cihaz veya çalışan silinemez (A5).
5. **Cihaz arşivleme:** Aktif zimmeti (`onaylandi` veya `teslim_edildi`) olan cihaz arşivlenemez; aktif zimmeti olmayan cihaz arşivlenebilir (A5).
6. **Çalışan arşivleme:** Teslim edilmiş zimmeti olan çalışan arşivlenebilir; zimmet kayıtları korunur ve geciken listesinde görünmeye devam eder (A5).

## B Bölümü - Süreç Akışı ve Geçişler
1. **Mutlu yol:** Mühendis taslak oluşturur, gönderir (talep_edildi), yetkili onaylar (onaylandi), aralığı gelince teslim eder (teslim_edildi), iade alır (iade_edildi). Fiili tarihler butonlarla yazılır.
2. **Kendi talebini onaylama:** Yetkili, kendi talebini başarıyla onaylayabilir (B7).
3. **Gerekçesiz red:** Yetkili `red_gerekcesi` alanını doldurmadan reddetmeye çalışırsa `UserError` verilir (B3). Gerekçeli red geçer ve mühendis sebebi kendi listesinde görür.
4. **Erken teslim:** Başlangıç tarihi henüz gelmemiş onaylı talep için "Teslim Et" `UserError` verir (B4).
5. **Aralığı geçmiş onaylı teslim:** Bitiş tarihi geçmiş onaylı kayıt teslim edilmeye çalışılırsa `UserError` verilir (B4).
6. **Teslim edilmiş kaydı iptal:** `teslim_edildi` durumundaki kayıt iptal edilmeye çalışılırsa hata verir; yalnızca iade alınabilir (B3).
7. **Yetkisiz geçiş (RPC):** Mühendis, arayüzde gizlenen `action_onayla` veya `action_teslim_et` metotlarını RPC/Python shell ile çağırırsa rol kontrolünden `AccessError` alır (B8).
8. **Son durumdan çıkış:** `iade_edildi`, `reddedildi` veya `iptal` durumundaki kayıt tekrar bir aktif duruma geçirilemez (B5).
9. **Geri çekme:** Mühendis bekleyen talebi geri çeker, düzenler ve tekrar gönderir (B5).
10. **Onaylı talebi geri çekme:** `onaylandi` durumundaki kayıt geri çekilemez, hata verir (B5).
11. **Başkasının talebini geri çekme:** Talebin sahibi olmayan kullanıcı (yetkili dahil) `action_geri_cek` çağırırsa hata alır (B2).
12. **Taslak silme:** Taslak kayıt silinebilir; gönderilmiş kayıt silinemez (mühendis ve yetkili için) (B3).
13. **Durumun doğrudan yazılması:** Mühendis RPC ile `state: 'onaylandi'` yazmaya çalışırsa hata alır (B8).
14. **Onaylı kayıt oluşturma:** Mühendis RPC ile `state: 'onaylandi'` içeren kayıt oluşturmaya çalışırsa hata alır (B8).
15. **Onaylı kaydı değiştirme:** Onaylı kaydın cihazı veya tarihi RPC ile değiştirilmeye çalışılırsa hata verir (B5).
16. **Chatter izlenebilirliği:** Onay sonrası chatter kaydında onaylayan kullanıcı görünür; geçişler `sudo()` ile yazılsa da kayıt gerçek kullanıcıyı gösterir (B7).
17. **Reddedilen talep akışı:** Yetkili tarihi yanlış talebi gerekçeyle reddeder, mühendis doğru tarihlerle yeni talep açar (B2, B3).
18. **Geçmiş tarihli talep:** Başlangıç tarihi bugünden önce olan taslak gönderilemez ve taslak kalır; bugün başlayan talep gönderilebilir. Taslak geçmiş tarihle kaydedilebilir, tarih düzeltilip gönderilir (B2).
19. **Red gerekçesinin sunucu kontrolü:** Mühendis RPC ile `red_gerekcesi` yazamaz; yetkili de onaylanmış veya reddedilmiş bir talebin gerekçesini sonradan değiştiremez (B3, D5).

## C Bölümü - Çakışma ve Takvim Kontrolleri
1. **İki çakışan bekleyen talep:** İlk onay geçer, ikincisi onaylanırken hata verir (C1, C2).
2. **Sınır günü:** Bir kayıt 10'unda biter, diğeri 10'unda başlar. Çakışma hatası beklenir (C3).
3. **Erken iade:** İade edilen kayıt takvimi bloklamaz, kalan günler için yeni talep onaylanabilir (C1).
4. **Gecikmiş cihaz:** Sonraki rezervasyon onaylanır, ancak "Teslim Et" aşamasında iade kaydı alınmadığı için hata verir (C4).
5. **Onaylı kaydın tarihini değiştirme:** Arayüz veya RPC üzerinden çakışacak şekilde değiştirme B5 hatasıyla durur. `sudo` ortamında (Odoo shell) aynı değişiklik yapılırsa C2 `constrains` çakışmayı yakalar (C2).
6. **Çakışma mesajı:** Yetkili çakışan bir onayı denediğinde hata mesajında çakışan kaydın referansı ve tarihleri görünür. Bloklayan duruma geçmeye çalışan mühendis çakışma kontrolüne ulaşmadan rol kontrolünden yetki hatası alır (C6, B8).
7. **Ters aralık:** Bitiş tarihi < başlangıç tarihi seçilirse hata verir (C3).
8. **Kendi kaydını dışlama:** Onaylı bir kayıt, değişiklik yapılmadan tekrar kaydedildiğinde kendiyle çakışma hatası vermez (C2).

## D Bölümü - Roller ve Güvenlik
1. **Mühendis görünürlüğü:** Mühendis yalnızca kendi zimmet kayıtlarını listeler; başkasının kaydı görünmez (D2).
2. **Ekipman yönetimi:** Mühendis ekipman veya kategori oluşturmaya çalışırsa hata alır; ekipmanı salt okunur görür ve talep formunda cihaz seçebilir (D4).
3. **Kimde bilgisi:** Mühendis "şu an kimde" alanını ve geçmiş sekmesini göremez; yetkili görür (D6).
4. **Yetkili görünürlüğü:** Yetkili tüm zimmet kayıtlarını görür; yönetici kullanıcı Yetkili grubundadır (D1, D5).
5. **Yetkili haklarının kapsamı:** Yetkili, mühendisin yapabildiği her işlemi (kendi adına talep açma) yapabilir (D1).

## E Bölümü - Kimde, Geçmiş, Gecikme, Dolu Tarihler
1. **Şu an kimde:** Teslim sonrası cihazın "kimde" alanı teslim alan çalışandır; iade sonrası boşalır (E1).
2. **Geçmiş:** Cihaz geçmişinde yalnızca teslim edilmiş ve iade edilmiş kayıtlar görünür; reddedilen ve iptal edilenler görünmez (E2).
3. **Geciken filtresi:** Teslim edilmiş ve bitişi geçmiş kayıt "Geciken" filtresinde ve menüsünde çıkar (E3).
4. **Süresi geçmiş onay:** Bitişi geçmiş ve hiç teslim edilmemiş onaylı kayıt "Süresi geçmiş onay" filtresinde çıkar (E3).
5. **Dolu tarihler:** Onaylı kaydın aralığı mühendisin formunda görünür, isim ve referans görünmez. Bekleyen talebin aralığı ve bitişi geçmiş aralıklar görünmez (E4).
6. **Gecikmiş cihaz:** Gecikmiş cihaz dolu tarihlerde "şu an elde, iade bekleniyor" olarak görünür (E4).
7. **Form görünürlüğü:** Dolu tarihler alanı talep formunda yalnızca taslak durumunda görünür (E4).
## F Bölümü - Ekranlar ve Menüler
1. **Menü görünürlüğü:** Yetkili hesabında Zimmet Talepleri, Onay Bekleyenler, Teslim Bekleyenler, Gecikenler, Süresi Geçmiş Onaylar, Ekipmanlar ve Kategoriler görünür. Mühendis hesabında yalnızca Zimmet Talepleri ve Ekipmanlar görünür (F1).
2. **Kuyruk içerikleri:** Onay Bekleyenler yalnızca `talep_edildi`, Teslim Bekleyenler yalnızca `onaylandi` kayıtları listeler. Kuyruk menüsü ilgili filtreyi arama çubuğunda etiket olarak açar; filtre kaldırılınca tüm kayıtlar görünür (F1).
3. **Buton görünürlüğü:** Taslakta sahibinde Talep Et ve İptal Et; bekleyen talepte sahibinde Geri Çek, yetkilide Onayla ve Reddet; onaylı talepte yetkilide Teslim Et; teslim edilmişte yetkilide İade Al; kapalı durumlarda (iade, red, iptal) hiçbir buton görünmez. Yetkili başkasının taslağını açtığında Talep Et, bekleyen talebinde Geri Çek görünmez (F2).
4. **Statusbar:** Statusbar'a tıklanarak durum değiştirilemez (F2, B8).
5. **Çalışan alanı:** Talep formunda çalışan kullanıcının kendi adıyla dolu ve düzenlenemezdir (F2, A4).
6. **Fiili tarihler:** Fiili tarih alanları taslakta ve onaylı durumda gizlidir, teslimden sonra salt okunur görünür (F2).
7. **Red gerekçesi alanı:** Yalnızca yetkiye ve yalnızca bekleyen talepte düzenlenebilir; reddedilen talepte salt okunur görünür; boşken Reddet hata verir (F2, B3).
8. **Liste vurgusu:** Geciken satır kırmızı, süresi geçmiş onay sarı, bekleyen talep mavi, kapalı durumlar soluk görünür; sıralama planlanan başlangıca göre azalandır (F3).
9. **Ekipman ekranı:** Ekipman listesinde "şu an kimde" kolonu yetkide görünür, mühendiste görünmez. Ekipman formunda "Geçmiş" sekmesi yalnızca yetkide görünür (F4, D6).
10. **Görünüm türleri:** Zimmet ve ekipman modelleri yalnızca liste ve form görünümü sunar; takvim, pivot ve kanban yoktur (F5).
11. **Arama ve gruplama:** Referans, cihaz ve çalışana göre arama çalışır; Onay Bekleyenler, Teslim Bekleyenler, Gecikenler ve Süresi Geçmiş Onaylar filtreleri doğru kayıtları getirir; cihaz, çalışan ve duruma göre gruplama çalışır (F6).
12. **Arayüz dili:** Menüler, alan etiketleri, butonlar ve hata mesajları Türkçedir (F7).

## G Bölümü - Mimari ve Kurulum
1. **Temiz kurulum:** Boş bir veritabanında modül kurulur; log'da `ERROR` veya modülümüze ait uyarı çıkmaz. Bağımlılık olarak yalnızca `mail` ve `hr` istenir (G2, G4, G9).
2. **Yükleme sırası:** Modül ilk kurulumda ve güncellemede (`-u`) hatasız yüklenir; demo açık ve demo kapalı veritabanlarında kurulur (G4).
3. **Referans numarası:** Yeni kayıt `ZMT/0001` biçiminde ad alır, ardışık kayıtlarda numara artar. Mühendis hesabıyla kayıt oluşturulunca da numara atanır (sıra yetkisi) (G5).
4. **Kopyalama:** Bir kayıt kopyalanınca yeni referans numarası alır, eskisini taşımaz (G5).
5. **Chatter:** Durum değişiklikleri chatter'da kullanıcı ve zamanla izlenir; aktivite planlama kullanılmaz (G6, B7).
6. **Benzersizlik:** Aynı etiket no ikinci bir cihaza verilirse anlaşılır bir hata alınır; seri no boş bırakılabilir (G7).
7. **Adlandırma:** Kodda Odoo'nun kendi adları dışında İngilizce tanımlayıcı kalmamıştır (örneğin zimmet modelinde `calisan_id` yerine İngilizce isim olmamalıdır). Elle tarama veya `grep` ile kontrol edilir (G3).
8. **Manifest:** Modül Uygulamalar listesinde uygulama olarak görünür, özet metni ve sürümü doğrudur (G9).
9. **Otomatik testler:** Modülün testleri komut satırından çalıştırılır ve geçer; temiz bir veritabanında tekrar çalıştırılabilir (G8).

## H Bölümü - Demo Verisi
1. **Demo kullanıcılar:** Beş demo kullanıcı kendi parolasıyla giriş yapar; her birinin bağlı bir çalışan kaydı ve doğru grubu vardır; yönetici kullanıcı Yetkili grubundadır (H1, D1).
2. **Ekipman:** Üç kategori ve altı cihaz yüklenmiştir (H2).
3. **Kayıtlar:** On iki zimmet kaydı doğru durum ve tarihlerle yüklenmiştir; cihazların fiziksel durumu ve "şu an kimde" bilgisi doğru hesaplanmıştır (örneğin OSC-001 Zimmette ve kimde Defne) (H3, E1).
4. **Göreli tarihler:** Veritabanı farklı bir günde yeniden oluşturulunca gecikmiş ve süresi geçmiş kayıtlar yine gecikmiş görünür, bugünü kapsayan onay yine bugünü kapsar (H4).
5. **Demo kapalı veritabanı:** Demo kapalı oluşturulan veritabanında modül kurulur; gruplar ve yapı gelir, senaryo kayıtları gelmez (H5).
6. **Sunum akışı:** H6'daki beş adım sırayla hatasız tamamlanır; her adımda beklenen hata ve sonuçlar görülür (H6).
7. **Çakışan talepler:** 3 ve 4 numaralı bekleyen talepten biri onaylanır, diğeri onaylanmaya çalışılınca çakışma hatası verir (H3, C2).
8. **Gecikmiş cihazın teslim hatası:** 2 numaralı kaydın aralığı bugünü kapsar; yetkili "Teslim Et"e basınca hata teslim zamanlaması kuralından (B4) değil, cihaz hâlâ 1 numaralı kayıtta olduğu için C4'ten gelir ("Önce iade alınması gerekir") (H3, C4).

## Otomatik / elle ayrımı (G8)
Aşağıdaki senaryolar `ekipman_zimmet/tests/test_zimmet.py` içindeki testlerle otomatik doğrulanır. Testler mühendis ve yetkili kullanıcılarıyla (`with_user`) çalışır. Diğer senaryolar elle denenir.

| Senaryo | Test |
|---|---|
| A/2 | `test_07_calisan_profili_olmayan_kullanici` |
| A/3 | `test_06_baskasi_adina_talep_acma_engeli`, `test_08_calisan_id_degistirilemez`, `test_17_create_korumalari` |
| B/1 | `test_12_erken_iade` (gönder, onayla, teslim et, iade al) |
| B/2 | `test_01_tarih_cakismasi` (yetkili kendi talebini onaylar) |
| B/3 | `test_02_red_gerekcesi` |
| B/11 | `test_15_geri_cekme_yetkisi` |
| B/12 | `test_03_unlink_kisiti`, `test_04_muhendis_taslak_unlink` |
| B/13 | `test_14_state_dogrudan_yazilamaz` |
| B/14 | `test_17_create_korumalari` |
| B/16 | `test_20_chatter_onaylayani_gosterir` |
| B/18 | `test_16_gecmis_tarihli_talep_gonderilemez` |
| B/19 | `test_09_red_gerekcesi_yetki_kontrolu`, `test_18_red_gerekcesi_yalnizca_bekleyen_talepte` |
| C/1 | `test_01_tarih_cakismasi` |
| C/2 | `test_11_sinir_gunu` |
| C/3 | `test_12_erken_iade` |
| C/4 | `test_13_gecikmis_cihaz_teslim` |
| E/2, E/6 | `test_10_gecmis_zimmet_ve_dolu_tarihler_overdue` |
| E/5 | `test_05_dolu_tarihler_related` (kısmen: onaylı aralığın görünmesi) |
| F/3 | `test_19_talep_sahibi_mi` (sahiplik alanı; butonların görünürlüğü elle denenir) |
| F/5 | `test_17_create_korumalari` (form üzerinden oluşturmada çalışan alanı) |
