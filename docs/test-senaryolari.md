# Ekipman Zimmet Modülü Test Senaryoları

## A Bölümü - Veri Modeli
1. **Fiziksel durum hesaplaması:** Cihaz teslim edilince durum "Zimmette", iade alınınca veya kayıp olarak işaretlenince "Zimmette değil" olur. Yalnızca `onaylandi` durumundaki kayıt fiziksel durumu değiştirmez (A3, B10).
2. **Çalışanı olmayan kullanıcı:** Bağlı çalışan kaydı olmayan kullanıcı talep açmaya çalışırsa `UserError` alır (A4).
3. **Başkası adına talep:** Mühendis RPC ile başka bir çalışanı `calisan_id` olarak vererek talep oluşturmaya çalışırsa hata verir; kendi çalışanını açıkça vererek oluşturursa kayıt oluşur. Oluşmuş kaydın `calisan_id` alanı RPC ile değiştirilemez (A4, D3, B8).
4. **Silme kısıtı:** Geçmiş zimmet kaydı olan cihaz veya çalışan silinemez (A5).
5. **Cihaz arşivleme:** Aktif zimmeti (`onaylandi` veya `teslim_edildi`) olan cihaz arşivlenemez; aktif zimmeti olmayan cihaz arşivlenebilir (A5).
6. **Çalışan arşivleme:** Teslim edilmiş zimmeti olan çalışan arşivlenebilir; zimmet kayıtları korunur ve geciken listesinde görünmeye devam eder (A5).
### Toplu talep (A6)
7. **Toplu talep oluşturma:** Mühendis sihirbazda iki cihaz ve bir tarih aralığı seçer. Her cihaz için ayrı bir kayıt oluşur; ikisi de `talep_edildi` durumundadır, çalışanı mühendisin kendisidir ve aynı `TPL/...` referansını taşır (A6).
8. **Toplu talebin tek işlem olması:** Seçilen cihazlardan biri geçersizse (ör. RPC ile kayıp bir cihaz verilirse) hiçbir kayıt oluşmaz (A6, A7).
9. **Sihirbazın cihaz listesi:** Sihirbazda yalnızca kullanılabilir cihazlar, dolu tarihleriyle birlikte listelenir (A6, A7).
10. **Kayıtların bağımsızlığı:** Toplu talepteki kayıtlardan biri geri çekilir veya reddedilir; diğeri bekler ve ayrıca onaylanabilir (A6).
11. **Toplu onay:** Yetkili toplu talebin kayıtlarını listede seçip tek seferde onaylar. Kayıtlardan biri çakışıyorsa hiçbiri onaylanmaz ve hata mesajı çakışan kaydı gösterir; çakışan kayıt seçimden çıkarılınca diğeri onaylanır (A6, C6).
12. **Toplu talep referansının korunması:** Mühendis RPC ile `toplu_ref` yazmaya çalışırsa hata alır; tek tek açılan kayıtlarda alan boştur (A6, B8).

### Cihazın kullanılabilirliği (A7)
13. **Yalnızca kullanılabilir cihaz seçilir:** Talep formunda ve toplu talep sihirbazında kontrolde, bakımda, kayıp ve hurda cihazlar listelenmez. RPC ile bu cihazlardan biriyle kayıt oluşturmak hata verir (A7).
14. **Mevcut taslak:** Taslağın cihazı kontrole veya bakıma girerse "Talep Et" hata verir ve formda uyarı bandı görünür; cihaz kullanılabilir olunca taslak gönderilebilir (A7).
15. **Mevcut bekleyen talep:** Onay bekleyen talebin cihazı kontrole veya bakıma girerse onay "Cihaz kontrolde; şu an onaylanamaz." gibi bir hata verir; Onay Bekleyenler listesinde cihazın durumu görünür; cihaz kullanılabilir olunca onaylanabilir (A7, F3).
16. **Mevcut onaylı talep:** Onaylı talebin cihazı kontrole veya bakıma girerse talep iptal edilmez, aralık bugünü kapsasa bile "Teslim Et" hata verir, talep "Kullanılamayan Cihaz Onayları" kuyruğunda görünür ve mühendisin formunda iptal seçeneğini hatırlatan uyarı bandı çıkar (A7, F1).
17. **İade kontrole alır:** İade alınan cihaz kendiliğinden "Kontrolde" olur ve "Kontrol Bekleyen Cihazlar" kuyruğunda görünür; cihaz formunda son iadenin referansı, iade edeni, tarihi, kullanıcı geri bildirimi ve iade notu görünür (A7, B10).
18. **Kontrolün sonucu:** "Kontrol Tamamlandı" cihazı "Kullanılabilir", "Bakıma Al" "Bakımda" yapar; bakımdaki cihaz "Kullanılabilir Yap" ile geri döner (A7).
19. **Zimmetteki cihaz:** Zimmetteki cihaz kontrole, bakıma veya hurdaya alınamaz; zimmette olmayan cihaz doğrudan kayıp yapılabilir (A7).
20. **Hurdaya Ayır:** Cihazın taslak, onay bekleyen ve onaylı bütün kayıtları iptal edilir; her birinin iptal nedeni iptal öncesi aşamayı ve cihazın etiket ve adını içerir (ör. "Gönderilmemiş taslağınızdaki cihaz (…) hurdaya ayrıldığı için taslak iptal edildi."); cihaz "Hurda" olur ve arşivlenir; hiçbir kayıt silinmez (A7, B2).
21. **Hurdanın mühendise görünmesi:** Hurda yüzünden iptal edilen talep, mühendisin "Güncel Talepler" listesinde bir hafta görünür; formda iptal nedeni okunur (A7, B3).
22. **Kayıp ve bulunma:** Cihaz kayba girince onaylı talepleri iptal edilmez; bulunan cihaz kontrole alınır ve eski kayıp zimmet kaydı geçmişte kalır (A7, B10).
23. **Ekipmanlar listesi:** Liste varsayılan olarak kayıp ve hurda dışındaki cihazları durumlarıyla gösterir; filtre kaldırılınca kayıp cihazlar, "Arşivlenenler" filtresiyle hurda cihazlar görünür (A7, F4).
24. **Kullanılabilirlik izi:** Kullanılabilirlik değişikliği cihazın chatter'ında değiştiren kullanıcıyla görünür (A7, G6).

## B Bölümü - Süreç Akışı ve Geçişler
1. **Mutlu yol:** Mühendis taslak oluşturur, gönderir (talep_edildi), yetkili onaylar (onaylandi), aralığı gelince teslim eder (teslim_edildi), iade alır (iade_edildi). Fiili tarihler butonlarla yazılır.
2. **Kendi talebini onaylama:** Yetkili, kendi talebini başarıyla onaylayabilir (B7).
3. **Gerekçesiz red:** Yetkili `red_gerekcesi` alanını doldurmadan reddetmeye çalışırsa `UserError` verilir (B3). Gerekçeli red geçer ve mühendis sebebi kendi listesinde görür.
4. **Erken teslim:** Başlangıç tarihi henüz gelmemiş onaylı talep için "Teslim Et" `UserError` verir (B4).
5. **Aralığı geçmiş onaylı teslim:** Bitiş tarihi geçmiş onaylı kayıt teslim edilmeye çalışılırsa `UserError` verilir (B4).
6. **Teslim edilmiş kaydı iptal:** `teslim_edildi` durumundaki kayıt iptal edilmeye çalışılırsa hata verir; yalnızca iade alınabilir veya kayıp olarak işaretlenebilir (B3, B10).
7. **Yetkisiz geçiş (RPC):** Mühendis, arayüzde gizlenen `action_onayla` veya `action_teslim_et` metotlarını RPC/Python shell ile çağırırsa rol kontrolünden `AccessError` alır; kayıp geçişi de yetkiliye özeldir (B8, B10).
8. **Son durumdan çıkış:** `iade_edildi`, `kayip`, `reddedildi` veya `iptal` durumundaki kayıt tekrar bir aktif duruma geçirilemez (B1, B5).
9. **Geri çekme:** Mühendis bekleyen talebi geri çeker, düzenler ve tekrar gönderir (B5).
10. **Onaylı talebi geri çekme:** `onaylandi` durumundaki kayıt geri çekilemez, hata verir (B5).
11. **Başkasının talebini geri çekme:** Talebin sahibi olmayan kullanıcı (yetkili dahil) `action_geri_cek` çağırırsa hata alır (B2).
12. **Taslak silme:** Talep sahibi taslağını formdaki "Taslağı Sil" ile siler; onay sorulur, silindikten sonra talep listesine dönülür. Yetkili başkasının taslağını silemez. Gönderilmiş kayıt silinemez (mühendis ve yetkili için). Taslak iptal edilemez (B3).
13. **Durumun doğrudan yazılması:** Mühendis RPC ile `state: 'onaylandi'` yazmaya çalışırsa hata alır (B8).
14. **Onaylı kayıt oluşturma:** Mühendis RPC ile `state: 'onaylandi'` içeren kayıt oluşturmaya çalışırsa hata alır (B8).
15. **Onaylı kaydı değiştirme:** Onaylı kaydın cihazı veya tarihi RPC ile değiştirilmeye çalışılırsa hata verir (B5).
16. **Chatter izlenebilirliği:** Onay sonrası chatter kaydında onaylayan kullanıcı görünür; geçişler `sudo()` ile yazılsa da kayıt gerçek kullanıcıyı gösterir (B7).
17. **Reddedilen talep akışı:** Yetkili tarihi yanlış talebi gerekçeyle reddeder, mühendis doğru tarihlerle yeni talep açar (B2, B3).
18. **Geçmiş tarihli talep:** Başlangıç tarihi bugünden önce olan taslak gönderilemez ve taslak kalır; bugün başlayan talep gönderilebilir. Taslak geçmiş tarihle kaydedilebilir, tarih düzeltilip gönderilir (B2).
19. **Red gerekçesinin sunucu kontrolü:** Mühendis RPC ile `red_gerekcesi` yazamaz; yetkili de onaylanmış veya reddedilmiş bir talebin gerekçesini sonradan değiştiremez (B3, D5).
20. **Bitişi geçmiş talebin onayı:** Planlanan bitişi bugünden önce olan bekleyen talep onaylanamaz; başlangıcı geçmiş ama bitişi gelmemiş talep onaylanabilir (B2).

### Süre uzatma (B9)
21. **Uzatma mutlu yolu:** Teslim edilmiş kayıtta mühendis "İstenen Bitiş"i yazıp kaydeder; formun üstünde "Uzatma isteği yetkili onayını bekliyor." bandı çıkar, durum `teslim_edildi` kalır. Yetkili onaylar; `planlanan_bitis` yeni tarih olur, `istenen_bitis` temizlenir, eski bitiş chatter'da görünür (B9, G6).
22. **Onaylı kayıtta uzatma:** Henüz teslim edilmemiş onaylı kayıt için de uzatma istenip onaylanabilir (B9).
23. **Geriye veya geçmişe uzatma:** İstenen bitiş mevcut planlanan bitişten önce veya ona eşitse, ya da bugünden önceyse hata verir (B9).
24. **Çakışan uzatma:** Yeni aralık onaylı başka bir kayıtla çakışıyorsa uzatma onayı hata verir, mesaj çakışan kaydı gösterir ve kayıt değişmez (B9, C2, C6).
25. **Gecikmiş kaydın uzatılması:** Gecikmiş kayıt uzatma ister; onaylanınca "Gecikenler" filtresinden çıkar (B9, B6, E3).
26. **Uzatmanın reddi ve geri çekilmesi:** Yetkili reddedince veya mühendis geri çekince `istenen_bitis` temizlenir; durum ve planlanan bitiş değişmez (B9).
27. **Bekleyen uzatma bloklamaz:** Uzatma beklerken aynı tarihlere başka bir talep onaylanabilir; bundan sonra uzatma onayı çakışma hatası verir (B9, C1).
28. **Uzatma alanının korunması:** Talep sahibi olmayan kullanıcı veya `onaylandi`/`teslim_edildi` dışındaki bir kayıtta `istenen_bitis` RPC ile yazılamaz (B9, B8).
29. **Bakımdaki cihazda uzatma:** Onaylı kaydın cihazı bakımdaysa uzatma onayı hata verir (B9, A7).

### Kayıp, iade notları ve geri bildirim (B10)
30. **Kayıp olarak işaretleme:** Yetkili teslim edilmiş kaydı iade / kayıp notuyla "Kayıp" yapar. Kayıt `kayip` olur, `fiili_bitis` bugündür, cihazın kullanılabilirliği "Kayıp" olur, "şu an kimde" boşalır (B10, A7, E1).
31. **Notsuz kayıp:** İade / kayıp notu boşken "Kayıp Olarak İşaretle" hata verir (B10).
32. **Kayıp geçişinin sınırları:** Kayıp geçişi yalnızca `teslim_edildi` kayıttan ve yalnızca yetkili tarafından yapılabilir (B2, B10).
33. **Hasarlı iade:** Yetkili iade notu yazarak iade alır; cihaz kontrole girer, yetkili kontrolde "Bakıma Al" der; zimmet `iade_edildi` olur (B10, A7).
34. **İade / kayıp notunun korunması:** Mühendis RPC ile `kapanis_notu` yazamaz; yetkili de bu alana yalnızca `teslim_edildi` durumunda yazabilir (B10, B8).
35. **Kullanıcı geri bildirimi:** Talep sahibi teslim edilmiş talebine geri bildirim yazabilir; başka kullanıcı veya başka durumda yazılamaz (RPC dahil); geri bildirim kontroldeki cihazın formunda görünür (B10, B8, A7).

### İptal nedeni (B3)
36. **Zorunlu iptal nedeni:** İptal nedeni boşken "İptal Et" hata verir; talep sahibi ve yetkili yazabilir; iptalden sonra alan salt okunur görünür ve kopyalanmaz (B3, B8).

## C Bölümü - Çakışma ve Takvim Kontrolleri
1. **İki çakışan bekleyen talep:** İlk onay geçer, ikincisi onaylanırken hata verir (C1, C2).
2. **Sınır günü:** Bir kayıt 10'unda biter, diğeri 10'unda başlar. Çakışma hatası beklenir (C3).
3. **Erken iade:** İade edilen kayıt takvimi bloklamaz; cihaz kontrolden çıkınca kalan günler için yeni talep onaylanabilir (C1, A7).
4. **Gecikmiş cihaz:** Sonraki rezervasyon onaylanır, ancak "Teslim Et" aşamasında iade kaydı alınmadığı için hata verir (C4).
5. **Onaylı kaydın tarihini değiştirme:** Arayüz veya RPC üzerinden çakışacak şekilde değiştirme B5 hatasıyla durur. `sudo` ortamında (Odoo shell) aynı değişiklik yapılırsa C2 `constrains` çakışmayı yakalar (C2).
6. **Çakışma mesajı:** Yetkili çakışan bir onayı denediğinde hata mesajında çakışan kaydın referansı ve tarihleri görünür. Bloklayan duruma geçmeye çalışan mühendis çakışma kontrolüne ulaşmadan rol kontrolünden yetki hatası alır (C6, B8).
7. **Ters aralık:** Bitiş tarihi < başlangıç tarihi seçilirse hata verir (C3).
8. **Kendi kaydını dışlama:** Onaylı bir kayıt, değişiklik yapılmadan tekrar kaydedildiğinde kendiyle çakışma hatası vermez (C2).
9. **Veritabanı çakışma kısıtı:** Python kontrolü atlanarak doğrudan SQL ile aynı cihaza çakışan iki onaylı kayıt yazılmaya çalışılırsa `EXCLUDE` kısıtı işlemi reddeder (C5).
10. **Veritabanı tek-zimmet indeksi:** Doğrudan SQL ile aynı cihaza ikinci bir `teslim_edildi` kayıt yazılmaya çalışılırsa kısmi benzersiz indeks işlemi reddeder (C5).
11. **Eklentisiz kurulum:** Modül kurulduktan sonra `btree_gist` eklentisi kurulu değildir ve iki kısıt da veritabanında mevcuttur (`pg_extension`, `pg_constraint`, `pg_indexes` sorguları) (C5).
12. **Kapalı durumlar bloklamaz:** Kayıp veya iptal edilmiş kaydın aralığına başka bir talep onaylanabilir (C1, B10).

## D Bölümü - Roller ve Güvenlik
1. **Mühendis görünürlüğü:** Mühendis yalnızca kendi zimmet kayıtlarını listeler; başkasının kaydı görünmez (D2).
2. **Ekipman yönetimi:** Mühendis ekipman veya kategori oluşturmaya çalışırsa hata alır; ekipmanı salt okunur görür ve talep formunda cihaz seçebilir (D4).
3. **Kimde bilgisi:** Mühendis "şu an kimde" alanını ve geçmiş sekmesini göremez; yetkili görür (D6).
4. **Yetkili görünürlüğü:** Yetkili tüm zimmet kayıtlarını görür; yönetici kullanıcı Yetkili grubundadır (D1, D5).
5. **Yetkili haklarının kapsamı:** Yetkili, mühendisin yapabildiği her işlemi (kendi adına talep açma, toplu talep, uzatma isteme) yapabilir (D1).
6. **Kullanılabilirlik yetkisi:** Mühendis cihazın kullanılabilirliğini görür ama değiştiremez (RPC dahil); yetkili değiştirir (D4, A7).
7. **Sihirbaz erişimi:** Mühendis toplu talep sihirbazını açıp kullanabilir (D5, A6).

## E Bölümü - Kimde, Geçmiş, Gecikme, Dolu Tarihler
1. **Şu an kimde:** Teslim sonrası cihazın "kimde" alanı teslim alan çalışandır; iade veya kayıp sonrası boşalır (E1).
2. **Geçmiş:** Cihaz geçmişinde yalnızca teslim edilmiş, iade edilmiş ve kayıp kayıtlar görünür; reddedilen ve iptal edilenler görünmez (E2).
3. **Geciken filtresi:** Teslim edilmiş ve bitişi geçmiş kayıt "Gecikenler" filtresinde ve menüsünde çıkar (E3).
4. **Süresi geçmiş onay:** Bitişi geçmiş ve hiç teslim edilmemiş onaylı kayıt "Süresi geçmiş onay" filtresinde çıkar (E3).
5. **Dolu tarihler:** Onaylı kaydın aralığı mühendisin formunda görünür, isim ve referans görünmez. Bekleyen talebin, bekleyen uzatmanın ve bitişi geçmiş aralıkların görünmez (E4, B9).
6. **Gecikmiş cihaz:** Gecikmiş cihaz dolu tarihlerde "şu an elde, iade bekleniyor" olarak görünür (E4).
7. **Form görünürlüğü:** Dolu tarihler alanı talep formunda yalnızca taslak durumunda görünür (E4).
8. **Kullanılamayan cihaz:** Kontroldeki veya bakımdaki cihazın dolu tarihler alanının başında yalnızca durumu yazılır ("Cihaz kontrolde", "Cihaz bakımda"); süre tahmini yoktur (E4, A7).

## F Bölümü - Ekranlar ve Menüler
1. **Menü görünürlüğü:** Zimmet Talepleri "Güncel Talepler" filtresiyle açılır (F/15). Yetkili hesabında Zimmet Talepleri, Onay Bekleyenler, Teslim Bekleyenler, Gecikenler, Süresi Geçmiş Onaylar, Uzatma Bekleyenler, Kullanılamayan Cihaz Onayları, Kontrol Bekleyen Cihazlar, Ekipmanlar ve Kategoriler görünür. Mühendis hesabında yalnızca Zimmet Talepleri ve Ekipmanlar görünür (F1).
2. **Kuyruk içerikleri:** Onay Bekleyenler yalnızca `talep_edildi`, Teslim Bekleyenler yalnızca `onaylandi`, Uzatma Bekleyenler yalnızca `istenen_bitis` dolu, Kullanılamayan Cihaz Onayları yalnızca cihazı kullanılabilir olmayan `onaylandi` kayıtları, Kontrol Bekleyen Cihazlar yalnızca kontroldeki cihazları listeler. Kuyruk menüsü ilgili filtreyi arama çubuğunda etiket olarak açar; filtre kaldırılınca tüm kayıtlar görünür (F1).
3. **Buton görünürlüğü:** Taslakta sahibinde Talep Et ve Taslağı Sil (İptal Et görünmez); bekleyen talepte sahibinde Geri Çek, yetkilide Onayla ve Reddet; onaylı talepte yetkilide Teslim Et, sahibinde düzenlenebilir "İstenen Bitiş" alanı; teslim edilmişte yetkilide İade Al ve Kayıp Olarak İşaretle, sahibinde düzenlenebilir "İstenen Bitiş" alanı; bekleyen uzatmada sahibinde Uzatmayı Geri Çek, yetkilide Uzatmayı Onayla ve Uzatmayı Reddet; kapalı durumlarda (iade, kayıp, red, iptal) hiçbir buton görünmez. Yetkili başkasının taslağını açtığında Talep Et ve Taslağı Sil, bekleyen talebinde Geri Çek görünmez (F2).
4. **Statusbar:** Statusbar'a tıklanarak durum değiştirilemez (F2, B8).
5. **Çalışan alanı:** Talep formunda çalışan kullanıcının kendi adıyla dolu ve düzenlenemezdir (F2, A4).
6. **Fiili tarihler:** Fiili tarih alanları taslakta ve onaylı durumda gizlidir, teslimden sonra salt okunur görünür (F2).
7. **Red gerekçesi alanı:** Yalnızca yetkiye ve yalnızca bekleyen talepte düzenlenebilir; reddedilen talepte salt okunur görünür; boşken Reddet hata verir (F2, B3).
8. **Liste vurgusu:** Geciken satır kırmızı, süresi geçmiş onay sarı, bekleyen talep mavi, kapalı durumlar (iade, kayıp, red, iptal) soluk görünür; sıralama planlanan başlangıca göre azalandır (F3).
9. **Ekipman ekranı:** Ekipman listesinde kullanılabilirlik kolonu herkese, "şu an kimde" kolonu yalnızca yetkiye görünür. "Verilebilir" filtresi yalnızca kullanılabilir ve zimmette olmayan cihazları getirir. Ekipman formunda "Geçmiş" sekmesi yalnızca yetkide görünür; altta chatter vardır (F4, D6, G6).
10. **Görünüm türleri:** Zimmet ve ekipman modelleri yalnızca liste ve form görünümü sunar; takvim, pivot ve kanban yoktur (F5).
11. **Arama ve gruplama:** Referans, cihaz ve çalışana göre arama çalışır; Güncel Talepler, Açık Talepler, Onay Bekleyenler, Teslim Bekleyenler, Gecikenler, Süresi Geçmiş Onaylar, Uzatma Bekleyenler ve Kullanılamayan Cihaz Onayları filtreleri doğru kayıtları getirir; cihaz, çalışan, durum ve toplu talebe göre gruplama çalışır (F6).
12. **Arayüz dili:** Menüler, alan etiketleri, butonlar ve hata mesajları Türkçedir (F7).
13. **Uzatma ve kapanış alanları:** İstenen bitiş alanı yalnızca `onaylandi`/`teslim_edildi` durumunda görünür. Kapanış notu teslim edilmiş kayıtta yetkiye düzenlenebilir, kapanmış kayıtta salt okunur görünür. Toplu talep referansı yalnızca doluysa görünür (F2).
14. **Cihaz açıklaması:** Talep formunda cihaz seçilince cihazın açıklaması salt okunur görünür; açıklaması olmayan cihazda alan gizlidir. Ekipman listesinde açıklama sütunu varsayılan olarak görünür (A3).
15. **Güncel ve Açık Talepler:** "Güncel Talepler" açık talepleri ve kapanış tarihi son 7 gün içinde olan (iade, kayıp, red, iptal) talepleri, "Açık Talepler" yalnızca açık talepleri getirir; ikisi birlikte seçilince Güncel Talepler gibi davranır; 7 günden eski kapanmış talepler filtre kaldırılınca görünür. Kapanış tarihi kapanış anında bir kez yazılır; kapanmış kayda sonradan yapılan bir yazma onu değiştirmez. Demoda yeni reddedilmiş 9 numaralı kayıt görünür, eski iptal edilmiş 11 numaralı kayıt görünmez (B3, F6, H3).
16. **Cihaz durumu ve uyarılar:** Talep formunda cihazın açıklaması ve kullanılabilirliği ("Cihaz Durumu") salt okunur görünür; cihaz kullanılabilir değilse formun üstünde aşamaya göre uyarı bandı çıkar; mühendisin listesinde isteğe bağlı "Cihaz Durumu" sütunu, Onay Bekleyenler listesinde kullanılabilirlik sütunu bulunur (A7, F2, F3).

## G Bölümü - Mimari ve Kurulum
1. **Temiz kurulum:** Boş bir veritabanında modül kurulur; log'da `ERROR` veya modülümüze ait uyarı çıkmaz. Bağımlılık olarak yalnızca `mail` ve `hr` istenir (G2, G4, G9).
2. **Yükleme sırası:** Modül ilk kurulumda ve güncellemede (`-u`) hatasız yüklenir; demo açık ve demo kapalı veritabanlarında kurulur. Güncellemede veritabanı kısıtları varsa yeniden oluşturulmaz ve hata vermez; `-u` iki kez art arda çalıştırılarak denenir (G4, C5).
3. **Referans numarası:** Yeni kayıt `ZMT/0001` biçiminde ad alır, ardışık kayıtlarda numara artar. Mühendis hesabıyla kayıt oluşturulunca da numara atanır (sıra yetkisi). Toplu talep `TPL/0001` biçiminde ayrı bir sıradan numara alır (G5, A6).
4. **Kopyalama:** Kapanmış (ör. iade edilmiş) bir kayıt mühendis tarafından kopyalanınca hata vermez; yeni kayıt kopyalayanın adına, aynı cihaz ve planlanan tarihlerle bir taslaktır. Yeni referans numarası alır; durum, fiili tarihler, red gerekçesi, istenen bitiş, kapanış notu ve toplu talep referansı kopyalanmaz. Yetkili başkasının kaydını kopyalayınca kayıt yetkilinin adına oluşur (B8, G5, A4).
5. **Chatter:** Zimmet durum değişiklikleri ve uzatmalar zimmet chatter'ında, kullanılabilirlik değişiklikleri cihaz chatter'ında kullanıcı ve zamanla izlenir; aktivite planlama kullanılmaz (G6, B7).
6. **Benzersizlik:** Aynı etiket no ikinci bir cihaza verilirse anlaşılır bir hata alınır; seri no boş bırakılabilir (G7).
7. **Adlandırma:** Kodda Odoo'nun kendi adları dışında İngilizce tanımlayıcı kalmamıştır (örneğin zimmet modelinde `calisan_id` yerine İngilizce isim olmamalıdır). Elle tarama veya `grep` ile kontrol edilir (G3).
8. **Manifest:** Modül Uygulamalar listesinde uygulama olarak görünür, özet metni ve sürümü doğrudur (G9).
9. **Otomatik testler:** Modülün testleri komut satırından çalıştırılır ve geçer; temiz bir veritabanında tekrar çalıştırılabilir (G8).

## H Bölümü - Demo Verisi
1. **Demo kullanıcılar:** Beş demo kullanıcı kendi parolasıyla giriş yapar; her birinin bağlı bir çalışan kaydı ve doğru grubu vardır; yönetici kullanıcı Yetkili grubundadır (H1, D1).
2. **Ekipman:** Üç kategori ve sekiz cihaz yüklenmiştir; her cihazın etiketinden farklı bir adı ve açıklaması vardır (seçim kutusunda ör. "[LTP-001] MacBook Pro 14 M1 Pro"); OSC-003 bakımda, LTP-003 kayıp, diğerleri kullanılabilirdir (H2).
3. **Kayıtlar:** On altı zimmet kaydı doğru durum ve tarihlerle yüklenmiştir; cihazların fiziksel durumu ve "şu an kimde" bilgisi doğru hesaplanmıştır (örneğin OSC-001 Zimmette ve kimde Defne; LTP-003 Zimmette değil ve kimde boş) (H3, E1).
4. **Göreli tarihler:** Veritabanı farklı bir günde yeniden oluşturulunca gecikmiş ve süresi geçmiş kayıtlar yine gecikmiş görünür, bugünü kapsayan onaylar (2, 8, 15) yine bugünü kapsar (H4).
5. **Demo kapalı veritabanı:** Demo kapalı oluşturulan veritabanında modül kurulur; gruplar ve yapı gelir, senaryo kayıtları gelmez (H5).
6. **Sunum akışı:** H6'daki adımlar (1, 2, 3, 3b, 3c, 3d, 4, 5) sırayla hatasız tamamlanır; her adımda beklenen hata ve sonuçlar görülür (H6).
7. **Çakışan talepler:** 3 ve 4 numaralı bekleyen talepten biri onaylanır, diğeri onaylanmaya çalışılınca çakışma hatası verir (H3, C2).
8. **Gecikmiş cihazın teslim hatası:** 2 numaralı kaydın aralığı bugünü kapsar; yetkili "Teslim Et"e basınca hata teslim zamanlaması kuralından (B4) değil, cihaz hâlâ 1 numaralı kayıtta olduğu için C4'ten gelir ("Önce iade alınması gerekir") (H3, C4).
9. **Demo uzatmaları:** 7 numaralı kaydın uzatması onaylanır; 1 numaralı kaydın uzatması 2 ile çakıştığı için hata verir (H3, B9).
10. **Demo toplu talep:** 13 ve 14 numaralı kayıtlar `TPL/0001` altında gruplanır ve birlikte onaylanabilir (H3, A6).
11. **Demo bakım ve kayıp:** 15 numaralı kayıt "Kullanılamayan Cihaz Onayları" kuyruğunda görünür ve aralık bugünü kapsadığı halde teslimi kullanılabilirlik (A7) hatası verir; LTP-003'ün geçmişinde 16 numaralı kayıp kaydı ve kapanış notu görünür (H3, A7, B10).

## Otomatik / elle ayrımı (G8)
Aşağıdaki senaryolar `ekipman_zimmet/tests/test_zimmet.py` içindeki testlerle otomatik doğrulanır. Testler mühendis ve yetkili kullanıcılarıyla (`with_user`) çalışır. Diğer senaryolar elle denenir. v2 senaryolarından henüz uygulanmamış olanların (A/7–A/24, B/29–B/35, C/12, D/6–D/7, E/8, F/13–F/14, F/16, H/9–H/11) testleri ilgili fazda eklenir ve bu tabloya işlenir. B/27 elle denenir.

| Senaryo | Test |
|---|---|
| A/2 | `test_07_calisan_profili_olmayan_kullanici` |
| A/3 | `test_06_baskasi_adina_talep_acma_engeli`, `test_08_calisan_id_degistirilemez`, `test_17_create_korumalari` |
| B/1 | `test_12_erken_iade` (gönder, onayla, teslim et, iade al) |
| B/2 | `test_01_tarih_cakismasi` (yetkili kendi talebini onaylar) |
| B/3 | `test_02_red_gerekcesi` |
| B/11 | `test_15_geri_cekme_yetkisi` |
| B/12 | `test_03_unlink_kisiti`, `test_04_muhendis_taslak_unlink`, `test_21_taslak_iptal_edilemez`, `test_22_taslagi_yalnizca_sahibi_siler` |
| B/13 | `test_14_state_dogrudan_yazilamaz` |
| B/14 | `test_17_create_korumalari` |
| B/16 | `test_20_chatter_onaylayani_gosterir` |
| B/18 | `test_16_gecmis_tarihli_talep_gonderilemez` |
| B/20 | `test_23_bitisi_gecmis_talep_onaylanamaz` |
| B/21, B/24, B/26 | `test_35_uzatma_onay_ve_red` |
| B/22, B/23, B/26 (geri çekme), B/28 | `test_34_uzatma_istegi` |
| B/25 | `test_36_gecikmis_kayit_uzatilinca_gecikenlerden_cikar` |
| B/36 | `test_31_iptal_nedeni_zorunlu`, `test_32_kapanis_tarihi` |
| B/19 | `test_09_red_gerekcesi_yetki_kontrolu`, `test_18_red_gerekcesi_yalnizca_bekleyen_talepte` |
| C/1 | `test_01_tarih_cakismasi` |
| C/2 | `test_11_sinir_gunu` |
| C/3 | `test_12_erken_iade` |
| C/4 | `test_13_gecikmis_cihaz_teslim` |
| C/6 | `test_25_cakisma_mesaji` |
| C/9 | `test_28_veritabani_cakisma_kisiti` |
| C/10 | `test_29_veritabani_tek_teslim_kisiti` |
| C/11 | `test_30_kisitlar_eklentisiz_kurulu` |
| A/1 | `test_26_fiziksel_durum` |
| E/5 (tarih biçimi) | `test_27_dolu_tarihler_kullanici_dil_bicimiyle` |
| G/4 | `test_24_kopya_kopyalayanin_adina_taslaktir` |
| E/2, E/6 | `test_10_gecmis_zimmet_ve_dolu_tarihler_overdue` |
| E/5 | `test_05_dolu_tarihler_related` (kısmen: onaylı aralığın görünmesi) |
| F/3 | `test_19_talep_sahibi_mi` (sahiplik alanı; butonların görünürlüğü elle denenir) |
| F/5 | `test_17_create_korumalari` (form üzerinden oluşturmada çalışan alanı) |
| F/15 | `test_33_guncel_ve_acik_talepler` |
