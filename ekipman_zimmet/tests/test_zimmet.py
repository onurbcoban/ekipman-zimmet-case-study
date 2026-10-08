from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools import format_date, mute_logger
from odoo.exceptions import AccessError, ValidationError, UserError
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.tools.safe_eval import safe_eval

from psycopg2 import errors

class TestZimmet(TransactionCase):

    def setUp(self):
        super(TestZimmet, self).setUp()
        
        self.kategori = self.env['ekipman.kategori'].create({
            'name': 'Test Kategori',
        })
        
        self.cihaz = self.env['ekipman.cihaz'].create({
            'name': 'Test Cihaz',
            'kategori_id': self.kategori.id,
            'seri_no': 'TEST-001',
            'etiket_no': 'ETK-001',
        })
        
        # self.env süper kullanıcıdır (env.su) ve write/create korumalarını atlar;
        # yetki gerektiren adımlar bu kullanıcıyla yapılır.
        self.group_yetkili = self.env.ref('ekipman_zimmet.group_zimmet_yetkili')
        self.user_yetkili = self.env['res.users'].create({
            'name': 'Test Yetkili',
            'login': 'testyetkili',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.group_yetkili.id])],
        })
        self.employee1 = self.env['hr.employee'].create({
            'name': 'Test Çalışan 1',
            'user_id': self.user_yetkili.id,
        })

        self.group_muhendis = self.env.ref('ekipman_zimmet.group_zimmet_muhendis')
        self.user2 = self.env['res.users'].create({
            'name': 'Test User 2',
            'login': 'testuser2',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.group_muhendis.id])],
        })
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Test Çalışan 2',
            'user_id': self.user2.id,
        })

        # Kod "bugün"ü kullanıcının saat dilimine göre alır; date.today() sunucu saatine
        # göredir ve gece yarısına yakın bir gün farklı çıkabilir.
        self.bugun = fields.Date.context_today(self.cihaz.with_user(self.user_yetkili))

    def _talep(self, user, baslangic, bitis):
        """Kullanıcı adına taslak talep oluşturur; baslangic ve bitis bugünden gün farkıdır."""
        return self.env['ekipman.zimmet'].with_user(user).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': self.bugun + timedelta(days=baslangic),
            'planlanan_bitis': self.bugun + timedelta(days=bitis),
        })

    def test_01_tarih_cakismasi(self):
        zimmet1 = self.env['ekipman.zimmet'].with_user(self.user_yetkili).create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
        })
        zimmet1.action_gonder()
        zimmet1.action_onayla()
        self.assertEqual(zimmet1.state, 'onaylandi')

        zimmet2 = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today() + timedelta(days=5),
            'planlanan_bitis': date.today() + timedelta(days=15),
        })
        zimmet2.action_gonder()
        
        with self.assertRaises(ValidationError):
            zimmet2.with_user(self.user_yetkili).action_onayla()

    def test_02_red_gerekcesi(self):
        zimmet = self.env['ekipman.zimmet'].with_user(self.user_yetkili).create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
        })
        zimmet.action_gonder()
        self.assertEqual(zimmet.state, 'talep_edildi')

        zimmet.red_gerekcesi = False
        with self.assertRaises(UserError):
            zimmet.action_reddet()

    def test_03_unlink_kisiti(self):
        zimmet = self.env['ekipman.zimmet'].with_user(self.user_yetkili).create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
        })
        zimmet.action_gonder()
        zimmet.action_onayla()
        self.assertEqual(zimmet.state, 'onaylandi')

        with self.assertRaises(UserError):
            zimmet.unlink()

    def test_04_muhendis_taslak_unlink(self):
        zimmet = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        self.assertEqual(zimmet.state, 'taslak')
        self.assertEqual(zimmet.calisan_id, self.employee2)
        zimmet_id = zimmet.id
        zimmet.unlink()
        self.assertFalse(self.env['ekipman.zimmet'].browse(zimmet_id).exists())

    def test_05_dolu_tarihler_related(self):
        zimmet = self.env['ekipman.zimmet'].with_user(self.user_yetkili).create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        zimmet.action_gonder()
        zimmet.action_onayla()
        self.assertEqual(zimmet.state, 'onaylandi')
        self.assertTrue(self.cihaz.dolu_tarihler)
        self.assertEqual(zimmet.dolu_tarihler, self.cihaz.dolu_tarihler)

    def test_06_baskasi_adina_talep_acma_engeli(self):
        with self.assertRaises(UserError):
            self.env['ekipman.zimmet'].with_user(self.user2).create({
                'cihaz_id': self.cihaz.id,
                'calisan_id': self.employee1.id,
                'planlanan_baslangic': date.today(),
                'planlanan_bitis': date.today() + timedelta(days=5),
            })

    def test_07_calisan_profili_olmayan_kullanici(self):
        user_no_emp = self.env['res.users'].create({
            'name': 'No Employee User',
            'login': 'no_emp_user',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.group_muhendis.id])],
        })
        with self.assertRaises(UserError):
            self.env['ekipman.zimmet'].with_user(user_no_emp).create({
                'cihaz_id': self.cihaz.id,
                'planlanan_baslangic': date.today(),
                'planlanan_bitis': date.today() + timedelta(days=5),
            })

    def test_08_calisan_id_degistirilemez(self):
        zimmet = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        with self.assertRaises(UserError):
            zimmet.write({'calisan_id': self.employee1.id})

    def test_09_red_gerekcesi_yetki_kontrolu(self):
        zimmet = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        zimmet.action_gonder()  # red gerekçesi yalnızca bekleyen talepte anlamlıdır (F2)
        with self.assertRaises(UserError):
            zimmet.with_user(self.user2).write({'red_gerekcesi': 'Yetkisiz red'})

        zimmet.with_user(self.user_yetkili).write({'red_gerekcesi': 'Yetkili red gerekçesi'})
        self.assertEqual(zimmet.red_gerekcesi, 'Yetkili red gerekçesi')

    def test_10_gecmis_zimmet_ve_dolu_tarihler_overdue(self):
        today = date.today()
        zimmet = self.env['ekipman.zimmet'].with_user(self.user_yetkili).create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': today - timedelta(days=10),
            'planlanan_bitis': today - timedelta(days=2),
        })
        self.assertNotIn(zimmet, self.cihaz.gecmis_zimmet_ids)

        zimmet.sudo().write({'state': 'teslim_edildi'})
        self.assertIn(zimmet, self.cihaz.gecmis_zimmet_ids)

        self.cihaz._compute_dolu_tarihler()
        self.assertIn("Şu an elde, iade bekleniyor", self.cihaz.dolu_tarihler)

        zimmet.sudo().write({'state': 'iade_edildi'})
        zimmet_onay = self.env['ekipman.zimmet'].with_user(self.user_yetkili).create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': today - timedelta(days=10),
            'planlanan_bitis': today - timedelta(days=2),
        })
        zimmet_onay.sudo().write({'state': 'onaylandi'})
        self.cihaz._compute_dolu_tarihler()
        self.assertFalse(self.cihaz.dolu_tarihler)

    def test_11_sinir_gunu(self):
        a = self._talep(self.user_yetkili, 0, 10)
        a.action_gonder()
        a.action_onayla()

        # Tarihler kapalı aralıktır: a'nın bitiş günü b'nin başlangıç günüyle çakışır
        b = self._talep(self.user2, 10, 15)
        b.action_gonder()
        with self.assertRaises(ValidationError):
            b.with_user(self.user_yetkili).action_onayla()

    def test_12_erken_iade(self):
        a = self._talep(self.user_yetkili, 0, 10)
        a.action_gonder()
        a.action_onayla()
        a.action_teslim_et()
        a.action_iade_al()
        self.assertEqual(a.state, 'iade_edildi')
        self.assertEqual(a.fiili_bitis, self.bugun)

        b = self._talep(self.user2, 3, 8)
        b.action_gonder()
        b.with_user(self.user_yetkili).action_onayla()
        self.assertEqual(b.state, 'onaylandi')

    def test_13_gecikmis_cihaz_teslim(self):
        # Geçen hafta teslim edilmiş, dün iade edilmesi gereken kayıt. Teslim yalnızca
        # planlanan aralıkta yapılabildiği için bu durum butonlarla kurulamaz.
        a = self._talep(self.user2, -7, -1)
        a.sudo().write({'state': 'teslim_edildi', 'fiili_baslangic': self.bugun - timedelta(days=7)})

        b = self._talep(self.user_yetkili, 0, 3)
        b.action_gonder()
        b.action_onayla()
        self.assertEqual(b.state, 'onaylandi')

        with self.assertRaises(ValidationError):
            b.action_teslim_et()

    def test_14_state_dogrudan_yazilamaz(self):
        zimmet = self._talep(self.user2, 0, 5)
        with self.assertRaises(UserError):
            zimmet.write({'state': 'onaylandi'})
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).write({'state': 'onaylandi'})
        self.assertEqual(zimmet.state, 'taslak')

    def test_15_geri_cekme_yetkisi(self):
        zimmet = self._talep(self.user2, 0, 5)
        zimmet.action_gonder()
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).action_geri_cek()

        zimmet.action_geri_cek()
        self.assertEqual(zimmet.state, 'taslak')

    def test_16_gecmis_tarihli_talep_gonderilemez(self):
        gecmis = self._talep(self.user2, -1, 3)
        with self.assertRaises(UserError):
            gecmis.action_gonder()
        self.assertEqual(gecmis.state, 'taslak')

        bugun_baslayan = self._talep(self.user2, 0, 3)
        bugun_baslayan.action_gonder()
        self.assertEqual(bugun_baslayan.state, 'talep_edildi')

    def test_17_create_korumalari(self):
        Zimmet = self.env['ekipman.zimmet'].with_user(self.user2)
        vals = {
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': self.bugun,
            'planlanan_bitis': self.bugun + timedelta(days=3),
        }
        with self.assertRaises(UserError):
            Zimmet.create(dict(vals, state='onaylandi'))
        with self.assertRaises(UserError):
            Zimmet.create(dict(vals, fiili_baslangic=self.bugun))

        # Web istemcisi yeni kayıtta durum çubuğundaki state='taslak' değerini de gönderir;
        # koruma bu normal yolu engellememeli.
        with Form(Zimmet) as form:
            form.cihaz_id = self.cihaz
            form.planlanan_baslangic = self.bugun
            form.planlanan_bitis = self.bugun + timedelta(days=3)
        zimmet = form.record
        self.assertEqual(zimmet.state, 'taslak')
        self.assertEqual(zimmet.calisan_id, self.employee2)

    def test_18_red_gerekcesi_yalnizca_bekleyen_talepte(self):
        zimmet = self._talep(self.user2, 0, 3)
        zimmet.action_gonder()
        zimmet.with_user(self.user_yetkili).action_onayla()
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).write({'red_gerekcesi': 'Sonradan eklenen gerekçe'})

    def test_19_talep_sahibi_mi(self):
        zimmet = self._talep(self.user2, 0, 3)
        self.assertTrue(zimmet.talep_sahibi_mi)
        self.assertFalse(zimmet.with_user(self.user_yetkili).talep_sahibi_mi)

    def test_20_chatter_onaylayani_gosterir(self):
        zimmet = self._talep(self.user2, 0, 3)
        zimmet.action_gonder()
        # Durum izleme mesajları işlem kaydedilmeden önce (precommit) oluşturulur.
        self.env.cr.precommit.run()
        zimmet.with_user(self.user_yetkili).action_onayla()
        self.env.cr.precommit.run()

        onay_mesaji = zimmet.sudo().message_ids.filtered(
            lambda m: m.tracking_value_ids.filtered(lambda t: t.field_id.name == 'state'
                                                    and t.new_value_char == 'Onaylandı')
        )
        self.assertEqual(len(onay_mesaji), 1)
        self.assertEqual(onay_mesaji.author_id, self.user_yetkili.partner_id)

    def test_21_taslak_iptal_edilemez(self):
        zimmet = self._talep(self.user2, 0, 3)
        with self.assertRaises(UserError):
            zimmet.action_iptal()
        self.assertEqual(zimmet.state, 'taslak')

    def test_22_taslagi_yalnizca_sahibi_siler(self):
        zimmet = self._talep(self.user2, 0, 3)
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).action_taslagi_sil()
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).unlink()

        zimmet_id = zimmet.id
        action = zimmet.action_taslagi_sil()
        self.assertFalse(self.env['ekipman.zimmet'].browse(zimmet_id).exists())
        self.assertEqual(action['res_model'], 'ekipman.zimmet')

    def test_23_bitisi_gecmis_talep_onaylanamaz(self):
        # Onay beklerken tarihi geçmiş talepler; gönderme geçmiş başlangıcı reddettiği için
        # bu durum zamanın geçmesiyle oluşur ve testte sudo ile kurulur.
        bitisi_gecmis = self._talep(self.user2, -5, -1)
        bitisi_gecmis.sudo().write({'state': 'talep_edildi'})
        with self.assertRaises(UserError):
            bitisi_gecmis.with_user(self.user_yetkili).action_onayla()

        baslangici_gecmis = self._talep(self.user2, -2, 3)
        baslangici_gecmis.sudo().write({'state': 'talep_edildi'})
        baslangici_gecmis.with_user(self.user_yetkili).action_onayla()
        self.assertEqual(baslangici_gecmis.state, 'onaylandi')

    def test_24_kopya_kopyalayanin_adina_taslaktir(self):
        kayit = self._talep(self.user2, 0, 3)
        kayit.sudo().write({'state': 'iade_edildi', 'fiili_baslangic': self.bugun, 'fiili_bitis': self.bugun})

        kopya = kayit.with_user(self.user_yetkili).copy()
        self.assertEqual(kopya.state, 'taslak')
        self.assertEqual(kopya.calisan_id, self.employee1)
        self.assertEqual(kopya.cihaz_id, kayit.cihaz_id)
        self.assertEqual(kopya.planlanan_baslangic, kayit.planlanan_baslangic)
        self.assertNotEqual(kopya.name, kayit.name)
        self.assertFalse(kopya.fiili_baslangic)

    def test_25_cakisma_mesaji(self):
        a = self._talep(self.user_yetkili, 1, 5)
        a.action_gonder()
        a.action_onayla()

        b = self._talep(self.user2, 3, 8)
        b.action_gonder()
        with self.assertRaises(ValidationError) as hata:
            b.with_user(self.user_yetkili).action_onayla()
        mesaj = str(hata.exception)
        self.assertIn(a.name, mesaj)
        self.assertIn(format_date(self.user_yetkili.env, a.planlanan_baslangic), mesaj)
        self.assertIn(format_date(self.user_yetkili.env, a.planlanan_bitis), mesaj)

    def test_26_fiziksel_durum(self):
        self.assertEqual(self.cihaz.fiziksel_durum, 'bosta')
        zimmet = self._talep(self.user_yetkili, 0, 3)
        zimmet.action_gonder()
        zimmet.action_onayla()
        zimmet.action_teslim_et()
        self.assertEqual(self.cihaz.fiziksel_durum, 'zimmette')
        zimmet.action_iade_al()
        self.assertEqual(self.cihaz.fiziksel_durum, 'bosta')

    def test_27_dolu_tarihler_kullanici_dil_bicimiyle(self):
        zimmet = self._talep(self.user_yetkili, 1, 5)
        zimmet.action_gonder()
        zimmet.action_onayla()
        dolu = self.cihaz.with_user(self.user2).dolu_tarihler
        self.assertIn(format_date(self.user2.env, zimmet.planlanan_baslangic), dolu)
        self.assertIn(format_date(self.user2.env, zimmet.planlanan_bitis), dolu)

    def _sql_ile_durum(self, kayit, durum):
        self.env.cr.execute("UPDATE ekipman_zimmet SET state = %s WHERE id = %s", (durum, kayit.id))

    def test_28_veritabani_cakisma_kisiti(self):
        # Eşzamanlı onay yarışının sonucu: iki Python kontrolü de geçmiş, iki yazma veritabanına ulaşmış.
        a = self._talep(self.user2, 0, 5)
        b = self._talep(self.user_yetkili, 3, 8)
        self.env.flush_all()
        self._sql_ile_durum(a, 'onaylandi')
        self._sql_ile_durum(b, 'onaylandi')
        with self.assertRaises(errors.ExclusionViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            b._kisitlari_simdi_denetle()

    def test_29_veritabani_tek_teslim_kisiti(self):
        # Tarihleri çakışmayan iki kayıt: tarih kısıtı geçer, aynı cihazın iki kez teslimini tek-teslim kısıtı durdurur.
        a = self._talep(self.user2, 0, 3)
        b = self._talep(self.user_yetkili, 10, 13)
        self.env.flush_all()
        self._sql_ile_durum(a, 'teslim_edildi')
        self._sql_ile_durum(b, 'teslim_edildi')
        with self.assertRaises(errors.ExclusionViolation), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            b._kisitlari_simdi_denetle()

    def test_30_kisitlar_eklentisiz_kurulu(self):
        self.env.cr.execute("SELECT 1 FROM pg_extension WHERE extname = 'btree_gist'")
        self.assertFalse(self.env.cr.fetchall())
        self.env.cr.execute(
            "SELECT conname FROM pg_constraint WHERE conrelid = 'ekipman_zimmet'::regclass AND contype = 'x'"
        )
        self.assertEqual(
            {satir[0] for satir in self.env.cr.fetchall()},
            {'ekipman_zimmet_cakisma_engeli', 'ekipman_zimmet_tek_teslim'},
        )

    def test_31_iptal_nedeni_zorunlu(self):
        zimmet = self._talep(self.user2, 0, 3)
        with self.assertRaises(UserError):
            zimmet.write({'iptal_nedeni': 'Taslakta yazılamaz'})
        zimmet.action_gonder()
        zimmet.with_user(self.user_yetkili).action_onayla()

        with self.assertRaises(UserError):
            zimmet.action_iptal()
        self.assertEqual(zimmet.state, 'onaylandi')

        zimmet.write({'iptal_nedeni': 'Artık ihtiyacım kalmadı.'})
        zimmet.action_iptal()
        self.assertEqual(zimmet.state, 'iptal')
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).write({'iptal_nedeni': 'Sonradan değiştirildi.'})

    def test_32_kapanis_tarihi(self):
        reddedilen = self._talep(self.user2, 0, 3)
        reddedilen.action_gonder()
        reddedilen.with_user(self.user_yetkili).write({'red_gerekcesi': 'Uygun değil.'})
        reddedilen.with_user(self.user_yetkili).action_reddet()
        self.assertEqual(reddedilen.kapanis_tarihi, self.bugun)

        iade_edilen = self._talep(self.user_yetkili, 0, 3)
        iade_edilen.action_gonder()
        iade_edilen.action_onayla()
        iade_edilen.action_teslim_et()
        self.assertFalse(iade_edilen.kapanis_tarihi)
        iade_edilen.action_iade_al()
        self.assertEqual(iade_edilen.kapanis_tarihi, self.bugun)

        iptal_edilen = self._talep(self.user2, 5, 8)
        iptal_edilen.action_gonder()
        iptal_edilen.write({'iptal_nedeni': 'Vazgeçtim.'})
        iptal_edilen.action_iptal()
        self.assertEqual(iptal_edilen.kapanis_tarihi, self.bugun)

        with self.assertRaises(UserError):
            iptal_edilen.with_user(self.user_yetkili).write({'kapanis_tarihi': self.bugun - timedelta(days=30)})
        with self.assertRaises(UserError):
            self.env['ekipman.zimmet'].with_user(self.user2).create({
                'cihaz_id': self.cihaz.id,
                'planlanan_baslangic': self.bugun,
                'planlanan_bitis': self.bugun,
                'kapanis_tarihi': self.bugun,
            })

    def _arama_filtresi(self, ad):
        """Arama görünümündeki filtrenin domain'ini web istemcisinin yaptığı gibi bugüne göre hesaplar."""
        arch = self.env.ref('ekipman_zimmet.view_ekipman_zimmet_search').arch
        filtre = etree.fromstring(arch).xpath(f"//filter[@name='{ad}']")[0]
        return safe_eval(filtre.get('domain'), {
            'context_today': lambda: self.bugun,
            'relativedelta': relativedelta,
        })

    def test_33_guncel_ve_acik_talepler(self):
        acik = self._talep(self.user2, 0, 3)
        # Kapanmış kayıtlar zamanla oluşur; testte durum ve kapanış tarihi sudo ile kurulur.
        yeni_red = self._talep(self.user2, 5, 8)
        yeni_red.sudo().write({'state': 'reddedildi', 'kapanis_tarihi': self.bugun})
        eski_iade = self._talep(self.user2, -20, -15)
        eski_iade.sudo().write({'state': 'iade_edildi', 'kapanis_tarihi': self.bugun - timedelta(days=10)})
        kayitlar = [('id', 'in', (acik | yeni_red | eski_iade).ids)]

        Zimmet = self.env['ekipman.zimmet']
        self.assertEqual(Zimmet.search(self._arama_filtresi('guncel_talepler') + kayitlar), acik | yeni_red)
        self.assertEqual(Zimmet.search(self._arama_filtresi('acik_talepler') + kayitlar), acik)
        varsayilan = self.env.ref('ekipman_zimmet.action_ekipman_zimmet').context
        self.assertIn('search_default_guncel_talepler', varsayilan)

    def test_34_uzatma_istegi(self):
        zimmet = self._talep(self.user2, 0, 3)
        with self.assertRaises(UserError):
            zimmet.write({'istenen_bitis': self.bugun + timedelta(days=6)})
        zimmet.action_gonder()
        zimmet.with_user(self.user_yetkili).action_onayla()

        zimmet.write({'istenen_bitis': self.bugun + timedelta(days=6)})
        self.assertEqual(zimmet.istenen_bitis, self.bugun + timedelta(days=6))
        zimmet.action_uzatmayi_geri_cek()
        self.assertFalse(zimmet.istenen_bitis)

        with self.assertRaises(UserError):
            zimmet.write({'istenen_bitis': zimmet.planlanan_bitis})
        with self.assertRaises(UserError):
            zimmet.with_user(self.user_yetkili).write({'istenen_bitis': self.bugun + timedelta(days=6)})

        # Gecikmiş kayıt: bitiş geçmişte; yeni bitiş mevcut bitişten sonra olsa da bugünden önce olamaz.
        gecikmis = self._talep(self.user2, -7, -3)
        gecikmis.sudo().write({'state': 'teslim_edildi', 'fiili_baslangic': self.bugun - timedelta(days=7)})
        with self.assertRaises(UserError):
            gecikmis.write({'istenen_bitis': self.bugun - timedelta(days=1)})
        gecikmis.write({'istenen_bitis': self.bugun + timedelta(days=2)})
        self.assertEqual(gecikmis.istenen_bitis, self.bugun + timedelta(days=2))

        with self.assertRaises(UserError):
            self.env['ekipman.zimmet'].with_user(self.user2).create({
                'cihaz_id': self.cihaz.id,
                'planlanan_baslangic': self.bugun,
                'planlanan_bitis': self.bugun,
                'istenen_bitis': self.bugun + timedelta(days=3),
            })

    def _onayli_talep(self, user, baslangic, bitis):
        zimmet = self._talep(user, baslangic, bitis)
        zimmet.action_gonder()
        zimmet.with_user(self.user_yetkili).action_onayla()
        return zimmet

    def test_35_uzatma_onay_ve_red(self):
        zimmet = self._onayli_talep(self.user2, 0, 3)
        zimmet.write({'istenen_bitis': self.bugun + timedelta(days=5)})
        with self.assertRaises(AccessError):
            zimmet.action_uzatmayi_onayla()
        zimmet.with_user(self.user_yetkili).action_uzatmayi_onayla()
        self.assertEqual(zimmet.planlanan_bitis, self.bugun + timedelta(days=5))
        self.assertFalse(zimmet.istenen_bitis)

        self._onayli_talep(self.user_yetkili, 8, 12)
        zimmet.write({'istenen_bitis': self.bugun + timedelta(days=9)})
        with self.assertRaises(ValidationError):
            zimmet.with_user(self.user_yetkili).action_uzatmayi_onayla()
        self.assertEqual(zimmet.planlanan_bitis, self.bugun + timedelta(days=5))

        zimmet.with_user(self.user_yetkili).action_uzatmayi_reddet()
        self.assertFalse(zimmet.istenen_bitis)
        self.assertEqual(zimmet.planlanan_bitis, self.bugun + timedelta(days=5))

    def test_36_gecikmis_kayit_uzatilinca_gecikenlerden_cikar(self):
        # Gecikmiş kayıt zamanla oluşur; testte sudo ile kurulur.
        gecikmis = self._talep(self.user2, -7, -2)
        gecikmis.sudo().write({'state': 'teslim_edildi', 'fiili_baslangic': self.bugun - timedelta(days=7)})
        gecikenler = self._arama_filtresi('gecikenler') + [('id', '=', gecikmis.id)]
        self.assertTrue(self.env['ekipman.zimmet'].search(gecikenler))

        gecikmis.write({'istenen_bitis': self.bugun + timedelta(days=3)})
        gecikmis.with_user(self.user_yetkili).action_uzatmayi_onayla()
        self.assertFalse(self.env['ekipman.zimmet'].search(gecikenler))

        gecikmis.write({'istenen_bitis': self.bugun + timedelta(days=6)})
        gecikmis.with_user(self.user_yetkili).action_iade_al()
        self.assertFalse(gecikmis.istenen_bitis)
