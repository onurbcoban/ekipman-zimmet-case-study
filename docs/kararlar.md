## A0 — Bir talepte kaç cihaz istenebilir?
Karar: Her bir zimmet talebi formu yalnızca tek bir cihazı (1 adet donanım) içerebilir.
Alternatifler: Bir formda satırlar halinde (One2many) birden çok cihaz ekleyebilmek.
Gerekçe: Dokümanda aksi belirtilmediği için, geliştirme süresini kısaltmak ve çakışma mantığını basitleştirmek adına atomik tasarım benimsenmiştir. Çoklu cihaz için ayrı talepler açılmalıdır.
Etkisi: Tasarımın geri kalanı (Tek Model) bu kural üzerine inşa edilecek.
README özeti: Her talep formu geliştirme hızını ve çakışma mimarisini basit tutmak adına tek bir cihaz (atomik) içerecek şekilde tasarlanmıştır.

## A1 — Talep ve zimmet aynı kayıt mı?
Karar: Tek model (`ekipman.zimmet`) kullanılacak. Talep taslak olarak başlar, durum (state) değiştirerek teslim ve iade aşamalarına geçer.
Alternatifler: Talep ve zimmet hareketi olarak iki ayrı model.
Gerekçe: A0 kararı gereği her talepte tek cihaz istenebileceği için, iki model kurmak gereksiz bir iş yükü doğurur. Tek model, bakım ve çakışma sorgusu açısından daha sadedir.
Etkisi: Çakışma kontrolleri ve durum yönetimi tek bir model üzerinde ele alınacak.
README özeti: Tek cihaz kuralı gereği 1:1 tablo ilişkisinden kaçınılarak Talep ve Zimmet süreçleri tek model (`ekipman.zimmet`) üzerinde durum geçişleriyle birleştirilmiştir.

## A2 — Tarih alanları ayrı mı tutulacak, veri tipi ne olacak?
Karar: Planlanan ile fiili tarihler ayrı alanlarda tutulacak. `Date` tipi kullanılacak. Fiili tarihler arayüzde (readonly) düzenlemeye kapalı olacak ve butonlarla (`context_today(self)`) otomatik basılacak.
Alternatifler: `Datetime` kullanmak veya fiili tarihleri elle düzeltmeye açmak.
Gerekçe: `Datetime` UTC olarak saklanır ve gün sınırı kullanıcının saat dilimine göre kayar; `Date` ise gün bazlı bir kavramı doğrudan ifade eder. `context_today` ile kullanıcının saat dilimine göre "bugün" alınır (sunucu saati hatası önlenir). "İade etmeyi unutma" için geçmişe dönük elle düzeltme yetkisi kapsam dışı bırakılmıştır; iade kaydı geç basılırsa kayıttaki tarih gerçek tarihten geç olur.
Etkisi: Arayüzde fiili tarihler `readonly` olacak; sunucu tarafında doğrudan yazma `write()` korumasıyla engellenir (B8). Python'da `context_today` çağrılacak.
README özeti: Saat dilimi karmaşasını önlemek için gün bazlı `Date` kullanılmış, fiili tarihler yalnızca işlem butonlarıyla otomatik doldurulur; geçmişe dönük elle düzeltme yoktur.

## A3 — Ekipman kaydı (sicili) nasıl tutulacak ve cihaz durumu nasıl takip edilecek?
Karar: Her fiziksel donanım tekil bir kayıt olacak (seri no / etiket no). Cihazın "Fiziksel Durumu" (etiket: **Şu an müsait / Zimmette**, teknik anahtarlar `musait` / `zimmette`) zimmet kayıtlarından hesaplanan VE saklanan (`compute + store=True`) bir alan olacak. `teslim_edildi` durumunda en az bir zimmet kaydı varsa `zimmette`, yoksa `musait`; `onaylandi` fiziksel durumu değiştirmez. Kategori `ekipman.kategori` adlı küçük bir modelle tutulur ve zorunludur. Kayıtlar silinmek yerine arşivlenir (`active=False`).
Alternatifler: Saklanmayan hesaplanan alan (`store=False`); kategoriyi `Selection` yapmak; miktar bazlı stok kaydı.
Gerekçe: `store=True` olmazsa alan üzerinden standart gruplama ve filtreleme yapılamaz. `@api.depends('zimmet_ids.state')` kullanmak, ORM üzerinden yapılan değişikliklerde veriyi tutarlı kılar. Alan müsaitliği değil, cihazın anlık fiziksel durumunu gösterir; bu yüzden etiket "Şu an müsait"tir ve gelecek tarihler için müsaitlik E4'teki "dolu tarihler" bilgisinden okunur. Kategori ayrı model olduğu için yetkili arayüzden yeni kategori ekleyebilir.
Etkisi: Hesaplama `len > 1` uç durumunda (hatalı çoklu teslim) çökmeyecek şekilde yazılacak. "Şu an kimde" alanı (E1) aynı hesaplama metodunda üretilir.
README özeti: Her cihaz tekil kayıttır; fiziksel durum yalnızca cihazın şu an bir kullanıcıda kayıtlı olup olmadığını gösterir (`store=True` computed field). Gelecek tarihler için müsaitlik "dolu tarihler" alanından okunur.

## A4 — Zimmet kime yapılacak (Kişi Bağı)?
Karar: Zimmet kaydı `hr.employee` modeline bağlanacak (`calisan_id`). Talep yalnızca giriş yapan kullanıcının kendi çalışan profili adına açılır; alan varsayılan olarak doldurulur ve düzenlenemez. Kullanıcının bağlı çalışanı yoksa talep açılamaz (`UserError`).
Alternatifler: Zimmeti `res.users` hesabına bağlamak; başkası adına talebe izin vermek (D3).
Gerekçe: `hr` modülü zorunlu kurulum olarak isteniyor ve çalışan, kişinin standart Odoo modelidir. Kullanıcısı olmayan personel için süreç eklenirse veri modeli değişmez.
Etkisi: Sunucu tarafı kural (B8): `create`'te değer gönderilmezse ya da kullanıcının kendi çalışanı gönderilirse kayıt kullanıcının çalışanıyla oluşur, başka bir çalışan gönderilirse `UserError`; `write`'ta `calisan_id` `sudo` dışında hiç değiştirilemez. `readonly` yalnızca arayüzdür (A2, D5).
README özeti: Zimmet çalışan profiline bağlanır; kullanıcı yalnızca kendi adına talep açabilir.

## A5 — Cihaz veya çalışan silinirse / arşivlenirse geçmiş kayıtlara ne olacak?
Karar: Zimmet kaydındaki `cihaz_id` ve `calisan_id` alanlarına `ondelete='restrict'` uygulanır: geçmiş zimmet kaydı olan cihaz veya çalışan silinemez. Aktif zimmeti ('onaylandi', 'teslim_edildi') olan **cihazın** arşivlenmesi, ekipman modelinin `write()` metodunda engellenir. Çalışan arşivlemesi engellenmez; çalışan arşivlense de zimmet kayıtları korunur.
Alternatifler: `cascade` veya `set null`; arşivlemeyi serbest bırakmak; çalışan arşivlemesini de engellemek (`hr.employee` genişletilerek).
Gerekçe: Geçmiş izlenebilirlik bozulmamalıdır. Cihaz kendi modelimiz olduğu için kontrol ucuzdur. Çalışan arşivlemesini engellemek çekirdek İK sürecine (ayrılış sihirbazı) müdahale gerektirirdi; "üzerinde cihaz varken işten ayrılamaz" ise bir süreç politikasıdır, veri tutarlılığı sorunu değildir.
Etkisi: `hr.employee` genişletilmez. Arşivlenmiş çalışanın teslim edilmiş kayıtları geciken ve geçmiş listelerinde görünmeye devam eder. Sınırlama: sistem, üzerinde cihaz olan çalışanın arşivlenmesini engellemez.
README özeti: Geçmiş izlenebilirlik için silme `ondelete='restrict'` ile engellenir; aktif zimmeti olan cihaz arşivlenemez. Çalışan arşivlemesi İK sürecine müdahale etmemek için engellenmez.

## B1 — Durum kümesi
Karar: Yedi durum: `taslak`, `talep_edildi`, `onaylandi`, `teslim_edildi`, `iade_edildi`, `reddedildi`, `iptal`. Son durumlar: `iade_edildi`, `reddedildi`, `iptal`.
Alternatifler: `taslak` olmadan (kayıt doğrudan `talep_edildi` başlar); `geciken` ayrı durum (B6).
Gerekçe: Her durum farklı bir iş anlamı taşır: kimin elinde olduğu ve takvimi bloklayıp bloklamadığı (C1) durumdan okunur. `taslak`, kullanıcının kaydı göndermeden saklamasını ve onaydan önce düzeltmesini sağlar (B5).
Etkisi: Durum alanı `Selection`, statusbar'da gösterilir. Bloklayan durumlar C1'de tanımlıdır.
Zayıf nokta: `taslak`, geri çekme (B5) olmasaydı en az gerekçelendirilmiş durum olurdu; şimdi geri çekmenin hedef durumudur.
README özeti: Bir zimmet kaydı yedi durumdan birinde bulunur; üçü (iade, red, iptal) süreci kapatır.

## B2 — Geçiş tablosu
Karar:

| # | Geçiş | Kim | Ön koşul | Yan etki |
|---|---|---|---|---|
| 1 | taslak → talep_edildi | Talep sahibi | Cihaz ve tarihler dolu; başlangıç bugünden önce değil | — |
| 2 | talep_edildi → onaylandi | Yetkili | C2 çakışma kuralı geçer | Chatter'a işlenir |
| 3 | talep_edildi → reddedildi | Yetkili | Red gerekçesi dolu | — |
| 4 | talep_edildi / onaylandi → iptal | Talep sahibi veya yetkili | — | — |
| 5 | onaylandi → teslim_edildi | Yetkili | Bugün planlanan aralıkta (B4); C4 tek-zimmet kuralı | `fiili_baslangic` = bugün |
| 6 | teslim_edildi → iade_edildi | Yetkili | — | `fiili_bitis` = bugün |
| 7 | talep_edildi → taslak (geri çek) | Talep sahibi | — | — |

"Talep sahibi", talebin çalışanının kullanıcısıdır (`calisan_id.user_id`) ve talebi açan kişidir (A4, D3).
Alternatifler: Onaydan sonra geri dönüş (B5); teslim ve iadeyi talep sahibinin kendisinin onaylaması; yetkilinin talebi taslağa geri çekmesi.
Gerekçe: Onay yetkilide, çünkü cihazın paylaşımı bir yönetim kararıdır. Teslim ve iadeyi yetkilinin yapması, cihazın fiziksel olarak elden ele geçtiğinin tek bir yetkili kişi tarafından teyit edilmesini sağlar. Yetkili hatalı bir talep görürse reddeder; zorunlu red gerekçesi (B3) mühendisi bilgilendirir, ayrı bir bildirim mekanizması gerekmez.
Etkisi: Her geçiş bir `action_*` metodudur. Bu tablo README'deki süreç akışı bölümünün temelidir.
README özeti: Tablo olduğu gibi README'ye girer.

## B3 — Red ve iptal
Karar: Red gerekçesi zorunludur. Onaylanmış bir talebi talep sahibi de iptal edebilir. `teslim_edildi` durumundaki kayıt iptal edilemez, yalnızca iade alınır. Taslak iptal edilmez; talep sahibi formdaki "Taslağı Sil" ile (onay sorularak) siler. Zimmet kaydı yalnızca `taslak` durumundayken ve yalnızca sahibi tarafından silinebilir; gönderilmiş kayıtlar iptal edilir ve geçmişte kalır. "Zimmet Talepleri" listesi varsayılan olarak yalnızca açık talepleri (iade, red ve iptal dışındakileri) gösterir; kapanmış kayıtlar filtre kaldırılınca görünür.
Alternatifler: Red için wizard (açılır pencere); gerekçesiz red; kayıtların her durumda silinebilmesi.
Gerekçe: Gerekçesiz red kullanıcıyı belirsizlikte bırakır. Wizard ek model demek, basit bir alan yeterli. Onaylı talebi sahibinin iptal edebilmesi, takvimi serbest bırakmanın en ucuz yoludur. Hiç gönderilmemiş taslağın denetim değeri yoktur; iptal edilmiş bir taslak listede değersiz bir kayıt olarak kalırdı, bu yüzden taslak iptal edilmez, silinir. Taslak kişiseldir ve henüz kimseye gönderilmemiştir; başkasının taslağını silmenin meşru bir nedeni olmadığı için yalnızca sahibi siler. Gönderilmiş kayıtlar ise izlenebilirlik için (A5) silinemez; özellikle onaylanıp iptal edilen kayıt, takvimi kimin tutup bıraktığının tek izidir. Listenin kapanmış kayıtlarla kalabalıklaşması silmeyle değil, varsayılan filtreyle çözülür.
Etkisi: İptal edilen onaylı talep takvimi bloklamaz (C1). Silme kontrolü `unlink()` içindedir (B8). `red_gerekcesi` alanına `write()` içinde yalnızca Yetkili grubu ve yalnızca `talep_edildi` durumunda yazabilir; karar verildikten sonra gerekçe değiştirilemez. Alan `sudo`'ya kısıtlanmaz, çünkü yetkili formdan normal yolla yazar.
Zayıf nokta: Gerekçe, Reddet'e basmadan önce formda yazılmalıdır. Form butonları çalışmadan önce kaydı kaydettiği için bu aynı ekranda yapılır, ayrı pencere gerekmez; ancak alanın boş olduğu butona basınca fark edilir.
README özeti: Reddedilen taleplerde gerekçe zorunludur; onaylı talep iptal edilirse takvim hemen serbest kalır; taslak iptal edilmez, yalnızca sahibi tarafından silinir; gönderilmiş kayıtlar silinmez, liste varsayılan olarak açık talepleri gösterir.

## B4 — Teslim ve iade zamanlaması
Karar: Teslim yalnızca bugün planlanan aralığın içindeyken yapılır (`başlangıç <= bugün <= bitiş`). Erken teslim ve aralığı geçmiş onayın teslimi desteklenmez; aralığı geçmiş onayı yetkili iptal eder. İade her zaman alınabilir.
Alternatifler: (b) Koşullu erken teslim: bugünden planlanan bitişe uzanan aralık başka bir bloklayan kayıtla çakışmıyorsa serbest. (c) Serbest teslim, yalnızca C4 fiziksel kontrolü.
Gerekçe: C4 yalnızca fiilen teslim edilmiş kayıtlara bakar. Erken teslim, onaylı ama henüz teslim alınmamış başka bir talebin hakkını bozabilir (A onaylı 8–11, B onaylı 12–15; B 10'unda alırsa A alamaz). Bitişi geçmiş bir onay teslim edilirse, sonraki onaylı kişinin aralığına girer. Her iki durumda planlanan tarihlere dayalı koruma (C1, C2) aşılmış olur.
Etkisi: `action_teslim_et` içinde tarih aralığı kontrolü. Süresi geçmiş onaylar için bir filtre eklenir (E3).
Zayıf nokta: Bir gün erken gelen kullanıcı için kayıt iptal edilip yeniden talep açılmalıdır. (b), yalnızca bu kontrolün genişletilmesiyle eklenebilir.
README özeti: Teslim yalnızca planlanan aralıkta yapılır; erken teslim, onaylı başka bir talebin hakkını bozabileceği için desteklenmez ve ileride çakışma kontrolüyle genişletilebilir.

## B5 — Geri dönüş ve düzenleme kilidi
Karar: Geri dönüş yalnızca onaydan önce mümkündür: bekleyen talep taslağa geri çekilir, düzeltilir ve tekrar gönderilir. Onaydan sonra geri dönüş yoktur; yanlış bir onay için yetkili talebi iptal eder, yeni talep açılır. Cihaz ve tarih alanları yalnızca `taslak` durumunda düzenlenebilir: arayüzde `readonly="state != 'taslak'"`, ayrıca `write()` içinde (B8) taslak dışındaki kayıtlarda bu alanlara yazma `UserError` verir.
Alternatifler: Geri dönüşü hiç sunmamak (iptal ve yeni talep); bekleyen talebi de düzenlenebilir bırakmak; "Onayı geri al" geçişi; yalnızca arayüz kilidi.
Gerekçe: Bekleyen talep takvimi bloklamadığı için (C1) geri çekmek kimsenin hakkını bozmaz ve "yalnızca taslakta düzenlenir" kuralını korur. Bekleyen talebi doğrudan düzenlenebilir bırakmak, yetkili formu açıkken içeriğin değişmesine yol açardı. Onay bir söz olduğu için sonrasında geri dönüş verilmedi; gerekirse tabloya bir satır ve bir metotla eklenebilir. `readonly` yalnızca arayüzü kapatır; RPC ve içe aktarma yolunu `write()` kontrolü kapatır.
Etkisi: `action_geri_cek` metodu (B8). C2'deki "tarih/cihaz değişince yeniden kontrol" artık esas olarak `sudo` ortamındaki yollar içindir.
README özeti: Yanlış gönderilen talep onaydan önce taslağa geri çekilip düzeltilebilir; onaydan sonra geri alma yerine iptal ve yeni talep kullanılır.

## B6 — Gecikme bir durum değildir
Karar: "Gecikmiş", `teslim_edildi` durumu ile planlanan bitişin bugünden önce olmasının birleşimidir, ayrı bir durum değildir.
Alternatifler: Ayrı `geciken` durumu; zamanlanmış görevle durum güncelleme.
Gerekçe: Bugünün tarihine bağlı bir durum kendiliğinden güncellenmez, zamanlanmış görev (cron) gerektirir. Türetilmiş koşul her zaman doğrudur.
Etkisi: Koşul tek bir arama filtresinde tutulur (E3).
README özeti: Gecikme ayrı bir durum değil, `teslim_edildi` ve geçmiş bitiş tarihi koşuludur; zamanlayıcı gerekmez.

## B7 — Roller ve kendi talebini onaylama
Karar: İki rol: Mühendis ve Yetkili (belgedeki gibi). Teslim ve iade yetkilinindir. Yetkili kendi talebini de onaylayabilir.
Alternatifler: Görevler ayrılığı ilkesi gereği kendi talebini onaylamayı yasaklamak; teslim için ayrı bir "teslim sorumlusu" rolü.
Gerekçe: Yasaklanırsa tek yetkilisi olan bir şirkette süreç tıkanır. Belgede böyle bir kısıt geçmez ve üçüncü rol belgede yoktur. Onaylayan ve zamanı chatter'da izlenir.
Etkisi: Onay metodunda kendi talebine dair kontrol yoktur. Gerekirse kural tek satırla eklenir. Geçişler `sudo()` ile yazıldığı için, chatter kaydında onaylayan kullanıcının görünmesi test edilir.
Zayıf nokta: Bir yetkili kendi talebini denetimsiz onaylayabilir; denetim yalnızca chatter kaydıyla sağlanır. Demo verisinde en az iki yetkili kullanıcı bulunmalıdır.
README özeti: Tıkanmayı önlemek için yetkili kendi talebini onaylayabilir; işlemler chatter'da izlenir.

## B8 — Geçişlerin uygulanışı ve izlenebilirlik
Karar: Her geçiş metodu rol ve kaynak durumu kendisi kontrol eder, ardından yazmayı `sudo()` ile yapar. `sudo` ortamı (`self.env.su`) dışında: `write()` `state`, fiili tarih ve `calisan_id` alanlarına yazmayı `UserError` ile reddeder; `create()` `taslak` dışında bir `state` veya fiili tarih verilirse `UserError` verir, `calisan_id` için A4'teki kuralı uygular. `create`'te `state='taslak'` kabul edilir, çünkü web istemcisi yeni kayıtta durum çubuğundaki varsayılan değeri de gönderir (testle doğrulandı). Statusbar tıklanabilir yapılmaz. `mail.thread` ile `state` izlenir (`tracking=True`).
Alternatifler: Yalnızca butonların `invisible` koşuluna güvenmek; context bayrağıyla yazma izni.
Gerekçe: Buton gizlemek yetki sağlamaz. Mühendisin kendi kayıtlarında yazma hakkı olduğu için `write({'state': 'onaylandi'})` çağrısı metot kontrolünü atlar; aynısı `create` için de geçerlidir. Context bayrağı istemci tarafından gönderilebileceği için güvenilmez; `su` ortamı istemci tarafından ayarlanamaz.
Etkisi: Geçiş metotları (`action_onayla` vb.) kendi içlerinde durum (`state != beklenen`) ve yetki (`has_group`) kontrolü yapar; ihlalde `UserError` fırlatır, ardından `rec.sudo().write(...)` kullanır.
README özeti: Durum geçişleri butonun görünürlüğüne değil, sunucu tarafındaki rol ve durum kontrolüne dayanır; durum alanına arayüz veya RPC üzerinden doğrudan yazılamaz.

## C1 — Hangi durumlar cihazın takvimini bloklar?
Karar: Yalnızca `onaylandi` ve `teslim_edildi`. `taslak`, `talep_edildi`, `reddedildi`, `iptal`, `iade_edildi` bloklamaz.
Alternatifler: (b) Bekleyen talepler de bloklar. (c) İade edilmiş kayıtlar planlanan bitişe kadar bloklar.
Gerekçe: Bekleyen talep henüz kimseye hak vermez; bloklarsa onaylanmadan başkasının önünü keser ve cihazı sahipsiz tutar. Erken iade edilen cihazın kalan günleri serbest kalmalıdır.
Etkisi: Çakışma yalnızca bloklayan durumlardaki kayıtlara bakar. İki kişi aynı tarihe talep açabilir, yalnızca biri onaylanabilir. Onay sonrası çakışan diğer talepler kendiliğinden reddedilmez, yetkili elle reddeder (otomatik red kapsam dışı).
README özeti: Yalnızca onaylı veya teslim edilmiş kayıtlar takvimi bloklar; bekleyen talepler cihazı sahipsiz tutamaz.

## C2 — Çakışma kontrolü ne zaman yapılır?
Karar: Sert kontrol, tek bir `@api.constrains` ile yapılır; bloklayan duruma geçişte ve bloklayan kaydın durum, cihaz veya tarih alanları değiştiğinde çalışır. Oluşturma anındaki uyarı (onchange) kapsam dışıdır.
Alternatifler: Yalnızca oluşturmada kontrol; yalnızca onay butonunun içinde kontrol.
Gerekçe: Kuralı tek yerde tutmak, buton, liste düzenleme, içe aktarma ve kod yoluyla gelen tüm girişlerin aynı kuraldan geçmesini sağlar. Butona bağlı kontrol bu yolları atlatır.
Etkisi: Metot birden fazla kaydı birlikte alabileceği için döngüyle çalışır ve her kaydı kendi dışında kalanlarla karşılaştırır. Dolu tarihler bilgisi (E4) pasif bir bilgidir, bir kontrol değildir.
README özeti: Çakışma kuralı tek bir doğrulama metodunda tutulur; arayüz, içe aktarma ve kod yoluyla ORM üzerinden yapılan tüm girişler aynı kuraldan geçer.

## C3 — Örtüşme tanımı (sınır günü)
Karar: `Date` tipi, kapalı aralık. İki kayıt `A.baslangic <= B.bitis` ve `A.bitis >= B.baslangic` ise çakışır. Aynı gün iade ve yeni teslim desteklenmez. Tarih alanları zorunludur ve `bitis >= baslangic` kısıtı vardır.
Alternatifler: `Datetime` + yarı açık aralık (aynı gün devir mümkün). `Date` + yarı açık (bir günlük zimmette sıfır uzunluklu aralık sorunu nedeniyle elendi).
Gerekçe: Saat bilgisi tutulmadığı için aynı gün devir ifade edilemez. Zimmetlerin genelde birkaç gün sürdüğü varsayımıyla bir günlük boşluk kabul edilmiş, basit ve açıklanabilir bir çakışma kuralı tercih edilmiştir.
Etkisi: Örtüşme koşulu tek metotta tutulur. Saatlik tahsis gerekirse planlanan/fiili alan tipleri ve bu koşul `Datetime` + yarı açık aralığa çevrilir. Bilinen sınırlama: ardışık zimmetler arasında en az bir gün boşluk kalır.
README özeti: Kapalı aralık kullanılır, aynı gün devir yoktur; zimmetlerin günden uzun sürdüğü varsayılmıştır.

## C4 — Gecikmiş cihaz
Karar: Onay kontrolü yalnızca planlanan tarihlere bakar; gecikmiş (`teslim_edildi` ve bitişi geçmiş) kayıt onay aşamasında ek bloklama yapmaz. Teslim aşamasında ise aynı cihaz için başka bir `teslim_edildi` kayıt varsa işlem engellenir. Bu kural da C2 gibi `@api.constrains` ile uygulanır; "Teslim Et" butonu yalnızca durumu değiştirir.
Alternatifler: Gecikmiş kaydı iade edilene kadar belirsiz bitişli sayıp onayı bloklamak.
Gerekçe: Cihazını zamanında getirmeyen bir personel yüzünden takvimin ucu açık şekilde tamamen kilitlenmesi, rezervasyon akışını felç eder. "Onaylamak" bir planlamadır ve takvime göre işletilmelidir; ancak cihazın teslim edilmesi tamamen fiziksel gerçeğe bağlıdır. İade kaydı alınmadığı sürece sistemsel olarak teslim durumuna geçiş engellenerek gerçek dünya ile veri uyumu sağlanır.
Etkisi: Onaylı bir talep, cihaz hâlâ gecikmiş kullanıcıdaysa başlangıç gününde teslim edilemeyebilir. Gecikenler listesi (E3) bu durumu yetkiliye görünür kılar.
README özeti: Onay planı, teslim ise cihazın fiziksel durumunu kontrol eder; iade kaydı alınmayan cihaz başkasına teslim edilemez, ama gecikme onayları durdurmaz.

## C5 — Uygulama yeri ve eşzamanlılık
Karar: Çakışma kuralı Python `@api.constrains` ile uygulanır. PostgreSQL `EXCLUDE` kısıtı kapsam dışıdır; eşzamanlı onayda oluşabilecek yarış durumu bilinen sınırlama olarak belgelenir.
Alternatifler: Yalnızca veritabanı kısıtı; onay anında cihaz kaydını kilitlemek.
Gerekçe: Odoo işlemleri `REPEATABLE READ` yalıtım seviyesinde çalıştırır; aynı anda onaya basan iki yetkilinin işlemi birbirinin henüz kaydedilmemiş değişikliğini göremez ve iki Python kontrolü de geçebilir (yarış durumu). Bunu kesin olarak yalnızca veritabanı kısıtı engeller. Tarih çakışması için `EXCLUDE` kısıtı gerekir; `btree_gist` eklentisi olmadan da cihaz kimliği tek elemanlı bir aralık (`int4range`) olarak yazılarak kurulabilir. Eşzamanlı onayın bu ölçekte (birkaç yetkili, düşük işlem hacmi) nadir olması nedeniyle bu kısıt kapsam dışı bırakılmış, süre çekirdek gereksinimlere ayrılmıştır.
Etkisi: C4'teki tek-zimmet kontrolü de Python'da olduğu için aynı yarışa teorik olarak açıktır. Pratikte iki eşzamanlı teslim aynı cihaz kaydındaki saklanan hesaplanan alanları (A3, E1) güncellemeye çalışacağından biri serileştirme hatası alıp yeniden denenebilir; ancak bu bir garanti olarak varsayılmaz. Sınırlama README'de yazılır.
README özeti: Çakışma kontrolü Python tarafında yapılır; eşzamanlı onayda oluşabilecek yarış durumu, bu ölçekte nadir olduğu için bilinen sınırlama olarak kabul edilmiştir. Çözüm yolu (eklentisiz `EXCLUDE` kısıtı) belirlenmiştir.

## C6 — Çakışma mesajı ve görünürlük
Karar: Çakışma sorgusu `sudo()` ile çalışır. Hata mesajında çakışan kaydın referansı ve tarihleri yalnızca yetkiliye gösterilir; diğer yollardan gelen çağrılar (ör. içe aktarma) için genel mesaj verilir.
Alternatifler: Sıradan sorgu (kayıt kuralına tabi); herkese çalışan adını göstermek.
Gerekçe: Mühendis yalnızca kendi kayıtlarını görürse (D2) kayıt kuralına tabi bir sorgu başkasının kaydını göremez ve çakışmayı sessizce kaçırırdı; kuralın kullanıcının görme yetkisinden bağımsız çalışması gerekir. Bloklayan geçişleri yalnızca yetkili yaptığı için (B2, B8) ayrıntılı mesajın tek gerçek alıcısı yetkilidir.
Etkisi: `sudo()` güvenlik kontrolünü atladığı için ayrıntı yalnızca role bakılarak gösterilir, kayıt içeriği başka kullanıcıya verilmez.
README özeti: Çakışma kontrolü `sudo()` ile tüm kayıtlara bakar; ayrıntılı bilgi yalnızca yetkiye gösterilir.

## D1 — Roller ve grup yapısı
Karar: İki grup: Mühendis (`group_zimmet_muhendis`) ve Yetkili (`group_zimmet_yetkili`). Yetkili, Mühendis'i kapsar (`implied_ids`); Mühendis standart iç kullanıcı grubunu kapsar.
Alternatifler: Üçüncü bir "teslim sorumlusu" rolü; tek grup ve alan bazlı kontrol.
Gerekçe: Belge iki rol istiyor (madde 8). Yetkili de kendi adına talep açabildiği için (B7) Mühendis haklarını kapsaması kural tekrarını önler.
Etkisi: Menü ve model yetkileri bu iki gruba bağlanır. Yönetici kullanıcı (`admin`) modül verisinde (`security.xml`) Yetkili grubuna eklenir, aksi halde menüleri görmeyebilir. Sistem hesabı (OdooBot) gruba eklenmez; testler kendi yetkili kullanıcısını oluşturur.
README özeti: Mühendis kendi taleplerini yönetir, yetkili onay, teslim, iade ve ekipman yönetimini yapar; yetkili mühendis haklarını kapsar.

## D2 — Mühendisin görünürlüğü
Karar: Mühendis yalnızca kendi zimmet kayıtlarını görür (kayıt kuralı: `calisan_id.user_id` = kullanıcı). Ekipman ve kategoriyi salt okunur görür. Başkalarının taleplerini göremez. Müsaitlik bilgisi E4'teki "dolu tarihler" alanıyla pasif olarak sağlanır.
Alternatifler: Tüm talepleri salt okunur göstermek; yalnızca ekipman listesi göstermek.
Gerekçe: Gizlilik ve basit bir kural. Aynı tarihler için iki talep açılabilir (C1); biri onaylanınca diğeri reddedilir ve sebep zorunlu red gerekçesinde yazılır (B3).
Etkisi: `ir.rule` (D5). Çakışma kontrolü başkasının kayıtlarını görmek için `sudo()` kullanır (C6).
README özeti: Mühendis yalnızca kendi taleplerini görür; cihazın dolu tarihleri ayrı bir bilgi alanından okunur.

## D3 — Başkası adına talep
Karar: Talep yalnızca kullanıcının kendi adına açılır. Başkası adına talep ve kullanıcısı olmayan çalışana zimmet kapsam dışıdır.
Alternatifler: Yetkilinin başkası adına talep açabilmesi (kullanıcısız çalışan dahil).
Gerekçe: Belge yalnızca mühendisin talep açmasını istiyor. Tüm çalışanların kullanıcı hesabı olduğu varsayımıyla talep, mühendisin kendi ekranından dakikalar içinde açılabilir; başkası adına talep rol bağımlı alan davranışı, sahiplik tanımı ve ek test yüzeyi getirirdi.
Etkisi: `calisan_id` kullanıcının kendi çalışanıdır ve sunucuda doğrulanır (A4, B8). Gerekirse alanın yetkili için düzenlenebilir olması ve `create` kontrolünün gevşemesi yeterlidir, model değişmez.
README özeti: Talep yalnızca kendi adına açılır; başkası adına talep ve kullanıcısı olmayan personele zimmet kapsam dışıdır.

## D4 — Ekipman yönetimi
Karar: Ekipman ve kategori oluşturma, düzenleme ve arşivleme yalnızca Yetkili'ye aittir. Mühendis salt okunur görür, böylece talep formunda cihaz seçebilir.
Alternatifler: Mühendisin ekipman eklemesine izin vermek.
Gerekçe: Ekipman sicili idari bir karardır. Silme hakkı yetkide olsa bile geçmişi olan kayıt `restrict` nedeniyle silinemez (A5), arşivleme kullanılır.
Etkisi: `ir.model.access.csv` (D5).
README özeti: Ekipman tanımlama yalnızca yetkilidedir.

## D5 — Yetki katmanları
Karar: Dört katman, her biri farklı bir şeyi korur:

| Katman | Ne korur | Bizdeki karşılığı |
|---|---|---|
| Model erişimi (`ir.model.access.csv`) | Grubun modele erişimi | Zimmet: Mühendis ve Yetkili okuma/yazma/oluşturma/silme; silme `unlink()` kontrolüyle yalnızca taslağa kısıtlı (B8). Ekipman ve kategori: Mühendis okuma, Yetkili tam |
| Kayıt kuralı (`ir.rule`) | Hangi kayıtlar | Zimmet: Mühendis kendi kayıtları, Yetkili tümü |
| Alan düzeyi (`groups`) | Hangi alan | "Şu an kimde" ve geçmiş yalnızca Yetkili (D6) |
| Metot ve `write`/`create` (B8) | İş kuralı | Rol, kaynak durum, doğrudan yazma koruması, çalışanın doğrulanması |

Arayüz gizlemeleri (`invisible`, `readonly`) yetki katmanı sayılmaz.
Alternatifler: Yalnızca arayüz gizlemesi; yalnızca model erişimi.
Gerekçe: Her katman başka bir saldırı yüzeyini kapatır: model erişimi hangi modele, kayıt kuralı hangi kayda, alan düzeyi hangi bilgiye, metot kontrolü hangi işleme. Mühendisin kendi kaydında yazma hakkı olduğu için `state`'in doğrudan yazılması metot kontrolüyle değil `write()` korumasıyla kapatılır (B8).
Etkisi: Yetkili'nin kayıt kuralı kısıtsızdır, Mühendis kuralı yalnızca Mühendis'e uygulanır. `calisan_id` doğrulaması kayıt kuralına değil sunucu kontrolüne (B8 `create`/`write`) dayanır. Mühendis grubunun çalışan adını formda görebilmesi için `hr.employee` okuma hakkı gerekir.
README özeti: Erişim dört katmanda uygulanır: model, kayıt, alan ve sunucu tarafı iş kuralı; arayüz gizlemesi yetki sayılmaz.

## D6 — "Kimde" bilgisinin ve geçmişin görünürlüğü
Karar: Cihazın şu an kimde olduğunu ve geçmişteki kullanıcılarını yalnızca Yetkili görür. Mühendis fiziksel durumu ve dolu tarihleri (E4) görür.
Alternatifler: Herkesin görmesi.
Gerekçe: C6'daki ad gizlemeyle tutarlı. Belge madde 6 görüntüleyecek rolü belirtmiyor, bu bir yorumdur ve README'de yazılır.
Etkisi: İlgili alanlara ve geçmiş sekmesine `groups` kısıtı. Canlı demo yetkili hesabıyla gösterilir.
README özeti: Kimde olduğu ve geçmiş bilgisi yalnızca yetkiye açıktır; mühendis yalnızca durum ve dolu tarihleri görür.

## E1 — Şu an kimde
Karar: Ekipman modelinde `su_an_kimde_id` alanı (`hr.employee`): `teslim_edildi` durumundaki zimmet kaydının çalışanı, yoksa boş. `compute + store=True`, bağımlılık zimmet durumu ve çalışan; fiziksel durum alanıyla (A3) aynı hesaplama metodunda üretilir. Birden fazla kayıt olursa çökmeden ilkini alır (C4 bunu zaten engelliyor).
Alternatifler: Saklanmayan hesaplanan alan; her seferinde sorgu.
Gerekçe: "Kimde" ana listedir (madde 6) ve filtre/gruplama gerektirir. Tek doğruluk kaynağı zimmet kayıtlarıdır, A3 ile aynı mekanizma tek açıklamayla savunulur.
Etkisi: Cihaz listesinde ve formunda gösterilir; alan D6 gereği Yetkili'ye açıktır.
README özeti: Şu an kimde bilgisi zimmet kayıtlarından hesaplanır ve saklanır; ayrıca elle tutulan bir veri yoktur.

## E2 — Geçmiş
Karar: Ayrı log yok. Cihaz formunda zimmet kayıtlarının tarihe göre azalan listesi, varsayılan olarak yalnızca `teslim_edildi` ve `iade_edildi` kayıtları (gerçekten cihazı taşıyanlar). Tüm durumlar zimmet menüsünde filtreyle görülür. Çalışan tarafında "Zimmetler" butonu kapsam dışıdır. Sekme yalnızca Yetkili'ye açıktır (D6).
Alternatifler: Ayrı geçmiş log modeli; yalnızca chatter kayıtları.
Gerekçe: Aynı bilgiyi iki yerde tutmamak. Zimmet kayıtları zaten kimde olduğunun tarihçesidir.
Etkisi: Cihaz modelinde, alan tanımında `domain` bulunan ayrı bir One2many (`gecmis_zimmet_ids`, yalnızca `teslim_edildi` ve `iade_edildi`) geçmiş sekmesinde gösterilir; tüm kayıtlar için `zimmet_ids` kullanılmaya devam eder.
README özeti: Geçmiş ayrı bir log değil, cihazın zimmet kayıtlarının tarihçesidir.

## E3 — Gecikmiş ve süresi geçmiş onaylar
Karar: İki arama filtresi: "Geciken" (`teslim_edildi` ve planlanan bitiş bugünden önce) ve "Süresi geçmiş onay" (`onaylandi` ve bitiş bugünden önce, B4). Yetkili için "Gecikenler" menüsü bu filtreyle (varsayılan arama filtresi olarak) açılır; listede geciken satırlar vurgulanır. Mühendis kendi gecikenlerini kendi listesinde filtreyle görür.
Alternatifler: Saklanan gecikme alanı ve zamanlanmış görev; saklanmayan alan ve arama metodu.
Gerekçe: B6 gereği gecikme türetilmiş bir koşuldur; filtre her zaman günceldir ve zamanlayıcı gerektirmez.
Etkisi: Bildirim gönderilmez (kapsam dışı).
README özeti: Geciken ve süresi geçmiş kayıtlar filtre ve menüyle listelenir; bildirim kapsam dışıdır.

## E4 — Dolu tarihler bilgisi
Karar: Ekipman modelinde saklanmayan hesaplanan `dolu_tarihler` metin alanı: bloklayan durumlardaki (`onaylandi`, `teslim_edildi`) kayıtların bugünden sonraki tarih aralıkları, isim ve referans olmadan. Bitişi geçmiş ama hâlâ `teslim_edildi` olan kayıt "şu an elde, iade bekleniyor" olarak dahil edilir. Sorgu `sudo()` ile yapılır. Cihaz formunda ve talep formunda (yalnızca `taslak` durumunda) gösterilir.
Alternatifler: Takvim görünümü; oluşturma anında onchange uyarısı; hiç gösterme.
Gerekçe: Mühendis başkasının kaydını görmediği için (D2) müsaitliği kendisi bilemez; bu bilgi talep açmayı kolaylaştırır ve reddedilen talepleri azaltır. Pasif bilgi olduğu için maliyeti küçüktür.
Etkisi: Yalnızca bloklayan durumlar gösterildiği için bekleyen talepler görünmez (C1); eşzamanlı onay yarışı (C5) bu bilgiyle ortadan kalkmaz.
README özeti: Cihazın onaylı ve teslim edilmiş tarih aralıkları isimsiz olarak gösterilir; bekleyen talepler görünmez.

## F1 — Menü yapısı
Karar: "Ekipman Zimmet" uygulaması altında: Zimmet Talepleri (herkes; mühendis kayıt kuralı gereği yalnızca kendi kayıtlarını görür; varsayılan "Açık Talepler" filtresiyle açılır, B3); yalnızca yetkiye açık kuyruk menüleri: Onay Bekleyenler (`talep_edildi`), Teslim Bekleyenler (`onaylandi`), Gecikenler, Süresi Geçmiş Onaylar; Ekipmanlar (herkes okur); Kategoriler (yalnızca yetkili). Kuyruk menüleri sabit `domain` yerine arama görünümündeki ilgili filtreyi varsayılan olarak açar (`search_default_*`).
Alternatifler: Tek menü ve yalnızca filtreler; her durum için ayrı menü.
Gerekçe: Kuyruk menüleri B2'deki geçiş tablosunu ekrana taşır ve yetkilinin günlük işini tek tıkla gösterir. Koşullar yalnızca arama filtrelerinde tanımlı olduğu için tek bir yerde tutulur (B6, E3); menü ve filtre birbirinden ayrışamaz. Filtre arama çubuğunda görünür, kullanıcı listenin neden süzüldüğünü görür.
Etkisi: Birkaç `ir.actions.act_window` ve menü satırı; menü erişimi gruplara bağlanır (D1).
README özeti: Yetkili için süreç adımlarına göre kuyruk menüleri, mühendis için tek bir kendi talepleri listesi vardır.

## F2 — Zimmet formu
Karar: Üstte tıklanamayan statusbar (B8) ve durumlara göre görünen butonlar: Talep Et ve Geri Çek (yalnızca talep sahibi); Onayla, Reddet, Teslim Et, İade Al (yalnızca yetkili, `groups`); İptal Et (yalnızca onay bekleyen ve onaylanmış talepte, B2); Taslağı Sil (yalnızca taslakta ve talep sahibine, onay sorar, B3). Gövdede: cihaz, çalışan (salt okunur), planlanan tarihler (yalnızca taslakta düzenlenebilir, B5), fiili tarihler (salt okunur, teslimden sonra görünür), red gerekçesi (bekleyen talepte yetkili tarafından düzenlenebilir, reddedilen talepte salt okunur görünür), dolu tarihler (yalnızca taslakta, E4). Altta chatter (G6). Buton görünürlüğü `invisible` ve `groups` ile sağlanır; asıl yetki kontrolü metottadır (B8). Talep sahipliği, ekrana bakan kullanıcıya göre değiştiği için saklanmayan hesaplanan bir alanla (`talep_sahibi_mi`, `depends_context('uid')`) belirlenir.
Alternatifler: Red için wizard (B3); tek bir "durumu değiştir" menüsü.
Gerekçe: Her buton B2'deki bir geçişe karşılık gelir; formun yapısı tabloyu birebir yansıtır.
Etkisi: Reddet butonu boş red gerekçesinde `UserError` verir (B3).
README özeti: Form, geçiş tablosundaki her adımı bir buton olarak sunar; yetki kontrolü arayüzde değil sunucuda yapılır.

## F3 — Zimmet listesi
Karar: Kolonlar: referans, cihaz, çalışan, planlanan başlangıç, planlanan bitiş, durum; fiili tarihler isteğe bağlı (varsayılan gizli). Geciken satırlar kırmızı, süresi geçmiş onaylar sarı, bekleyen talepler mavi, kapalı durumlar (iade, red, iptal) soluk. Sıralama planlanan başlangıca göre azalan.
Alternatifler: Vurgusuz sade liste.
Gerekçe: Vurgu E3'teki türetilmiş koşulları kullanır; yetkili gecikmeyi ayrı menüye girmeden görür.
Etkisi: Liste satırı vurgu ifadeleri filtre koşullarıyla tutarlı olmalıdır.
README özeti: Listede geciken ve süresi geçmiş kayıtlar renkle işaretlenir.

## F4 — Ekipman ekranları
Karar: Liste: etiket no, ad, kategori, fiziksel durum, şu an kimde (yalnızca yetkili). Form: temel bilgiler, dolu tarihler (E4), yetkiye özel "Geçmiş" sekmesi (E2). Kanban yok.
Alternatifler: Kanban kart görünümü.
Gerekçe: Ana ihtiyaç "kimde" ve "dolu tarihler" bilgisidir; kanban ek bir değer katmaz.
Etkisi: Görünürlük D6 ve D5'e göre `groups` ile sağlanır.
README özeti: Ekipman ekranı cihazın durumunu, dolu tarihlerini ve (yetkiye) geçmişini gösterir.

## F5 — Ek görünümler
Karar: Takvim, pivot, kanban ve grafik görünümleri yapılmaz; yalnızca form ve liste.
Alternatifler: Zimmet kayıtları için takvim görünümü.
Gerekçe: Gereksinim yok; E4 müsaitlik ihtiyacını karşılıyor. Takvimde isim görünürlüğü D6 kararını yeniden gündeme getirirdi.
Etkisi: Gerekirse tarih alanlarıyla bir takvim görünümü eklenir ve yetkiye kısıtlanır; model değişmez.
README özeti: Takvim, pivot ve kanban görünümleri kapsam dışıdır.

## F6 — Arama, filtre ve gruplama
Karar: Arama alanları referans, cihaz, çalışan. Filtreler: Açık Talepler (B3), durumlar, Onay Bekleyenler, Teslim Bekleyenler, Gecikenler, Süresi Geçmiş Onaylar (E3, F1). Gruplama: cihaz, çalışan, durum.
Alternatifler: Kategoriye göre gruplama (ek saklanan alan gerektirir).
Gerekçe: Gereksinimleri karşılayan en küçük küme.
Etkisi: Filtreler E3 ile aynı koşulları kullanır.
README özeti: Zimmet listesi cihaz, çalışan ve duruma göre aranır ve gruplanır.

## F7 — Arayüz dili
Karar: Etiketler doğrudan Türkçe yazılır (`string='...'`); çeviri dosyası (`.po`) kapsam dışıdır.
Alternatifler: İngilizce kaynak metin ve Türkçe çeviri dosyası.
Gerekçe: Tek dil, çeviri altyapısı gereksiz iş.
Etkisi: Odoo'nun kendi menüleri İngilizce kalabilir; istenirse demo veritabanında Türkçe dil paketi kurulur.
README özeti: Arayüz metinleri Türkçedir; çeviri altyapısı kapsam dışıdır.

## G1 — Hazır ekipman modülü kullanılsın mı?
Karar: Kendi modelimiz (`ekipman.cihaz`) kullanılır; Odoo'nun `maintenance` modülü genişletilmez.
Alternatifler: `maintenance` modülünün ekipman modelini genişletmek.
Gerekçe: `maintenance.equipment` bir cihaz sicili ve bakım talebi modelidir (ad, seri no, model, konum, garanti ve hurda tarihi; `maintenance.request` ile bakım talepleri ve bakım ekipleri). `hr` ile birlikte kurulunca otomatik kurulan `hr_maintenance` köprüsü cihazı bir çalışana veya departmana atar (`employee_id`, `assign_date`). Ancak bu atama tek bir anlık alandır: tarih aralıklı rezervasyon, talep–onay akışı, çakışma kontrolü ve atama geçmişi yoktur. Genişletmek bu özelliklerin yine yazılmasını, üstüne bakım ekipleri ve bakım talepleri gibi gereksiz kavramların bağımlılık olarak gelmesini gerektirirdi; ayrıca mevcut `employee_id` alanı "şu an kimde" (E1) hesabıyla iki doğruluk kaynağı oluştururdu.
Etkisi: Bağımlılıklar yalnızca `mail` ve `hr` kalır. Bakım süreci (bakım ekipleri, bakım talepleri, planlı bakım) gerekirse `maintenance` modülü kurulup cihaz modeli ona bağlanabilir.
README özeti: Odoo'nun bakım modülü cihazı bir çalışana atamayı destekler ama tarih aralıklı rezervasyon, onay akışı ve atama geçmişi sunmadığı için kendi modelimiz kullanılmıştır.

## G2 — Kurulan modüller ve gerekçeleri
Karar: Belgede istenen iki modülden başka modül kurulmaz: `mail` (Discuss; chatter ve durum izleme) ve `hr` (Employees; çalışan modeli).
Alternatifler: `maintenance`, `fleet` gibi ek modüller.
Gerekçe: Gereksinimler iki modülle karşılanır; ek modül bağımlılığı ve kurulum yükü getirir.
Etkisi: Kurulum çıktısında görünen diğer modüller (`resource`, `portal`, `sms`, `hr_skills` vb.) bu iki modülün bağımlılıkları ya da otomatik kurulan modülleridir, doğrudan seçilmemiştir.
README özeti: Yalnızca `mail` ve `hr` seçilmiştir; diğerleri bağımlılık olarak kurulur.

## G3 — Adlandırma kuralı
Karar: Odoo'nun kendi adları ve kalıpları (`name`, `state`, `active`, `*_id` / `*_ids` sonekleri, `action_` öneki) İngilizce kalır; bizim eklediğimiz model, alan, durum değeri ve metot adları Türkçe ASCII yazılır (`calisan_id`, `onaylandi`, `action_onayla`). Modül teknik adı `ekipman_zimmet`; modeller `ekipman.zimmet`, `ekipman.cihaz`, `ekipman.kategori`. Etiketler Türkçedir.
Alternatifler: Tüm tanımlayıcılar İngilizce; model ve durum Türkçe, alan adları İngilizce karışımı.
Gerekçe: Tüm karar belgeleri, testler, README ve sunum Türkçe terimlerle yazıldı; "zimmet" kavramının iyi bir İngilizce karşılığı yok. Karışık adlandırma kod içinde tutarsızlık yaratırdı.
Etkisi: Grup kimlikleri `group_zimmet_muhendis` ve `group_zimmet_yetkili`. Zimmet alanları: `cihaz_id`, `calisan_id`, `planlanan_baslangic`, `planlanan_bitis`, `fiili_baslangic`, `fiili_bitis`, `red_gerekcesi`. Ekipman alanları: `etiket_no`, `fiziksel_durum`, `su_an_kimde_id`, `dolu_tarihler`.
README özeti: Odoo'nun kendi adları İngilizce, bizim eklediklerimiz Türkçe ASCII yazılmıştır.

## G4 — Dosya yapısı ve yükleme sırası
Karar: `models/` (model başına bir dosya), `views/` (model başına bir dosya ve `menu_views.xml`), `security/` (`security.xml`, `ir.model.access.csv`, `ir_rule.xml`), `data/` (`sequence.xml`), `demo/`, `tests/`. Manifest'te `data` sırası: gruplar, erişim dosyası, kayıt kuralları, sıra numarası verisi, görünümler, menüler.
Alternatifler: Tek dosyada toplamak.
Gerekçe: Erişim dosyası ve kurallar gruplara, menüler görünümlerdeki action'lara başvurduğu için bu sıra zorunludur.
Etkisi: Yanlış sırada yükleme "kayıt bulunamadı" hatası verir; kurulum notlarına yazılır.
README özeti: Standart Odoo modül yapısı kullanılmış, yükleme sırası gruplardan menülere doğrudur.

## G5 — Referans numarası
Karar: `ir.sequence` ile `ZMT/0001` biçiminde, `create()` içinde atanır; `name` alanı salt okunurdur.
Alternatifler: Kayıt kimliğini (id) göstermek.
Gerekçe: Hata mesajları (C6) ve chatter için okunabilir bir kayıt adı gerekir.
Etkisi: `create()` override'ı (B8) sıra atamasını da yapar.
README özeti: Her zimmet kaydına ardışık bir referans numarası verilir.

## G6 — Chatter ve izleme
Karar: Yalnızca `mail.thread`; durum ile birlikte cihaz, çalışan, planlanan ve fiili tarihler ve red gerekçesi izlenir (`tracking=True`). Aktivite mixin'i kullanılmaz.
Alternatifler: Aktivite ve bildirimler.
Gerekçe: Bildirimler kapsam dışı (E3); izleme denetim ihtiyacını karşılıyor (B7).
Etkisi: Geçişlerin kim tarafından yapıldığı chatter'dan okunur.
README özeti: Durum değişiklikleri chatter'da izlenir; bildirim yoktur.

## G7 — Benzersizlik
Karar: Etiket no zorunlu ve benzersiz (SQL kısıtı); seri no isteğe bağlıdır.
Alternatifler: Yalnızca Python doğrulaması.
Gerekçe: Benzersizlik veritabanı seviyesinde garanti edilir.
Etkisi: Aynı etiket no ikinci kez girilemez; hata mesajı anlaşılır yazılır.
README özeti: Her cihazın etiket numarası benzersizdir.

## G8 — Otomatik testler
Karar: Mantık içeren çekirdek senaryolar Odoo test altyapısıyla otomatikleştirilir (tek dosya, `tests/test_zimmet.py`): çakışma ve sınır günü, erken iade, gecikmiş teslim, `state`'in doğrudan yazılması, `create`'te durum ve fiili tarih verilmesi, geri çekme yetkisi, geçmiş tarihli talebin gönderilmesi, taslak silme ve taslağın iptal edilememesi, `create` ve `write`'ta çalışan kontrolü, red gerekçesinin yetki ve durum kontrolü, talep sahipliği alanı, dolu tarihler ve geçmiş listesi. Testler `self.env` (süper kullanıcı, korumaları atlar) yerine `with_user` ile gerçek mühendis ve yetkili kullanıcılarla çalışır. Arayüz senaryoları elle denenir.
Alternatifler: Yalnızca elle test.
Gerekçe: Bu testler aynı zamanda `env.su`, chatter kullanıcısı ve kayıt kuralı birleşimi gibi varsayımların doğrulamasıdır.
Etkisi: Zaman daralırsa ilk elenecek kalemdir.
README özeti: Çekirdek iş kuralları otomatik testlerle doğrulanır.

## G9 — Manifest
Karar: `application=True`, `depends=['mail', 'hr']`, `license='LGPL-3'`, anlamlı `summary`, sürüm `18.0.1.0.0`.
Alternatifler: —
Gerekçe: Standart Odoo geleneği.
Etkisi: `data` listesi G4'teki sıraya uyar.
README özeti: Modül `mail` ve `hr`'ye bağlı bağımsız bir uygulamadır.

## G10 — Çoklu şirket
Karar: Kapsam dışı; modellerde `company_id` yoktur.
Alternatifler: Şirket bazlı kayıt kuralları.
Gerekçe: Gereksinim yok, tek şirket varsayılır.
Etkisi: Çoklu şirket gerekirse `company_id` ve kayıt kuralları eklenir.
README özeti: Çoklu şirket desteği kapsam dışıdır.

## H1 — Demo kullanıcıları ve çalışanlar
Karar: Beş demo kullanıcı, her biri tam bir çalışan kaydına bağlı: iki Yetkili (Nehir Sezgin, Kaan Bayrak), üç Mühendis (Defne Karadut, Tuna Akgün, Işıl Tezcan). Kullanıcılar ve çalışanlar `hr` modülünün demo verisinden bağımsız oluşturulur. Parola kullanıcı adıyla aynıdır (yalnızca demo). Yönetici kullanıcı (admin) demo dışı veride Yetkili grubuna eklenir (D1).
Alternatifler: `hr` demo çalışanlarını kullanmak; tek yetkili kullanıcı.
Gerekçe: `hr` demo verisinin içeriği sürümler arasında değişebilir ve rollerimizle eşleşmez. Yetkili kendi talebini onaylayabildiği için (B7) tek yetkili süreci tıkamaz, ama iki yetkili farklı kişilerce yapılan işlemlerin chatter'da ayrışmasını gösterir.
Etkisi: Her demo kullanıcının tam bir çalışan kaydı vardır (A4); aksi halde talep açılamaz.
README özeti: Demo veri beş kullanıcı (iki yetkili, üç mühendis) ve bağlı çalışan kayıtlarıyla gelir; giriş bilgileri README'dedir.

## H2 — Demo ekipman ve kategoriler
Karar: Üç kategori (Osiloskop, Dizüstü bilgisayar, Ölçüm cihazı) ve altı cihaz: OSC-001, OSC-002 (osiloskop), LTP-001, LTP-002 (dizüstü), MLT-001 (multimetre), SPK-001 (spektrum analizör).
Alternatifler: Tek kategori ve az cihaz.
Gerekçe: Belgedeki örneklerle (osiloskop, laptop, ölçüm cihazı) uyumlu; her senaryo için ayrı bir cihaz olduğundan senaryolar birbirini bozmaz.
Etkisi: Etiket no benzersizdir (G7).
README özeti: Demo veri üç kategoriden altı cihaz içerir.

## H3 — Demo zimmet kayıtları
Karar: Aşağıdaki 12 kayıt, bugüne göre göreli tarihlerle oluşturulur (G = bugün):

| # | Cihaz | Çalışan | Durum | Planlanan aralık | Gösterdiği |
|---|---|---|---|---|---|
| 1 | OSC-001 | Defne | teslim_edildi | G-10 … G-3 | Geciken zimmet (E3), "kimde" (E1), "şu an elde" (E4) |
| 2 | OSC-001 | Tuna | onaylandi | G … G+4 | Gecikme onayı bloklamaz; aralık bugünü kapsadığı halde teslim, cihaz hâlâ 1'de olduğu için hata verir (C4) |
| 3 | LTP-001 | Tuna | talep_edildi | G+3 … G+7 | Çakışan bekleyen talep 1 (C1, C2) |
| 4 | LTP-001 | Işıl | talep_edildi | G+5 … G+9 | Çakışan bekleyen talep 2: biri onaylanınca diğeri hata verir |
| 5 | SPK-001 | Defne | iade_edildi | G-25 … G-20 | Geçmiş (E2) |
| 6 | SPK-001 | Işıl | iade_edildi | G-12 … G-8 | Geçmiş |
| 7 | SPK-001 | Tuna | teslim_edildi | G-2 … G+3 | Şu an kimde; iade alma |
| 8 | OSC-002 | Işıl | onaylandi | G … G+3 | Aralığı bugünü kapsayan onay: canlı "Teslim Et" |
| 9 | OSC-002 | Tuna | reddedildi | G+1 … G+4 | Red gerekçesi (B3, D2) |
| 10 | LTP-002 | Işıl | onaylandi | G-10 … G-6 | Süresi geçmiş onay (B4, E3) |
| 11 | LTP-002 | Defne | iptal | G+10 … G+12 | Kapalı durum bloklamaz (C1) |
| 12 | MLT-001 | Tuna | taslak | G … G+2 | Canlı demo başlangıcı: gönder, onayla, teslim et, iade al |

Fiili tarihler: 1 için G-10 başlangıç; 5 için G-25 / G-21; 6 için G-12 / G-9; 7 için G-2 başlangıç. 9 numaralı kayıtta red gerekçesi: "Aynı tarihlerde başka bir talep onaylandı; lütfen farklı tarihlerle yeniden talep açın."
Alternatifler: Yalnızca birkaç sade kayıt; sabit tarihli kayıtlar.
Gerekçe: Her kayıt bir gereksinimi veya kararı canlı gösterir; yukarıdaki tablo sunumdaki demo akışının iskeletidir. Bloklayan durumdaki kayıtlar birbiriyle çakışmaz, çakışan taleplerin ikisi de bekleyen durumdadır. Teslim hatası gösterecek kaydın (2) aralığı bugünü kapsar; aksi halde hata, gösterilmek istenen kuraldan (C4) değil teslim zamanlaması kuralından (B4) gelirdi.
Etkisi: Demo kayıtları durumlarıyla doğrudan oluşturulur; bu `create()` korumasından (B8) yalnızca `sudo` ortamında, yani veri yüklemesinde geçer.
README özeti: Demo veri, her biri bir gereksinimi gösteren on iki zimmet kaydı içerir (çakışma, gecikme, red, geçmiş, canlı akış).

## H4 — Göreli tarihler
Karar: Demo tarihleri sabit değil, yükleme gününe göre hesaplanır (`bugün ± N gün`).
Alternatifler: Sabit tarihler.
Gerekçe: Gecikmiş, süresi geçmiş ve "bugün aralıkta" senaryoları sabit tarihle zamanla bozulur; sunum günü farklı bir tarihte olabilir.
Etkisi: Tarih alanları `eval` ifadeleriyle yazılır. Sınırlama: veritabanı ay sonra yüklenmiş olsa bile tarihler yükleme anına göre kalır; sunum günü veritabanı yeniden oluşturulursa senaryolar taze olur.
README özeti: Demo tarihleri yükleme gününe göre hesaplanır, senaryolar her zaman geçerlidir.

## H5 — Yükleme biçimi
Karar: Demo dosyaları manifest'te `demo` anahtarında listelenir: `demo/kullanicilar.xml`, `demo/ekipman.xml`, `demo/zimmet.xml`. README'de veritabanının demo verisi açık oluşturulması gerektiği yazılır.
Alternatifler: Demo verisini `data` anahtarına koymak (her kurulumda yüklenir).
Gerekçe: Odoo geleneği demo verisini `demo` anahtarında tutar; üretim veritabanına demo kullanıcı ve kayıt yüklemek yanlıştır.
Etkisi: Demo kapalı oluşturulmuş bir veritabanında senaryo verisi yoktur; bu sınırlama README'de açık yazılır. Demo dışı veri (gruplar, sıra numarası, yönetici kullanıcının gruba eklenmesi) `data` altındadır.
README özeti: Demo verisi yalnızca "demo verisiyle" oluşturulan veritabanlarında yüklenir.

## H6 — Demo kullanıcılarla sunum akışı
Karar: Sunumda sırasıyla: (1) yetkili hesabıyla geciken ve süresi geçmiş kayıtlar, ekipman geçmişi; (2) çakışan iki bekleyen talepte biri onaylanır, diğeri hata verir; (3) gecikmiş cihazda teslim hatası; (4) mühendis hesabıyla yalnızca kendi kayıtları ve dolu tarihler; (5) taslak kaydın gönder, onayla, teslim et, iade al akışı, onay adımında debugger.
Alternatifler: Boş veritabanında sıfırdan akış.
Gerekçe: Sunumun 3. ve 4. maddeleri (canlı demo, debugger) tek bir veriyle ve hazır senaryolarla daha güvenli gösterilir.
Etkisi: Demo kayıtları H3'teki gibi sunum sırasıyla uyumludur; canlı akış için 12 numaralı taslak ve 8 numaralı bugünü kapsayan onay kullanılır.
README özeti: Demo hesaplarıyla sunum akışı README'de adım adım verilir.

## README için derlemeler

### Belge dışı kararlar
- Tek cihaz / tek talep (A0)
- Yetkili kendi talebini onaylayabilir (B7)
- Erken teslim yok, aralığı geçmiş onay teslim edilmez (B4)
- Onaydan önce taslağa geri çekme (B5)
- "Kimde" ve geçmiş bilgisi yalnızca yetkiye açık (D6)
- Dolu tarihler bilgisi (E4)

### Bilinen sınırlamalar
- İade kaydı geç basılırsa kayıttaki tarih gerçek tarihten geç olur; geçmişe dönük düzeltme yok (A2)
- Ardışık zimmetler arasında en az bir gün boşluk kalır (C3)
- Eşzamanlı onayda çakışan iki onay oluşabilir; veritabanı kısıtı kapsam dışıdır, çözüm yolu belirlenmiştir (C5)
- Bekleyen talepler dolu tarihlerde görünmez, mühendis müsaitliği talep açmadan önce eksiksiz göremez (E4)
- Üzerinde cihaz olan çalışanın arşivlenmesi engellenmez (A5)
- Onay sonrası çakışan talepler otomatik reddedilmez (C1)

### Kapsam dışı
- Başkası adına talep, kullanıcısı olmayan personele zimmet (D3)
- E-posta ve diğer bildirimler (E3)
- Zamanlanmış görevler (B6)
- PostgreSQL `EXCLUDE` kısıtı (C5)
- Oluşturma anında çakışma uyarısı (C2)
- Çalışan tarafında "Zimmetler" butonu (E2)
- Onaydan sonra geri alma (B5)
- Çoklu cihazlı talep (A0)