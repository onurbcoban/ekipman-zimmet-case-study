from odoo import models, fields


class EkipmanKategori(models.Model):
    _name = 'ekipman.kategori'
    _description = 'Ekipman Kategorisi'
    _order = 'name'

    name = fields.Char(string='Kategori Adı', required=True)
    description = fields.Text(string="Açıklama")
