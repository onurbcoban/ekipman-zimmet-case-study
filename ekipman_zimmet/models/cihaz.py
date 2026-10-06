from odoo import models, fields, api


class EkipmanCihaz(models.Model):
    _name = 'ekipman.cihaz'
    _description = 'Ekipman Cihazı'
    _order = 'etiket_no, id'

    name = fields.Char(string='Cihaz Adı', required=True)
    etiket_no = fields.Char(string='Etiket No', required=True, copy=False)
    seri_no = fields.Char(string='Seri No')
    kategori_id = fields.Many2one(
        'ekipman.kategori',
        string='Kategori',
        required=True,
        ondelete='restrict',
    )
    active = fields.Boolean(string='Aktif', default=True)

    # A5 Kararı: zimmet_ids One2many ilişkisi
    zimmet_ids = fields.One2many(
        'ekipman.zimmet',
        'cihaz_id',
        string='Zimmet Kayıtları',
    )

    # A3 ve E1 Kararları
    fiziksel_durum = fields.Selection(
        selection=[
            ('musait', 'Şu an müsait'),
            ('zimmette', 'Zimmette'),
        ],
        string='Fiziksel Durum',
        compute='_compute_durum_ve_kimde',
        store=True,
        default='musait',
    )
    su_an_kimde_id = fields.Many2one(
        'hr.employee',
        string='Şu An Kimde',
        compute='_compute_durum_ve_kimde',
        store=True,
    )

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
                rec.fiziksel_durum = 'musait'
                rec.su_an_kimde_id = False

    def _compute_dolu_tarihler(self):
        today = fields.Date.context_today(self)
        for rec in self:
            bloklayanlar = rec.sudo().zimmet_ids.filtered(
                lambda z: z.state in ('onaylandi', 'teslim_edildi')
            ).sorted(key=lambda z: z.planlanan_baslangic or today)

            satirlar = []
            for z in bloklayanlar:
                if z.state == 'teslim_edildi' and z.planlanan_bitis and z.planlanan_bitis < today:
                    satirlar.append(f"{z.planlanan_baslangic} - {z.planlanan_bitis} (Şu an elde, iade bekleniyor)")
                elif z.planlanan_bitis and z.planlanan_bitis >= today:
                    satirlar.append(f"{z.planlanan_baslangic} - {z.planlanan_bitis}")
            rec.dolu_tarihler = "\n".join(satirlar) if satirlar else "Müsait"

    def _compute_display_name(self):
        for rec in self:
            if rec.etiket_no and rec.name:
                rec.display_name = f"[{rec.etiket_no}] {rec.name}"
            else:
                rec.display_name = rec.name or rec.etiket_no or ''
