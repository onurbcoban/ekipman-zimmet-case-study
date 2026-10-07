from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta

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

