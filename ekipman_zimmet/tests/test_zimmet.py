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
        })
        
        self.employee2 = self.env['hr.employee'].create({
            'name': 'Test Çalışan 2',
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
        zimmet1.action_talep_et()
        zimmet1.action_onayla()
        self.assertEqual(zimmet1.state, 'onaylandi')

        # Aynı cihaz için tarihleri kesişen (çakışan) ikinci bir kayıt aç
        zimmet2 = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee2.id,
            'planlanan_baslangic': date.today() + timedelta(days=5),
            'planlanan_bitis': date.today() + timedelta(days=15),
            'state': 'taslak'
        })
        zimmet2.action_talep_et()
        
        # Onaylamaya çalış, ValidationError fırlatıldığını doğrula
        with self.assertRaises(ValidationError):
            zimmet2.action_onayla()

    def test_02_red_gerekcesi(self):
        # Durumu talep_edildi olan bir kayıt oluştur.
        zimmet = self.env['ekipman.zimmet'].create({
            'cihaz_id': self.cihaz.id,
            'calisan_id': self.employee1.id,
            'planlanan_baslangic': date.today(),
            'planlanan_bitis': date.today() + timedelta(days=10),
            'state': 'taslak'
        })
        zimmet.action_talep_et()
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
        zimmet.action_talep_et()
        zimmet.action_onayla()
        self.assertEqual(zimmet.state, 'onaylandi')

        # unlink() metodu ile silmeye çalış, UserError fırlatıldığını doğrula.
        with self.assertRaises(UserError):
            zimmet.unlink()
