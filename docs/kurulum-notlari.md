# Kurulum Notları

## Ortam
| Bileşen | Değer |
|---|---|
| İşletim sistemi | Arch Linux, doğrudan kurulum (Docker ve WSL kullanılmadı) |
| Odoo | 18.0 Community, resmi depodan kaynak koddan; dal `18.0`, commit `0f474b81` |
| Python | 3.14.7, sanal ortam (`venv`) |
| PostgreSQL | 18.6, aynı makinede |
| Editör | VS Code `1.140.0`, doğrudan Linux üzerinde |
| Yapılandırma | `odoo.conf` (repo dışında); örnek: `odoo.conf.example`. Modül klasörü ayrı bir dizinde tutulur ve `addons_path` ile tanıtılır |

## Kurulum adımları
1. PostgreSQL kullanıcı oluşturma: `createuser -s odoo`
2. Odoo kaynak kodu: `git clone https://github.com/odoo/odoo.git --branch 18.0 --depth 1`
3. Sanal ortam ve bağımlılıklar: `python -m venv venv`, `source venv/bin/activate`, `pip install -r odoo/requirements.txt`
4. `odoo.conf` yazılması: `addons_path`, `db_user` ve diğer satırlar tanımlandı.
5. İlk kurulum: `./odoo-bin -c ../odoo.conf -d zimmet_db -i base --stop-after-init`
6. `mail` ve `hr` kurulumu: `./odoo-bin -c ../odoo.conf -d zimmet_db -i hr,mail --stop-after-init`
7. Modül kurulumu (demo verisiyle; `mail` ve `hr` bağımlılık olarak kendiliğinden kurulur): `./odoo-bin -c ../odoo.conf -d zimmet_db -i ekipman_zimmet --stop-after-init`. Kod değiştikten sonra güncelleme: `-i` yerine `-u ekipman_zimmet`. Otomatik testler ayrı bir veritabanında: `./odoo-bin -c ../odoo.conf -d zimmet_test -i ekipman_zimmet --test-enable --test-tags /ekipman_zimmet --stop-after-init`
8. Debugger: depodaki `.vscode/launch.json.example`, çalışma klasöründe (`odoo/`, `venv/` ve `odoo.conf`'un bulunduğu klasör) `.vscode/launch.json` olarak kopyalanır. VS Code bu klasörle açılır, "Odoo 18: Zimmet" yapılandırması başlatılır (`debugpy`, `zimmet_db` veritabanı) ve modül koduna (ör. `models/zimmet.py` içinde `action_onayla`) breakpoint konur.

## Karşılaşılan sorunlar ve çözümleri
| # | Sorun | Nasıl fark edildi | Neden | Çözüm | Doğrulama |
|---|---|---|---|---|---|
| 1 | `addons_path` modül klasörünün kendisini gösteriyordu | İlk kurulum çıktısındaki "addons paths" satırında, kendi modülümüzün klasörü doğrudan listedeydi (kurulum başarılı, ama modül henüz yoktu) | Odoo yolun altındaki klasörlerde modül arar; yol modül klasörünün kendisi olursa modül görünmez | Yol, modülü barındıran repo klasörüne çevrildi | İkinci kurulum çıktısında yeni yol loglardan görüldü |

## Python sürümü kararı
- **Seçim:** Python 3.14.7. Odoo'nun `requirements.txt` dosyasında 3.14 için ayrı sürüm sabitlemeleri vardı (`lxml`, `Pillow`, `greenlet` vb.).
- **Risk:** Bu sabitlemelerin varlığı, kodun 3.14'te çalıştığını kanıtlamaz; yalnızca düşünüldüğünü gösterir.
- **Sonuç:** `base`, `hr` ve `mail` modüllerinin kurulumu hatasız tamamlandı. Kurulan Odoo kaynağı 3.14'ü açıkça destekliyor: `odoo/__init__.py` içinde `MAX_PY_VERSION = (3, 14)`. Modül demo verisiyle sıfırdan kuruldu, art arda iki güncellemede (`-u`) uyarı vermedi ve otomatik testlerin tamamı geçti.
- **Geri dönüş planı:** Sorun çıkarsa Python 3.12 ile yeni bir venv kurulacak (`python3.12 -m venv venv`).

## Zararsız log mesajları
- **wkhtmltopdf uyarıları:** PDF rapor yazdırmak için gerekir; bu modül PDF raporu kullanmıyor.
- **`phonenumbers` mesajı** (`sms` modülünden): Telefon doğrulaması devre dışı kalır; senaryoda kullanılmıyor.
- **`<string>:38: (ERROR/3) Unexpected indentation.`** ve ardından gelen `(WARNING/2)` satırı: `mail` modülü kurulurken, Odoo modül açıklama metnini (reStructuredText) çözümlerken yazılır. Bizim modülümüzle ilgisi yoktur; kurulumun sonucunu etkilemez.

## Doğrulama
- [x] Odoo `18.0` sürümü log'da görünüyor
- [x] `base`, `hr`, `mail` hatasız kuruldu
- [ ] Web arayüzüne giriş yapıldı
- [ ] VS Code'dan debugger ile başlatıldı, breakpoint'te duruldu
- [x] Kendi modülümüz demo verisiyle sıfırdan kuruldu; art arda iki güncellemede (`-u`) hata ve uyarı yok
- [x] Otomatik testler geçti (`--test-enable --test-tags /ekipman_zimmet`)
