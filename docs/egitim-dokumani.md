# Ekipman Zimmet — Kullanıcı Eğitim Dokümanı

Bu doküman, Ekipman Zimmet uygulamasını günlük işinde kullanacak mühendisler ve yetkililer içindir. Teknik bilgi gerektirmez.

## 1. Uygulama ne işe yarar?

Şirketteki ortak ekipmanlar (osiloskop, dizüstü bilgisayar, ölçüm cihazları) belirli tarihler için bir kişiye zimmetlenir. Uygulama bu süreci baştan sona takip eder: cihazın istenmesi, onaylanması, teslim edilmesi ve iade alınması. Böylece:

- Bir cihazın şu an kimde olduğu her zaman bilinir.
- Aynı cihaz aynı tarihler için iki kişiye verilemez.
- İade tarihi geçmiş cihazlar listede hemen görünür.

İki rol vardır:

| Rol | Ne yapar |
|---|---|
| **Mühendis** | Kendi adına cihaz talep eder, talebini takip eder. |
| **Yetkili** | Talepleri onaylar veya reddeder, cihazı teslim eder ve iade alır, ekipmanları tanımlar. Yetkili, mühendisin yapabildiği her şeyi de yapabilir. |

## 2. Temel kavramlar

**Talep (zimmet kaydı):** Bir cihazın belirli tarihler arasında size verilmesi isteği. Her talep tek bir cihaz içerir ve `ZMT/0001` gibi bir referans numarası alır. Talep, cihaz iade edilene kadar aynı kayıt üzerinde ilerler.

**Talebin aşamaları:** Formun sağ üstündeki durum çubuğunda talebin hangi aşamada olduğu görünür.

| Aşama | Anlamı | Sıradaki adım |
|---|---|---|
| **Taslak** | Talep hazırlanıyor, henüz gönderilmedi. | Mühendis "Talep Et"e basar. |
| **Talep Edildi** | Yetkilinin onayını bekliyor. | Yetkili onaylar veya reddeder. |
| **Onaylandı** | Tarihler size ayrıldı, cihaz henüz verilmedi. | Planlanan tarihte yetkili cihazı teslim eder. |
| **Teslim Edildi** | Cihaz sizde. | Bitiş tarihinde cihazı yetkiliye iade edersiniz. |
| **İade Edildi** | Cihaz geri alındı; süreç tamamlandı. | — |
| **Reddedildi** | Yetkili talebi kabul etmedi; gerekçesi formda yazar. | Gerekirse yeni talep açılır. |
| **İptal** | Talep iptal edildi; nedeni formda yazar. | — |

**Planlanan ve fiili tarihler:** Planlanan tarihler talep ederken sizin seçtiğiniz tarihlerdir. Fiili tarihler, cihazın gerçekten verildiği ve geri alındığı günlerdir; yetkili "Teslim Et" ve "İade Al" butonlarına bastığında sistem tarafından otomatik yazılır.

**Dolu tarihler:** Bir cihazın onaylanmış veya şu an birinde olan tarih aralıkları. Talep oluştururken cihazı seçtiğinizde formda görünür; böylece cihazın hangi günler boş olduğunu talep göndermeden önce görebilirsiniz. Kimin kullandığı gösterilmez.

**Gecikmiş zimmet:** Teslim edilmiş ve planlanan bitiş tarihi geçmiş, ama henüz iade edilmemiş kayıt. Listelerde kırmızı görünür.

## 3. Mühendis için

### Talep oluşturma

1. **Ekipman Zimmet → Zimmet Talepleri** menüsünü açın ve **Yeni**'ye basın.
2. **Cihaz** alanından istediğiniz cihazı seçin. Cihazlar etiket numarası ve adıyla listelenir (ör. "[LTP-001] MacBook Pro 14 M1 Pro"); seçtiğiniz cihazın açıklaması (ör. "16 GB RAM, 512 GB SSD, şarj adaptörü ile") hemen altında görünür. Altında ayrıca **Dolu Tarihler** görünür; seçeceğiniz tarihlerin bu aralıklarla çakışmamasına dikkat edin.
3. **Planlanan Başlangıç** ve **Planlanan Bitiş** tarihlerini girin. **Çalışan** alanı sizin adınızla otomatik dolar, değiştirilemez.
4. Kaydedin. Talep **Taslak** olarak saklanır; bu aşamada istediğiniz kadar düzenleyebilirsiniz.
5. Hazır olduğunuzda **Talep Et**'e basın. Talep **Talep Edildi** aşamasına geçer ve yetkiliye ulaşır.

> **[Ekran görüntüsü 1 — `img/egitim/01-talep-formu.png`]** Mühendis hesabıyla taslak bir talep formu: cihaz, dolu tarihler, planlanan tarihler ve "Talep Et" butonu.

Birden fazla cihaza ihtiyacınız varsa her cihaz için ayrı talep açın.

### Talebi düzeltme, geri çekme ve iptal

- **Gönderdiğiniz talepte hata varsa:** Talep henüz onaylanmadıysa **Geri Çek**'e basın. Talep tekrar **Taslak** olur; düzeltip yeniden **Talep Et**'e basın.
- **Onaylanmış talep düzenlenemez.** Tarih değişikliği gerekiyorsa talebi iptal edip yenisini açın.
- **İptal Et:** Onay bekleyen veya onaylanmış (henüz teslim edilmemiş) talebinizi iptal edebilirsiniz. Önce formdaki **İptal Nedeni** alanını doldurun (ör. "Artık ihtiyacım kalmadı."), sonra **İptal Et**'e basın; neden boşken iptal yapılamaz. Onaylı bir talebi iptal etmek, o tarihleri başkalarının kullanımına açar; ihtiyacınız kalmadıysa iptal etmeniz rica edilir.
- **Taslağı Sil:** Hiç gönderilmemiş bir taslaktan vazgeçtiyseniz formdaki **Taslağı Sil**'e basın; onayınız sorulur ve taslak kalıcı olarak silinir. Taslaklar iptal edilmez, silinir. Gönderilmiş talepler geçmiş kaydı olarak kalır; iptal edilir ama silinmez.

### Talebinizi takip etme

**Zimmet Talepleri** listesinde yalnızca kendi talepleriniz görünür. Liste varsayılan olarak **Güncel Talepler** filtresiyle açılır: açık talepleriniz ve son bir hafta içinde kapanmış (iade edilen, reddedilen, iptal edilen) talepleriniz görünür. Böylece reddedilen veya iptal edilen bir talebinizi fark eder, nedenini formda okursunuz. Yalnızca açık talepleri görmek için arama çubuğundan **Açık Talepler**'i seçin; daha eski kapanmış talepler için filtreyi kaldırın. Satır renkleri: mavi = onay bekliyor, sarı = onaylanmış ama tarihi geçmiş (teslim edilmemiş), kırmızı = iadesi gecikmiş, soluk = tamamlanmış (iade, red, iptal).

> **[Ekran görüntüsü 2 — `img/egitim/02-muhendis-liste.png`]** Mühendisin kendi talepleri listesi; farklı aşamalardaki talepler ve renkler.

- **Reddedildiyse:** Talebi açın; yetkilinin yazdığı **Red Gerekçesi** formda görünür. Genellikle farklı tarihlerle yeni bir talep açmanız yeterlidir.
- **Onaylandıysa:** Planlanan başlangıç tarihinde cihazı yetkiliden alın. Yetkili teslimi sisteme işlediğinde talebiniz **Teslim Edildi** olur.
- **İade:** Planlanan bitiş tarihine kadar cihazı yetkiliye teslim edin. Yetkili iadeyi sisteme işler. Cihazı erken getirebilirsiniz; kalan günler başkalarının kullanımına açılır.
- **Formun altındaki kayıt geçmişi**, talebin kim tarafından ve ne zaman onaylandığını, teslim edildiğini gösterir.

### Süreyi uzatma

Cihaza planladığınızdan daha uzun süre ihtiyacınız varsa, talebiniz onaylandıktan sonra veya cihaz elinizdeyken uzatma isteyebilirsiniz:

1. Talebinizi açın ve **İstenen Bitiş** alanına yeni bitiş tarihini yazıp kaydedin. Yeni tarih mevcut bitişten sonra olmalı ve bugünden önce olamaz.
2. Formun üstünde "Uzatma isteği yetkili onayını bekliyor." bandı görünür. Ayrıca bir butona basmanız gerekmez.
3. Yetkili onaylarsa **Planlanan Bitiş** yeni tarihe güncellenir. Reddederse istenen tarih temizlenir ve formun altındaki kayıt geçmişinde reddedildiği yazar.
4. Vazgeçerseniz **Uzatmayı Geri Çek**'e basın.

İade tarihini kaçırdıysanız (cihaz hâlâ sizdeyse) de uzatma isteyebilirsiniz; onaylanırsa kaydınız geciken listesinden çıkar. Uzatma, aynı tarihlere başka biri için verilmiş bir onayla çakışıyorsa onaylanamaz.

### Ekipmanlara göz atma

**Ekipmanlar** menüsünde tüm cihazları görebilirsiniz. **Fiziksel Durum** sütunu cihazın şu an birinde olup olmadığını ("Zimmette" / "Zimmette değil") gösterir. Cihazı açıp **Müsaitlik Bilgisi** sekmesinden dolu tarihlerine bakabilirsiniz. Cihazın kimde olduğu ve geçmiş kullanıcıları yalnızca yetkililere görünür.

## 4. Yetkili için

Yetkili menüsünde, günlük işinizi aşama aşama gösteren kuyruklar vardır. Her kuyruk ilgili filtreyle açılır; filtre arama çubuğunda görünür ve kaldırılırsa tüm kayıtlar listelenir.

| Menü | İçindekiler | Yapılacak iş |
|---|---|---|
| **Onay Bekleyenler** | Gönderilmiş talepler | Onaylamak veya reddetmek |
| **Teslim Bekleyenler** | Onaylanmış, cihazı henüz verilmemiş talepler | Cihazı verirken teslimi işlemek |
| **Gecikenler** | İade tarihi geçmiş zimmetler | Kişiyle iletişime geçmek, cihaz gelince iadeyi işlemek |
| **Süresi Geçmiş Onaylar** | Bitiş tarihi geçmiş ama hiç teslim edilmemiş onaylar | İptal etmek |
| **Uzatma Bekleyenler** | Süre uzatma isteği olan talepler | Uzatmayı onaylamak veya reddetmek |

> **[Ekran görüntüsü 3 — `img/egitim/03-onay-bekleyenler.png`]** Yetkili hesabıyla "Onay Bekleyenler" listesi; arama çubuğundaki filtre etiketi.

### Onaylama ve reddetme

1. **Onay Bekleyenler**'den talebi açın.
2. Uygunsa **Onayla**'ya basın. Sistem, aynı cihazın aynı tarihlerde onaylanmış başka bir talebi olup olmadığını kontrol eder; çakışma varsa onaya izin vermez ve çakışan talebin numarasını ve tarihlerini gösterir.
3. Uygun değilse **Red Gerekçesi** alanına nedenini yazın ve **Reddet**'e basın. Gerekçe boşken reddetme yapılamaz. Gerekçe, talep sahibine formda görünür; karar verildikten sonra değiştirilemez.

> **[Ekran görüntüsü 4 — `img/egitim/04-onay-formu.png`]** Onay bekleyen bir talebin formu: Onayla, Reddet ve Red Gerekçesi alanı.

Aynı cihaz için aynı tarihlere iki ayrı talep gelebilir. Birini onayladığınızda diğeri kendiliğinden reddedilmez; onu gerekçe yazarak siz reddedersiniz (örneğin "Aynı tarihlerde başka bir talep onaylandı; lütfen farklı tarihlerle yeniden talep açın.").

> **[Ekran görüntüsü 5 — `img/egitim/05-cakisma-uyarisi.png`]** Çakışan ikinci talep onaylanmaya çalışıldığında çıkan uyarı.

Kendi talebinizi de onaylayabilirsiniz; işlem formun altındaki kayıt geçmişinde adınızla görünür.

### Uzatma isteklerini onaylama

**Uzatma Bekleyenler**'den talebi açın; istenen yeni bitiş tarihi formda görünür. **Uzatmayı Onayla** planlanan bitişi yeni tarihe taşır; yeni tarihler aynı cihazın onaylı başka bir talebiyle çakışıyorsa sistem çakışan talebi göstererek onaya izin vermez. **Uzatmayı Reddet** isteği temizler ve kayıt geçmişine not düşer.

### Teslim etme ve iade alma

- **Teslim Et:** Cihazı fiziksel olarak verdiğiniz anda **Teslim Bekleyenler**'den talebi açıp **Teslim Et**'e basın. Fiili başlangıç tarihi bugün olarak yazılır. Teslim yalnızca planlanan tarih aralığı içinde yapılabilir; erken teslim yapılamaz.
- **Cihaz hâlâ başkasındaysa** (önceki kullanıcı iade etmediyse) teslim yapılamaz. Önce önceki kullanıcının iadesini alın; ardından teslimi işleyin.
- **İade Al:** Cihaz geri geldiği gün ilgili talebi (örneğin **Gecikenler**'den) açıp **İade Al**'a basın. Fiili bitiş tarihi bugün olarak yazılır. İadeyi cihazın geldiği gün işleyin; tarih sonradan geriye düzeltilemez.

> **[Ekran görüntüsü 6 — `img/egitim/06-gecikenler.png`]** "Gecikenler" listesi; kırmızı satırlar.

### Süresi geçmiş onaylar

Onaylanmış ama tarihi geçtiği halde hiç teslim edilmemiş talepler artık teslim edilemez. Bunları **Süresi Geçmiş Onaylar**'dan açıp iptal nedenini (ör. "Süresi geçti, teslim edilmedi.") yazarak **İptal Et** ile kapatın; kişinin hâlâ ihtiyacı varsa yeni tarihlerle talep açması gerekir.

### Ekipman ve kategori tanımlama

- **Ekipmanlar → Yeni:** **Cihaz Adı** (herkesin tanıyacağı ad, ör. "MacBook Pro 14 M1 Pro"), **Etiket No** (cihazın üzerindeki demirbaş etiketi, ör. "LTP-001"), **Açıklama** (cihazı benzerlerinden ayıran ayrıntılar, ör. "16 GB RAM, 512 GB SSD, şarj adaptörü ile"), **Seri No** (isteğe bağlı) ve **Kategori** girilir. Etiket numarası her cihaz için farklı olmalıdır.
- **Kategoriler** menüsünden yeni kategori eklenebilir (örneğin "Osiloskop", "Dizüstü bilgisayar").
- **Kullanımdan kaldırma:** Cihazı silmek yerine arşivleyin (form üzerindeki işlem menüsünden **Arşivle**). Geçmiş zimmet kaydı olan cihaz silinemez. Onaylı veya teslim edilmiş talebi olan cihaz arşivlenemez; önce o talepleri tamamlayın veya iptal edin. Arşivlenen cihazlar ekipman listesinde **Arşivlenenler** filtresiyle görülür.

### Cihaz şu an kimde, daha önce kimdeydi?

- **Ekipmanlar** listesindeki **Şu An Kimde** sütunu cihazın kimde olduğunu gösterir. **Zimmetteki Cihazlar** filtresi yalnızca şu an birinde olan cihazları listeler.
- Cihazı açtığınızda **Zimmet Geçmişi** sekmesi, cihazı daha önce teslim alan herkesi tarihleriyle gösterir.

> **[Ekran görüntüsü 7 — `img/egitim/07-ekipman-gecmis.png`]** Yetkili hesabıyla bir cihaz formu: "Şu An Kimde" alanı ve "Zimmet Geçmişi" sekmesi.

## 5. Uyarı mesajları ve ne yapmalı

| Mesaj | Anlamı | Ne yapmalı |
|---|---|---|
| Çalışan profiliniz bulunmuyor. | Kullanıcı hesabınız bir çalışan kaydına bağlı değil. | Sistem yöneticisinden hesabınızı çalışan kaydınıza bağlamasını isteyin. |
| Bitiş tarihi, başlangıç tarihinden önce olamaz. | Tarihler ters girilmiş. | Tarihleri düzeltin. |
| Başlangıç tarihi geçmiş bir talep gönderilemez. Lütfen tarihleri güncelleyin. | Taslağın başlangıç tarihi bugünden önce. | Tarihleri bugün veya sonrası olacak şekilde düzeltip tekrar gönderin. |
| ZMT/… referanslı kayıtla … tarihleri arasında çakışıyor. | Cihaz bu tarihlerde başka bir onaylı talebe ayrılmış. | Talebi gerekçe yazarak reddedin; kişi farklı tarihlerle yeni talep açsın. |
| Reddetmek için red gerekçesi doldurulmalıdır. | Gerekçe alanı boş. | Red Gerekçesi alanını doldurup tekrar Reddet'e basın. |
| Teslimat yalnızca planlanan tarih aralığında yapılabilir. Erken veya süresi geçmiş teslimat yapılamaz. | Bugün, talebin planlanan aralığında değil. | Erkense başlangıç tarihini bekleyin; süresi geçmişse talebi iptal edin. |
| Bu cihaz şu anda başka bir çalışana teslim edilmiş durumdadır. Önce iade alınması gerekir. | Önceki kullanıcı cihazı henüz iade etmedi. | **Gecikenler**'den önceki kaydın iadesini alın, sonra teslimi işleyin. |
| Yalnızca … durumundaki kayıtlar onaylanabilir / teslim edilebilir / … | Kayıt, siz ekranı açtıktan sonra başka biri tarafından değiştirilmiş. | Sayfayı yenileyip talebin güncel aşamasına bakın. |
| Yalnızca taslak durumundaki kayıtlar silinebilir. | Gönderilmiş talepler silinemez. | Gerekirse **İptal Et** kullanın. |
| İptal etmek için iptal nedeni doldurulmalıdır. | İptal Nedeni alanı boş. | Nedeni yazıp tekrar **İptal Et**'e basın. |
| Yalnızca kendi taslaklarınızı silebilirsiniz. | Başka birinin taslağını silmeye çalıştınız. | Taslak, sahibi tarafından silinir; gönderildiğinde yetkili onaylayabilir veya reddedebilir. |
| Bu etiket numarasına sahip bir cihaz zaten mevcut! | Aynı etiket numarası başka bir cihazda var. | Farklı bir etiket numarası girin. |
| Geçmiş zimmet kaydı olan cihaz silinemez, arşivleyiniz. | Cihazın geçmişi korunmalı. | Cihazı arşivleyin. |
| Aktif zimmeti olan cihaz arşivlenemez. | Cihazın onaylı veya teslim edilmiş talebi var. | Önce talepleri tamamlayın veya iptal edin. |
| İstenen bitiş, mevcut bitiş tarihinden sonra olmalıdır. | Uzatma için daha erken veya aynı tarih girildi. | Daha ileri bir tarih girin; erken bırakmak için cihazı iade edin. |
| İstenen bitiş bugünden önce olamaz. | Uzatma için geçmiş bir tarih girildi. | Bugün veya sonrası bir tarih girin. |
| Uzatma yalnızca onaylı veya teslim edilmiş talepte istenebilir. | Talep henüz onaylanmamış veya kapanmış. | Onay bekleyen talepte tarihi düzeltmek için talebi geri çekin. |

## 6. Akılda tutulacak kurallar

- Her talep tek bir cihaz içerir.
- Onay bekleyen talepler tarihleri ayırmaz; tarihler ancak onaylandığında ayrılır. Aynı tarihlere birden fazla kişi talep açabilir, yalnızca biri onaylanır.
- Aynı cihaz için iki talebin tarihleri aynı günü paylaşamaz: bir talep ayın 10'unda bitiyorsa sonraki talep en erken 11'inde başlayabilir.
- Cihaz planlanan başlangıç tarihinden önce teslim edilemez; iade ise her zaman yapılabilir.
- Onaylanmış talep düzenlenemez; değişiklik için iptal edip yeni talep açılır.
- Teslim ve iade tarihleri sistem tarafından o günün tarihiyle yazılır ve sonradan değiştirilemez.

## Ek: Demo verisiyle deneyin

Demo verisiyle kurulmuş bir veritabanında aşağıdaki adımlarla uygulamayı uçtan uca deneyebilirsiniz. Kullanıcıların parolası kullanıcı adıyla aynıdır. Talep numaraları, veritabanı sıfırdan kurulduğunda geçerlidir.

1. **Mühendis olarak talep:** `tunaakgun` ile girin. **Zimmet Talepleri**'nde **ZMT/0012** (multimetre, taslak) talebini açın ve **Talep Et**'e basın.
2. **Yetkili olarak onay, teslim ve iade:** `nehirsezgin` ile girin. **Onay Bekleyenler**'den ZMT/0012'yi **Onayla**'yın; **Teslim Bekleyenler**'den **Teslim Et**'e, ardından **İade Al**'a basın. Formun altındaki kayıt geçmişinde her adımı kimin yaptığını görün.
3. **Çakışma:** Aynı kullanıcıyla **Onay Bekleyenler**'de dizüstü bilgisayar için çakışan iki talep vardır (ZMT/0003 ve ZMT/0004). Birini onaylayın; diğerini onaylamaya çalıştığınızda çakışma uyarısı çıkar.
4. **Uzatma:** **Uzatma Bekleyenler**'de iki istek vardır. ZMT/0007'nin (spektrum analizör) uzatmasını onaylayın: bitiş tarihi ilerler. ZMT/0001'in (osiloskop, gecikmiş) uzatmasını onaylamaya çalışın: aynı osiloskobun ZMT/0002 talebiyle çakıştığı için sistem izin vermez.
5. **Gecikmiş cihaz:** **Gecikenler**'de ZMT/0001'i (osiloskop, Defne) görün. **Teslim Bekleyenler**'deki ZMT/0002 aynı osiloskobun bugün başlayan talebidir; **Teslim Et**'e bastığınızda "Önce iade alınması gerekir" uyarısı çıkar. ZMT/0001'in iadesini aldıktan sonra ZMT/0002 teslim edilebilir.
6. **Süresi geçmiş onay ve red:** **Süresi Geçmiş Onaylar**'da ZMT/0010'u görün. Reddedilmiş ZMT/0009'u açıp red gerekçesini okuyun.
7. **Ekipman geçmişi:** **Ekipmanlar**'dan spektrum analizörünü (SPK-001) açın; **Şu An Kimde** alanını ve **Zimmet Geçmişi** sekmesini inceleyin.
8. **Mühendisin görünürlüğü:** `defnekaradut` ile girin. **Zimmet Talepleri**'nde yalnızca Defne'nin kendi talepleri görünür; ekipman listesinde **Şu An Kimde** sütunu yoktur.
