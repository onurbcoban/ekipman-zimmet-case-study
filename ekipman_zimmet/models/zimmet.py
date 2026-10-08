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
    dolu_tarihler = fields.Text(
        related='cihaz_id.dolu_tarihler',
        string='Dolu Tarihler',
    )
    calisan_id = fields.Many2one(
        'hr.employee',
        string='Çalışan',
        required=True,
        ondelete='restrict',
        tracking=True,
        copy=False,
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
    talep_sahibi_mi = fields.Boolean(compute='_compute_talep_sahibi_mi')

    @api.depends('calisan_id.user_id')
    @api.depends_context('uid')
    def _compute_talep_sahibi_mi(self):
        for rec in self:
            rec.talep_sahibi_mi = rec.calisan_id.user_id == self.env.user

    @api.model
    def _default_calisan_id(self):
        return self.env.user.employee_id.id or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Yeni') == 'Yeni':
                vals['name'] = self.env['ir.sequence'].next_by_code('ekipman.zimmet') or 'Yeni'
            if not self.env.su:
                if not self.env.user.employee_id:
                    raise UserError('Çalışan profiliniz bulunmuyor.')
                user_emp_id = self.env.user.employee_id.id
                if vals.get('calisan_id'):
                    calisan_val = vals['calisan_id']
                    calisan_val_id = calisan_val if isinstance(calisan_val, int) else getattr(calisan_val, 'id', calisan_val)
                    if calisan_val_id != user_emp_id:
                        raise UserError('Sadece kendi adınıza talep açabilirsiniz.')
                vals['calisan_id'] = user_emp_id
                # Web istemcisi yeni kayıtta varsayılan state='taslak' değerini de gönderir.
                if vals.get('state', 'taslak') != 'taslak' or 'fiili_baslangic' in vals or 'fiili_bitis' in vals:
                    raise UserError('Kayıt yalnızca taslak olarak ve fiili tarihler olmadan oluşturulabilir.')
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
                    cakisan = cakisan_kayitlar[0]
                    raise ValidationError(
                        f"{cakisan.name} referanslı kayıtla {cakisan.planlanan_baslangic.strftime('%d.%m.%Y')} - "
                        f"{cakisan.planlanan_bitis.strftime('%d.%m.%Y')} tarihleri arasında çakışıyor."
                    )

    @api.constrains('cihaz_id', 'state')
    def _check_fiziksel_teslim(self):
        for rec in self:
            if rec.state == 'teslim_edildi' and rec.cihaz_id:
                domain = [
                    ('cihaz_id', '=', rec.cihaz_id.id),
                    ('state', '=', 'teslim_edildi'),
                    ('id', '!=', rec.id),
                ]
                teslim_edilenler = self.sudo().search(domain)
                if teslim_edilenler:
                    raise ValidationError("Bu cihaz şu anda başka bir çalışana teslim edilmiş durumdadır. Önce iade alınması gerekir.")

    def action_gonder(self):
        bugun = fields.Date.context_today(self)
        for rec in self:
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar talep edilebilir.')
            if rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taleplerinizi iletebilirsiniz.')
            if rec.planlanan_baslangic < bugun:
                raise UserError('Başlangıç tarihi geçmiş bir talep gönderilemez. Lütfen tarihleri güncelleyin.')
            rec.sudo().write({'state': 'talep_edildi'})

    def action_geri_cek(self):
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar geri çekilebilir.')
            if rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taleplerinizi geri çekebilirsiniz.')
            rec.sudo().write({'state': 'taslak'})

    def action_onayla(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        bugun = fields.Date.context_today(self)
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar onaylanabilir.')
            if rec.planlanan_bitis < bugun:
                raise UserError('Bitiş tarihi geçmiş bir talep onaylanamaz; teslim edilemeyeceği için reddedilmelidir.')
            rec.sudo().write({'state': 'onaylandi'})

    def action_reddet(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar reddedilebilir.')
            if not rec.red_gerekcesi:
                raise UserError('Reddetmek için red gerekçesi doldurulmalıdır.')
            rec.sudo().write({'state': 'reddedildi'})

    def action_teslim_et(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
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
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
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
            if rec.state == 'taslak':
                raise UserError('Taslak talepler iptal edilmez; Taslağı Sil ile silinebilir.')
            if rec.state not in ['talep_edildi', 'onaylandi']:
                raise UserError('Bu durumdaki bir kayıt iptal edilemez.')
            if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili') and rec.calisan_id.user_id != self.env.user:
                raise UserError('Başkasının talebini iptal edemezsiniz.')
            rec.sudo().write({'state': 'iptal'})

    def action_taslagi_sil(self):
        self.unlink()
        return self.env['ir.actions.act_window']._for_xml_id('ekipman_zimmet.action_ekipman_zimmet')

    def write(self, vals):
        if not self.env.su:
            restricted_for_all = {'state', 'fiili_baslangic', 'fiili_bitis', 'calisan_id'}
            if restricted_for_all.intersection(vals.keys()):
                raise UserError('Durum, çalışan ve fiili tarihler doğrudan güncellenemez.')
            if 'red_gerekcesi' in vals:
                if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
                    raise UserError('Red gerekçesini yalnızca yetkililer düzenleyebilir.')
                if any(rec.state != 'talep_edildi' for rec in self):
                    raise UserError('Red gerekçesi yalnızca onay bekleyen taleplerde düzenlenebilir.')

        restricted_fields = {'cihaz_id', 'planlanan_baslangic', 'planlanan_bitis'}
        if restricted_fields.intersection(vals.keys()):
            for rec in self:
                if rec.state != 'taslak':
                    raise UserError('Taslak durumunda olmayan kayıtların cihaz ve planlanan tarih bilgileri değiştirilemez.')
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar silinebilir.')
            if not self.env.su and rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taslaklarınızı silebilirsiniz.')
        return super().unlink()
