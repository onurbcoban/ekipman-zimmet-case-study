from odoo import models, fields, api


class EkipmanZimmet(models.Model):
    _name = 'ekipman.zimmet'
    _description = 'Ekipman Zimmeti'
    _inherit = ['mail.thread']
    _order = 'planlanan_baslangic desc, id desc'

    name = fields.Char(
        string='Referans',
        required=True,
        copy=False,
        readonly=True,
        default='Yeni',
    )
    state = fields.Selection(
        selection=[
            ('taslak', 'Taslak'),
            ('talep_edildi', 'Talep Edildi'),
            ('onaylandi', 'Onaylandı'),
            ('teslim_edildi', 'Teslim Edildi'),
            ('iade_edildi', 'İade Edildi'),
            ('reddedildi', 'Reddedildi'),
            ('iptal', 'İptal'),
        ],
        string='Durum',
        default='taslak',
        required=True,
        tracking=True,
        copy=False,
    )
    cihaz_id = fields.Many2one(
        'ekipman.cihaz',
        string='Cihaz',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    calisan_id = fields.Many2one(
        'hr.employee',
        string='Çalışan',
        required=True,
        ondelete='restrict',
        tracking=True,
        default=lambda self: self._default_calisan_id(),
    )
    planlanan_baslangic = fields.Date(
        string='Planlanan Başlangıç',
        required=True,
        tracking=True,
    )
    planlanan_bitis = fields.Date(
        string='Planlanan Bitiş',
        required=True,
        tracking=True,
    )
    fiili_baslangic = fields.Date(
        string='Fiili Başlangıç',
        readonly=True,
        copy=False,
        tracking=True,
    )
    fiili_bitis = fields.Date(
        string='Fiili Bitiş',
        readonly=True,
        copy=False,
        tracking=True,
    )
    red_gerekcesi = fields.Text(
        string='Red Gerekçesi',
        copy=False,
        tracking=True,
    )

    @api.model
    def _default_calisan_id(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee.id if employee else False

    def action_talep_et(self):
        for rec in self:
            rec.state = 'talep_edildi'

    def action_geri_cek(self):
        for rec in self:
            rec.state = 'taslak'

    def action_onayla(self):
        for rec in self:
            rec.state = 'onaylandi'

    def action_reddet(self):
        for rec in self:
            rec.state = 'reddedildi'

    def action_teslim_et(self):
        for rec in self:
            rec.state = 'teslim_edildi'
            if not rec.fiili_baslangic:
                rec.fiili_baslangic = fields.Date.context_today(self)

    def action_iade_al(self):
        for rec in self:
            rec.state = 'iade_edildi'
            if not rec.fiili_bitis:
                rec.fiili_bitis = fields.Date.context_today(self)

    def action_iptal(self):
        for rec in self:
            rec.state = 'iptal'
