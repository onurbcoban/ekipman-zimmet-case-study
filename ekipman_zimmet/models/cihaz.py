from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError
from odoo.tools import format_date
class EkipmanCihaz(models.Model):
    _name = 'ekipman.cihaz'
    _description = 'Ekipman Cihazı'
    _inherit = ['mail.thread']
    _order = 'etiket_no, id'

    name = fields.Char(string='Cihaz Adı', required=True)
    etiket_no = fields.Char(string='Etiket No', required=True, copy=False)
    seri_no = fields.Char(string='Seri No')
    aciklama = fields.Text(string='Açıklama')
    # Yalnızca butonlarla değişir (kontrol, bakım, kayıp, hurda); fiziksel durumdan bağımsızdır (A7).
    kullanilabilirlik = fields.Selection(
        selection=[
            ('kullanilabilir', 'Kullanılabilir'),
            ('kontrolde', 'Kontrolde'),
            ('bakimda', 'Bakımda'),
            ('kayip', 'Kayıp'),
            ('hurda', 'Hurda'),
        ],
        string='Kullanılabilirlik',
        default='kullanilabilir',
        required=True,
        tracking=True,
    )
    kategori_id = fields.Many2one(
        'ekipman.kategori',
        string='Kategori',
        required=True,
        ondelete='restrict',
    )
    active = fields.Boolean(string='Aktif', default=True)

    zimmet_ids = fields.One2many(
        'ekipman.zimmet',
        'cihaz_id',
        string='Zimmet Kayıtları',
    )
    gecmis_zimmet_ids = fields.One2many(
        'ekipman.zimmet',
        'cihaz_id',
        string='Geçmiş Zimmetler',
        domain=[('state', 'in', ['teslim_edildi', 'iade_edildi'])],
    )

    # A3 ve E1 Kararları
    fiziksel_durum = fields.Selection(
        selection=[
            ('bosta', 'Zimmette değil'),
            ('zimmette', 'Zimmette'),
        ],
        string='Fiziksel Durum',
        compute='_compute_durum_ve_kimde',
        store=True,
        default='bosta',
    )
    su_an_kimde_id = fields.Many2one(
        'hr.employee',
        string='Şu An Kimde',
        compute='_compute_durum_ve_kimde',
        store=True,
        groups="ekipman_zimmet.group_zimmet_yetkili",
    )

    # Kontrol eden yetkili, son iadenin notlarını cihaz formunda görür (A7, B10).
    son_iade_id = fields.Many2one(
        'ekipman.zimmet',
        string='Son İade',
        compute='_compute_son_iade',
        groups="ekipman_zimmet.group_zimmet_yetkili",
    )
    son_iade_eden_id = fields.Many2one('hr.employee', string='İade Eden', compute='_compute_son_iade', groups="ekipman_zimmet.group_zimmet_yetkili")
    son_iade_tarihi = fields.Date(string='İade Tarihi', compute='_compute_son_iade', groups="ekipman_zimmet.group_zimmet_yetkili")
    son_iade_geri_bildirimi = fields.Text(string='Kullanıcı Geri Bildirimi', compute='_compute_son_iade', groups="ekipman_zimmet.group_zimmet_yetkili")
    son_iade_notu = fields.Text(string='İade Notu', compute='_compute_son_iade', groups="ekipman_zimmet.group_zimmet_yetkili")

    # E4 Kararı
    dolu_tarihler = fields.Text(
        string='Dolu Tarihler',
        compute='_compute_dolu_tarihler',
    )

    _sql_constraints = [
        ('etiket_no_unique', 'UNIQUE(etiket_no)', 'Bu etiket numarasına sahip bir cihaz zaten mevcut!'),
    ]

    @api.depends('zimmet_ids.state', 'zimmet_ids.calisan_id')
    def _compute_durum_ve_kimde(self):
        for rec in self:
            aktif_zimmet = rec.zimmet_ids.filtered(lambda z: z.state == 'teslim_edildi')
            if aktif_zimmet:
                rec.fiziksel_durum = 'zimmette'
                rec.su_an_kimde_id = aktif_zimmet[0].calisan_id
            else:
                rec.fiziksel_durum = 'bosta'
                rec.su_an_kimde_id = False

    @api.depends('zimmet_ids.state', 'zimmet_ids.planlanan_baslangic', 'zimmet_ids.planlanan_bitis')
    def _compute_dolu_tarihler(self):
        today = fields.Date.context_today(self)
        for rec in self:
            bloklayanlar = rec.sudo().zimmet_ids.filtered(
                lambda z: z.state in ('onaylandi', 'teslim_edildi') and z.planlanan_bitis
            ).sorted(key=lambda z: z.planlanan_baslangic or today)

            satirlar = []
            for z in bloklayanlar:
                if z.planlanan_bitis >= today:
                    if z.planlanan_baslangic and z.planlanan_bitis:
                        satirlar.append(f"{format_date(self.env, z.planlanan_baslangic)} - {format_date(self.env, z.planlanan_bitis)}")
                elif z.state == 'teslim_edildi' and z.planlanan_bitis < today:
                    satirlar.append("Şu an elde, iade bekleniyor")
            rec.dolu_tarihler = "\n".join(satirlar) if satirlar else False

    @api.depends('zimmet_ids.state', 'zimmet_ids.kullanici_geri_bildirimi', 'zimmet_ids.kapanis_notu')
    def _compute_son_iade(self):
        Zimmet = self.env['ekipman.zimmet'].sudo()
        for rec in self:
            son = Zimmet.search([
                ('cihaz_id', '=', rec.id),
                ('state', '=', 'iade_edildi'),
            ], order='kapanis_tarihi desc, id desc', limit=1)
            rec.son_iade_id = son.id
            rec.son_iade_eden_id = son.calisan_id.id
            rec.son_iade_tarihi = son.fiili_bitis
            rec.son_iade_geri_bildirimi = son.kullanici_geri_bildirimi
            rec.son_iade_notu = son.kapanis_notu

    def _compute_display_name(self):
        for rec in self:
            if rec.etiket_no and rec.name:
                rec.display_name = f"[{rec.etiket_no}] {rec.name}"
            else:
                rec.display_name = rec.name or rec.etiket_no or ''

    def unlink(self):
        for rec in self:
            if rec.zimmet_ids:
                raise UserError("Geçmiş zimmet kaydı olan cihaz silinemez, arşivleyiniz.")
        return super().unlink()

    def _yetkili_olmali(self):
        if not self.env.user.has_group('ekipman_zimmet.group_zimmet_yetkili'):
            raise AccessError('Bu işlemi sadece Yetkililer yapabilir.')

    def _kullanilabilirlik_degistir(self, beklenen, yeni):
        self._yetkili_olmali()
        etiketler = dict(self._fields['kullanilabilirlik'].selection)
        for rec in self:
            if rec.kullanilabilirlik not in beklenen:
                raise UserError(f"Cihaz şu an {etiketler[rec.kullanilabilirlik].lower()}; bu işlem yapılamaz.")
            if rec.fiziksel_durum == 'zimmette':
                raise UserError('Zimmetteki cihazın durumu değiştirilemez; önce iade alınmalıdır.')
            rec.sudo().write({'kullanilabilirlik': yeni})

    def action_kontrol_tamamlandi(self):
        self._kullanilabilirlik_degistir(('kontrolde',), 'kullanilabilir')

    def action_bakima_al(self):
        self._kullanilabilirlik_degistir(('kullanilabilir', 'kontrolde'), 'bakimda')

    def action_kullanilabilir_yap(self):
        self._kullanilabilirlik_degistir(('bakimda',), 'kullanilabilir')

    def write(self, vals):
        if 'kullanilabilirlik' in vals and not self.env.su:
            raise UserError('Kullanılabilirlik yalnızca cihaz formundaki işlemlerle değiştirilebilir.')
        if vals.get('active') is False:
            for rec in self:
                aktif_zimmet = rec.zimmet_ids.filtered(lambda z: z.state in ('onaylandi', 'teslim_edildi'))
                if aktif_zimmet:
                    raise UserError("Aktif zimmeti olan cihaz arşivlenemez.")
        return super().write(vals)
