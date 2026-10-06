from odoo import models, fields, api
from odoo.exceptions import UserError


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
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar talep edilebilir.')
            rec.state = 'talep_edildi'

    def action_geri_cek(self):
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar geri çekilebilir.')
            rec.state = 'taslak'

    def action_onayla(self):
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar onaylanabilir.')
            rec.state = 'onaylandi'

    def action_reddet(self):
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar reddedilebilir.')
            if not rec.red_gerekcesi:
                raise UserError('Reddetmek için red gerekçesi doldurulmalıdır.')
            rec.state = 'reddedildi'

    def action_teslim_et(self):
        for rec in self:
            if rec.state != 'onaylandi':
                raise UserError('Yalnızca onaylanmış kayıtlar teslim edilebilir.')
            rec.state = 'teslim_edildi'
            rec.fiili_baslangic = fields.Date.context_today(self)

    def action_iade_al(self):
        for rec in self:
            if rec.state != 'teslim_edildi':
                raise UserError('Yalnızca teslim edilmiş kayıtlar iade alınabilir.')
            rec.state = 'iade_edildi'
            rec.fiili_bitis = fields.Date.context_today(self)

    def action_iptal(self):
        for rec in self:
            if rec.state not in ['taslak', 'talep_edildi', 'onaylandi']:
                raise UserError('Bu durumdaki bir kayıt iptal edilemez.')
            rec.state = 'iptal'

    def write(self, vals):
        restricted_fields = {'cihaz_id', 'planlanan_baslangic', 'planlanan_bitis'}
        if restricted_fields.intersection(vals.keys()):
            for rec in self:
                if rec.state != 'taslak':
                    raise UserError('Taslak durumunda olmayan kayıtların cihaz ve planlanan tarih bilgileri değiştirilemez.')
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state not in ['taslak', 'iptal']:
                raise UserError('Yalnızca taslak veya iptal durumundaki kayıtlar silinebilir.')
        return super().unlink()
