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
        
        self.employee1 = self.env['hr.employee'].create({
            'name': 'Test Çalışan 1',
            'user_id': self.env.user.id,
        })
        
        # Test Çalışan 2 requires a separate user to test permission failures if needed, 
        # or we just let it fail. Let's create a separate user for it.
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

    def test_01_tarih_cakismasi(self):
        # Bir zimmet kaydını oluşturup onaylandi yap
        zimmet1 = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
            'state': 'taslak'
        })
        zimmet1.action_gonder()
        zimmet1.action_onayla()
        self.assertEqual(zimmet1.state, 'onaylandi')

        # Aynı cihaz için tarihleri kesişen (çakışan) ikinci bir kayıt aç (user2 adına)
        zimmet2 = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today() + timedelta(days=5),
            'planlanan_bitis': date.today() + timedelta(days=15),
            'state': 'taslak'
        })
        zimmet2.action_gonder()
        
        # Onaylamaya çalış (yetkili admin onaylayabilir), ValidationError fırlatıldığını doğrula
        with self.assertRaises(ValidationError):
            zimmet2.with_user(self.env.user).action_onayla()

    def test_02_red_gerekcesi(self):
        # Durumu talep_edildi olan bir kayıt oluştur.
        zimmet = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
            'state': 'taslak'
        })
        zimmet.action_gonder()
        self.assertEqual(zimmet.state, 'talep_edildi')

        # red_gerekcesi boşken action_reddet() metodunu çağır, UserError fırlatıldığını doğrula.
        zimmet.red_gerekcesi = False
        with self.assertRaises(UserError):
            zimmet.action_reddet()

    def test_03_unlink_kisiti(self):
        # Durumu onaylandi olan bir kaydı oluştur
        zimmet = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
            'state': 'taslak'
        })
        zimmet.action_gonder()
        zimmet.action_onayla()
        self.assertEqual(zimmet.state, 'onaylandi')

        # unlink() metodu ile silmeye çalış, UserError fırlatıldığını doğrula.
        with self.assertRaises(UserError):
            zimmet.unlink()

    def test_04_muhendis_taslak_unlink(self):
        # Mühendis kullanıcısı kendi taslak talebini oluşturur ve silebilir
        zimmet = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        self.assertEqual(zimmet.state, 'taslak')
        self.assertEqual(zimmet.calisan_id, self.employee2)
        # Kendi taslak kaydını başarıyla silebilir
        zimmet_id = zimmet.id
        zimmet.unlink()
        self.assertFalse(self.env['ekipman.zimmet'].browse(zimmet_id).exists())

    def test_05_dolu_tarihler_related(self):
        # Cihazın onaylanmış veya teslim edilmiş zimmeti varsa dolu_tarihler zimmet modelinde de görünür
        zimmet = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
            'state': 'taslak',
        })
        zimmet.action_gonder()
        zimmet.action_onayla()
        self.assertEqual(zimmet.state, 'onaylandi')
        self.assertTrue(self.cihaz.dolu_tarihler)
        self.assertEqual(zimmet.dolu_tarihler, self.cihaz.dolu_tarihler)

    def test_06_baskasi_adina_talep_acma_engeli(self):
        # Mühendis kullanıcısı başkası adına talep açamaz
        with self.assertRaises(UserError):
            self.env['ekipman.zimmet'].with_user(self.user2).create({
                'cihaz_id': self.cihaz.id,
                'calisan_id': self.employee1.id,
                'planlanan_baslangic': date.today(),
                'planlanan_bitis': date.today() + timedelta(days=5),
            })

    def test_07_calisan_profili_olmayan_kullanici(self):
        # Çalışan profili olmayan kullanıcı talep açamaz
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
        # calisan_id alanı write ile değiştirilemez
        zimmet = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        with self.assertRaises(UserError):
            zimmet.write({'calisan_id': self.employee1.id})

    def test_09_red_gerekcesi_yetki_kontrolu(self):
        # Mühendis red gerekçesi yazamaz
        zimmet = self.env['ekipman.zimmet'].with_user(self.user2).create({
            'cihaz_id': self.cihaz.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=5),
        })
        with self.assertRaises(UserError):
            zimmet.with_user(self.user2).write({'red_gerekcesi': 'Yetkisiz red'})

        # Yetkili kullanıcı red gerekçesi yazabilir
        zimmet.with_user(self.env.user).write({'red_gerekcesi': 'Yetkili red gerekçesi'})
        self.assertEqual(zimmet.red_gerekcesi, 'Yetkili red gerekçesi')

    def test_10_gecmis_zimmet_ve_dolu_tarihler_overdue(self):
        today = date.today()
        # Taslak ve talep_edildi gecmis_zimmet_ids'de görünmemeli
        zimmet = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': today - timedelta(days=10),
            'planlanan_bitis': today - timedelta(days=2),
            'state': 'taslak',
        })
        self.assertNotIn(zimmet, self.cihaz.gecmis_zimmet_ids)

        # teslim_edildi durumuna geçtiğinde gecmis_zimmet_ids'de görünmeli
        zimmet.sudo().write({'state': 'teslim_edildi'})
        self.assertIn(zimmet, self.cihaz.gecmis_zimmet_ids)

        # Süresi geçmiş teslim_edildi için dolu_tarihler "Şu an elde, iade bekleniyor" içermeli
        self.cihaz._compute_dolu_tarihler()
        self.assertIn("Şu an elde, iade bekleniyor", self.cihaz.dolu_tarihler)

        # Süresi geçmiş onaylandi kaydı dolu_tarihler'de görünmemeli
        zimmet.sudo().write({'state': 'iade_edildi'})
        zimmet_onay = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': today - timedelta(days=10),
            'planlanan_bitis': today - timedelta(days=2),
            'state': 'taslak',
        })
        zimmet_onay.sudo().write({'state': 'onaylandi'})
        self.cihaz._compute_dolu_tarihler()
        self.assertFalse(self.cihaz.dolu_tarihler)

