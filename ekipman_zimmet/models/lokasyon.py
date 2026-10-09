from odoo import models, fields


class EkipmanLokasyon(models.Model):
    _name = 'ekipman.lokasyon'
    _description = 'Ekipman Lokasyonu'
    _order = 'name'

    name = fields.Char(string='Lokasyon Adı', required=True)
    description = fields.Text(string="Açıklama")
