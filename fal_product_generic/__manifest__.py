# -*- coding: utf-8 -*-
{
    'name': 'Product Enhancement',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Warehouse',
    'summary': 'Product Enhancement',
    'description': '''
        add field is stock product in product template,
        can copy account income  and account outcome.
    ''',
    'depends': [
        'account',
        'stock',
    ],
    'data': [
        'views/fal_product_views.xml',
        'views/res_config_settings.xml',
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
}
