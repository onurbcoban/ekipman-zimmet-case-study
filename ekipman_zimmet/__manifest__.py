{
    'name': 'Ekipman Zimmet',
    'version': '18.0.1.0.0',
    'summary': 'Mühendislik ekipmanları zimmet ve talep takibi',
    'author': 'Onur',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/sequence.xml',
        'views/kategori_views.xml',
        'views/cihaz_views.xml',
        'views/zimmet_views.xml',
        'views/menu_views.xml',
        'wizard/zimmet_toplu_views.xml',
    ],
    'demo': [
        'demo/kullanicilar.xml',
        'demo/ekipman.xml',
        'demo/zimmet.xml',
    ],
    'installable': True,
    'application': True,
}