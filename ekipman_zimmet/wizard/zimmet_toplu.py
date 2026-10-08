from odoo import models, fields
from odoo.exceptions import UserError


class EkipmanZimmetToplu(models.TransientModel):
    _name = 'ekipman.zimmet.toplu'
    _description = 'Toplu Zimmet Talebi'

    cihaz_ids = fields.Many2many(
        'ekipman.cihaz',
        string='Cihazlar',
        domain=[('kullanilabilirlik', '=', 'kullanilabilir')],
    )
    planlanan_baslangic = fields.Date(string='Planlanan Başlangıç', required=True)
    planlanan_bitis = fields.Date(string='Planlanan Bitiş', required=True)

    def action_talep_et(self):
        self.ensure_one()
        if not self.cihaz_ids:
            raise UserError('En az bir cihaz seçilmelidir.')
        # Kayıtlar kullanıcının kendi yetkisiyle açılıp gönderilir; tek tek talepteki bütün
        # kurallar aynen uygulanır. Bir kayıt hata verirse işlem bütünüyle geri alınır (A6).
        kayitlar = self.env['ekipman.zimmet'].create([{
            'cihaz_id': cihaz.id,
            'planlanan_baslangic': self.planlanan_baslangic,
            'planlanan_bitis': self.planlanan_bitis,
        } for cihaz in self.cihaz_ids])
        kayitlar.sudo().write({'toplu_ref': self.env['ir.sequence'].next_by_code('ekipman.zimmet.toplu')})
        kayitlar.action_gonder()
        eylem = self.env['ir.actions.act_window']._for_xml_id('ekipman_zimmet.action_ekipman_zimmet')
        eylem['domain'] = [('id', 'in', kayitlar.ids)]
        eylem['context'] = {}
        return eylem
