from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, AccessError


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
        return self.env.user.employee_id.id or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Yeni') == 'Yeni':
                vals['name'] = self.env['ir.sequence'].next_by_code('ekipman.zimmet') or 'Yeni'
            if not self.env.su:
                if not self.env.user.has_group('ekipman_zimmet.group_yetkili'):
                    vals['calisan_id'] = self.env.user.employee_id.id
                vals['state'] = 'taslak'
        return super().create(vals_list)

    @api.constrains('planlanan_baslangic', 'planlanan_bitis')
    def _check_tarihler(self):
        for rec in self:
            if rec.planlanan_baslangic and rec.planlanan_bitis and rec.planlanan_bitis < rec.planlanan_baslangic:
                raise ValidationError("Bitiş tarihi, başlangıç tarihinden önce olamaz.")

    @api.constrains('cihaz_id', 'planlanan_baslangic', 'planlanan_bitis', 'state')
    def _check_tarih_cakismasi(self):
        for rec in self:
            if rec.state in ['onaylandi', 'teslim_edildi'] and rec.cihaz_id and rec.planlanan_baslangic and rec.planlanan_bitis:
                domain = [
                    ('cihaz_id', '=', rec.cihaz_id.id),
                    ('state', 'in', ['onaylandi', 'teslim_edildi']),
                    ('id', '!=', rec.id),
                    ('planlanan_baslangic', '<=', rec.planlanan_bitis),
                    ('planlanan_bitis', '>=', rec.planlanan_baslangic),
                ]
                cakisan_kayitlar = self.sudo().search(domain)
                if cakisan_kayitlar:
                    if self.env.user.has_group('ekipman_zimmet.group_yetkili'):
                        raise ValidationError(f"{cakisan_kayitlar[0].name} referanslı kayıtla {cakisan_kayitlar[0].planlanan_baslangic} / {cakisan_kayitlar[0].planlanan_bitis} tarihleri arasında çakışıyor.")
                    else:
                        raise ValidationError(f"Seçilen tarihlerde ({rec.planlanan_baslangic} / {rec.planlanan_bitis}) bu cihaz doludur.")

    @api.constrains('cihaz_id', 'state')
    def _check_fiziksel_teslim(self):
        for rec in self:
            if rec.state == 'teslim_edildi' and rec.cihaz_id:
                domain = [
                    ('cihaz_id', '=', rec.cihaz_id.id),
                    ('state', '=', 'teslim_edildi'),
                    ('id', '!=', rec.id),
                ]
                teslim_edilenler = self.search(domain)
                if teslim_edilenler:
                    raise ValidationError("Bu cihaz şu anda başka bir çalışana teslim edilmiş durumdadır. Önce iade alınması gerekir.")

    def action_gonder(self):
        for rec in self:
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar talep edilebilir.')
            if rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taleplerinizi iletebilirsiniz.')
            rec.sudo().write({'state': 'talep_edildi'})

    def action_geri_cek(self):
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar geri çekilebilir.')
            if rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taleplerinizi geri çekebilirsiniz.')
            rec.sudo().write({'state': 'taslak'})

    def action_onayla(self):
        if not self.env.user.has_group('ekipman_zimmet.group_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar onaylanabilir.')
            rec.sudo().write({'state': 'onaylandi'})

    def action_reddet(self):
        if not self.env.user.has_group('ekipman_zimmet.group_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar reddedilebilir.')
            if not rec.red_gerekcesi:
                raise UserError('Reddetmek için red gerekçesi doldurulmalıdır.')
            rec.sudo().write({'state': 'reddedildi'})

    def action_teslim_et(self):
        if not self.env.user.has_group('ekipman_zimmet.group_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'onaylandi':
                raise UserError('Yalnızca onaylanmış kayıtlar teslim edilebilir.')
            
            bugun = fields.Date.context_today(self)
            if not (rec.planlanan_baslangic <= bugun <= rec.planlanan_bitis):
                raise UserError('Teslimat yalnızca planlanan tarih aralığında yapılabilir. Erken veya süresi geçmiş teslimat yapılamaz.')
                
            rec.sudo().write({
                'state': 'teslim_edildi',
                'fiili_baslangic': bugun
            })

    def action_iade_al(self):
        if not self.env.user.has_group('ekipman_zimmet.group_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'teslim_edildi':
                raise UserError('Yalnızca teslim edilmiş kayıtlar iade alınabilir.')
            rec.sudo().write({
                'state': 'iade_edildi',
                'fiili_bitis': fields.Date.context_today(self)
            })

    def action_iptal(self):
        for rec in self:
            if rec.state not in ['taslak', 'talep_edildi', 'onaylandi']:
                raise UserError('Bu durumdaki bir kayıt iptal edilemez.')
            if not self.env.user.has_group('ekipman_zimmet.group_yetkili') and rec.calisan_id.user_id != self.env.user:
                raise UserError('Başkasının talebini iptal edemezsiniz.')
            rec.sudo().write({'state': 'iptal'})

    def write(self, vals):
        if not self.env.su:
            restricted_for_all = {'state', 'fiili_baslangic', 'fiili_bitis'}
            if restricted_for_all.intersection(vals.keys()):
                raise UserError('Durum ve fiili tarihler doğrudan güncellenemez.')
                
        restricted_fields = {'cihaz_id', 'planlanan_baslangic', 'planlanan_bitis', 'calisan_id'}
        if restricted_fields.intersection(vals.keys()):
            for rec in self:
                if rec.state != 'taslak':
                    raise UserError('Taslak durumunda olmayan kayıtların cihaz ve planlanan tarih bilgileri değiştirilemez.')
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar silinebilir.')
        return super().unlink()
