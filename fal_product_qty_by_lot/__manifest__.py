# -*- coding: utf-8 -*-
{
    "name": "Advanced LoT/SN Management",
    'version': '12.2.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Warehouse',
    'summary': 'Give a more advanced method of LoT management ',
    "description": """
        Give a more advanced method of LoT management in Odoo
    """,
    "depends": ['fal_serial_number_sticker'],
    'data': [
        'views/product_views.xml',
        'views/stock_production_lot_views.xml',
        'wizard/product_lot_discard_views.xml',
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
}
