from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import format_date


class EkipmanZimmet(models.Model):
    _name = 'ekipman.zimmet'
    _description = 'Ekipman Zimmeti'
    _inherit = ['mail.thread']
    _order = 'planlanan_baslangic desc, id desc'

    # Python kontrolleri (C2, C4) eşzamanlı işlemleri göremez; bu kısıtlar yarışta son savunmadır (C5).
    # Cihaz kimliği tek elemanlı aralık (int4range) olarak yazıldığı için btree_gist eklentisi gerekmez.
    # Ertelenmiştir: işlem içindeki ara durumlar (önce iade, sonra yeni teslim) sorun çıkarmaz ve
    # Python kontrollerinin search() ile yaptığı flush kısıta takılmaz; denetim geçiş sonunda yapılır.
    _sql_constraints = [
        ('cakisma_engeli',
         "EXCLUDE USING gist (int4range(cihaz_id, cihaz_id, '[]') WITH &&, "
         "daterange(planlanan_baslangic, planlanan_bitis, '[]') WITH &&) "
         "WHERE (state IN ('onaylandi', 'teslim_edildi')) DEFERRABLE INITIALLY DEFERRED",
         'Bu cihaz seçilen tarihlerde başka bir onaylı veya teslim edilmiş talebe ayrılmış.'),
        ('tek_teslim',
         "EXCLUDE (cihaz_id WITH =) WHERE (state = 'teslim_edildi') DEFERRABLE INITIALLY DEFERRED",
         'Bu cihaz şu anda başka bir çalışana teslim edilmiş durumda; önce iade alınması gerekir.'),
    ]

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
            ('kayip', 'Kayıp'),
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
        domain=[('kullanilabilirlik', '=', 'kullanilabilir')],
    )
    cihaz_aciklama = fields.Text(
        related='cihaz_id.aciklama',
        string='Cihaz Açıklaması',
    )
    cihaz_kullanilabilirlik = fields.Selection(
        related='cihaz_id.kullanilabilirlik',
        string='Cihaz Durumu',
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
    iptal_nedeni = fields.Text(
        string='İptal Nedeni',
        copy=False,
        tracking=True,
    )
    # Bekleyen uzatma ayrı bir durum değil, bu alanın dolu olmasıdır (B9).
    istenen_bitis = fields.Date(
        string='İstenen Bitiş',
        copy=False,
        tracking=True,
    )
    # Güncel Talepler filtresi bu tarihe bakar; write_date kapandıktan sonraki her yazmada değişir.
    kapanis_tarihi = fields.Date(
        string='Kapanış Tarihi',
        readonly=True,
        copy=False,
    )
    kullanici_geri_bildirimi = fields.Text(
        string='Kullanıcı Geri Bildirimi',
        copy=False,
        tracking=True,
    )
    kapanis_notu = fields.Text(
        string='İade / Kayıp Notu',
        copy=False,
        tracking=True,
    )
    talep_sahibi_mi = fields.Boolean(compute='_compute_talep_sahibi_mi')
    yetkili_mi = fields.Boolean(compute='_compute_yetkili_mi')

    @api.depends('calisan_id.user_id')
    @api.depends_context('uid')
    def _compute_talep_sahibi_mi(self):
        for rec in self:
            rec.talep_sahibi_mi = rec.calisan_id.user_id == self.env.user

    @api.depends_context('uid')
    def _compute_yetkili_mi(self):
        self.yetkili_mi = self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili')

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
                # Web istemcisi yeni kayıtta formdaki varsayılanları da gönderir (state='taslak',
                # boş tarihler); yalnızca dolu değerler engellenir.
                surec_alanlari = ('fiili_baslangic', 'fiili_bitis', 'kapanis_tarihi', 'istenen_bitis')
                if vals.get('state', 'taslak') != 'taslak' or any(vals.get(alan) for alan in surec_alanlari):
                    raise UserError('Kayıt yalnızca taslak olarak ve süreç tarihleri olmadan oluşturulabilir.')
        kayitlar = super().create(vals_list)
        if not self.env.su:
            kayitlar._cihaz_kullanilabilir_olmali('talep edilemez')
        return kayitlar

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
                        f"{cakisan.name} referanslı kayıtla {format_date(self.env, cakisan.planlanan_baslangic)} - "
                        f"{format_date(self.env, cakisan.planlanan_bitis)} tarihleri arasında çakışıyor."
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

    def _kisitlari_simdi_denetle(self):
        # Ertelenmiş kısıtlar normalde commit'te denetlenir; commit Odoo'nun istek döngüsünün dışında
        # olduğu için oradaki ihlal kullanıcıya teknik bir hata olarak döner. Geçiş sonunda hemen
        # denetlenince eşzamanlı işlemden doğan ihlal yakalanır ve kısıtın mesajıyla gösterilir.
        # IMMEDIATE bekleyen denetimleri yapar ama modu işlemin sonuna kadar değiştirir; sonraki
        # geçişlerin ara durumları için kısıtlar yeniden ertelenir.
        kisitlar = "ekipman_zimmet_cakisma_engeli, ekipman_zimmet_tek_teslim"
        self.env.flush_all()
        self.env.cr.execute(f"SET CONSTRAINTS {kisitlar} IMMEDIATE")
        self.env.cr.execute(f"SET CONSTRAINTS {kisitlar} DEFERRED")

    def action_gonder(self):
        bugun = fields.Date.context_today(self)
        for rec in self:
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar talep edilebilir.')
            if rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taleplerinizi iletebilirsiniz.')
            if rec.planlanan_baslangic < bugun:
                raise UserError('Başlangıç tarihi geçmiş bir talep gönderilemez. Lütfen tarihleri güncelleyin.')
            rec._cihaz_kullanilabilir_olmali('gönderilemez')
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
            rec._cihaz_kullanilabilir_olmali('onaylanamaz')
            rec.sudo().write({'state': 'onaylandi'})
        self._kisitlari_simdi_denetle()

    def action_reddet(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'talep_edildi':
                raise UserError('Yalnızca talep edildi durumundaki kayıtlar reddedilebilir.')
            if not rec.red_gerekcesi:
                raise UserError('Reddetmek için red gerekçesi doldurulmalıdır.')
            rec.sudo().write({'state': 'reddedildi', 'kapanis_tarihi': fields.Date.context_today(self)})

    def action_teslim_et(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'onaylandi':
                raise UserError('Yalnızca onaylanmış kayıtlar teslim edilebilir.')
            
            bugun = fields.Date.context_today(self)
            if not (rec.planlanan_baslangic <= bugun <= rec.planlanan_bitis):
                raise UserError('Teslimat yalnızca planlanan tarih aralığında yapılabilir. Erken veya süresi geçmiş teslimat yapılamaz.')
            rec._cihaz_kullanilabilir_olmali('teslim edilemez')

            rec.sudo().write({
                'state': 'teslim_edildi',
                'fiili_baslangic': bugun
            })
        self._kisitlari_simdi_denetle()

    def action_iade_al(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'teslim_edildi':
                raise UserError('Yalnızca teslim edilmiş kayıtlar iade alınabilir.')
            bugun = fields.Date.context_today(self)
            rec.sudo().write({
                'state': 'iade_edildi',
                'fiili_bitis': bugun,
                'kapanis_tarihi': bugun,
                'istenen_bitis': False,
            })
            rec.cihaz_id.sudo().write({'kullanilabilirlik': 'kontrolde'})

    def action_kayip(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if rec.state != 'teslim_edildi':
                raise UserError('Yalnızca teslim edilmiş kayıtlar kayıp olarak işaretlenebilir.')
            if not rec.kapanis_notu:
                raise UserError('Kayıp olarak işaretlemek için İade / Kayıp Notu yazılmalıdır.')
            bugun = fields.Date.context_today(self)
            rec.sudo().write({
                'state': 'kayip',
                'fiili_bitis': bugun,
                'kapanis_tarihi': bugun,
                'istenen_bitis': False,
            })
            rec.cihaz_id.sudo().write({'kullanilabilirlik': 'kayip'})

    def action_iptal(self):
        for rec in self:
            if rec.state == 'taslak':
                raise UserError('Taslak talepler iptal edilmez; Taslağı Sil ile silinebilir.')
            if rec.state not in ['talep_edildi', 'onaylandi']:
                raise UserError('Bu durumdaki bir kayıt iptal edilemez.')
            if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili') and rec.calisan_id.user_id != self.env.user:
                raise UserError('Başkasının talebini iptal edemezsiniz.')
            if not rec.iptal_nedeni:
                raise UserError('İptal etmek için iptal nedeni doldurulmalıdır.')
            rec.sudo().write({
                'state': 'iptal',
                'kapanis_tarihi': fields.Date.context_today(self),
                'istenen_bitis': False,
            })

    def action_uzatmayi_onayla(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if not rec.istenen_bitis:
                raise UserError('Bekleyen bir uzatma isteği yok.')
            rec._cihaz_kullanilabilir_olmali('uzatma onaylanamaz')
            rec.sudo().write({'planlanan_bitis': rec.istenen_bitis, 'istenen_bitis': False})
        self._kisitlari_simdi_denetle()

    def action_uzatmayi_reddet(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')
        for rec in self:
            if not rec.istenen_bitis:
                raise UserError('Bekleyen bir uzatma isteği yok.')
            istenen = format_date(self.env, rec.istenen_bitis)
            rec.sudo().write({'istenen_bitis': False})
            rec._message_log(body=f"{istenen} tarihine uzatma isteği reddedildi.")

    def action_uzatmayi_geri_cek(self):
        for rec in self:
            if not rec.istenen_bitis:
                raise UserError('Bekleyen bir uzatma isteği yok.')
            rec.write({'istenen_bitis': False})

    def action_taslagi_sil(self):
        self.unlink()
        return self.env['ir.actions.act_window']._for_xml_id('ekipman_zimmet.action_ekipman_zimmet')

    def write(self, vals):
        if not self.env.su:
            restricted_for_all = {'state', 'fiili_baslangic', 'fiili_bitis', 'calisan_id', 'kapanis_tarihi'}
            if restricted_for_all.intersection(vals.keys()):
                raise UserError('Durum, çalışan, fiili tarihler ve kapanış tarihi doğrudan güncellenemez.')
            if 'red_gerekcesi' in vals:
                if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
                    raise UserError('Red gerekçesini yalnızca yetkililer düzenleyebilir.')
                if any(rec.state != 'talep_edildi' for rec in self):
                    raise UserError('Red gerekçesi yalnızca onay bekleyen taleplerde düzenlenebilir.')
            if 'istenen_bitis' in vals:
                self._uzatma_istegini_denetle(vals['istenen_bitis'])
            if 'kullanici_geri_bildirimi' in vals:
                if any(rec.calisan_id.user_id != self.env.user for rec in self):
                    raise UserError('Geri bildirimi yalnızca talep sahibi yazabilir.')
                if any(rec.state != 'teslim_edildi' for rec in self):
                    raise UserError('Geri bildirim yalnızca cihaz sizdeyken yazılabilir.')
            if 'kapanis_notu' in vals:
                if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
                    raise UserError('İade / kayıp notunu yalnızca yetkililer yazabilir.')
                if any(rec.state != 'teslim_edildi' for rec in self):
                    raise UserError('İade / kayıp notu yalnızca teslim edilmiş talepte yazılabilir.')
            if 'iptal_nedeni' in vals:
                yetkili = self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili')
                if any(not yetkili and rec.calisan_id.user_id != self.env.user for rec in self):
                    raise UserError('İptal nedenini yalnızca talep sahibi veya yetkili yazabilir.')
                if any(rec.state not in ('talep_edildi', 'onaylandi') for rec in self):
                    raise UserError('İptal nedeni yalnızca onay bekleyen veya onaylı taleplerde yazılabilir.')

            restricted_fields = {'cihaz_id', 'planlanan_baslangic', 'planlanan_bitis'}
            if restricted_fields.intersection(vals.keys()):
                for rec in self:
                    if rec.state != 'taslak':
                        raise UserError('Taslak durumunda olmayan kayıtların cihaz ve planlanan tarih bilgileri değiştirilemez.')
        sonuc = super().write(vals)
        if 'cihaz_id' in vals and not self.env.su:
            self._cihaz_kullanilabilir_olmali('talep edilemez')
        return sonuc

    def _cihaz_kullanilabilir_olmali(self, islem):
        # Yalnızca yeni işlemleri engeller; cihaz kullanılamaz olunca mevcut kayıtlar değişmez (A7).
        for rec in self:
            cihaz = rec.cihaz_id
            if cihaz.kullanilabilirlik != 'kullanilabilir':
                durum = dict(cihaz._fields['kullanilabilirlik'].selection)[cihaz.kullanilabilirlik]
                raise UserError(f"Cihaz şu an {durum.lower()}; {islem}.")

    def _uzatma_istegini_denetle(self, istenen):
        bugun = fields.Date.context_today(self)
        istenen = fields.Date.to_date(istenen)
        for rec in self:
            if rec.calisan_id.user_id != self.env.user:
                raise UserError('Uzatmayı yalnızca talep sahibi isteyebilir.')
            if rec.state not in ('onaylandi', 'teslim_edildi'):
                raise UserError('Uzatma yalnızca onaylı veya teslim edilmiş talepte istenebilir.')
            if istenen and istenen <= rec.planlanan_bitis:
                raise UserError('İstenen bitiş, mevcut bitiş tarihinden sonra olmalıdır.')
            if istenen and istenen < bugun:
                raise UserError('İstenen bitiş bugünden önce olamaz.')

    def unlink(self):
        for rec in self:
            if rec.state != 'taslak':
                raise UserError('Yalnızca taslak durumundaki kayıtlar silinebilir.')
            if not self.env.su and rec.calisan_id.user_id != self.env.user:
                raise UserError('Yalnızca kendi taslaklarınızı silebilirsiniz.')
        return super().unlink()
