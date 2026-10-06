{
    'name': 'Ekipman Zimmet',
    'version': '18.0.1.0.0',
    'summary': 'Mühendislik ekipmanları zimmet ve talep takibi',
    'author': 'Onur',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/kategori_views.xml',
        'views/cihaz_views.xml',
        'views/zimmet_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}