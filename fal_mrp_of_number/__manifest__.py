# -*- coding: utf-8 -*-
{
    'name': 'MRP Stock PO Number',
    'version': '12.2.0.0.0',
    'author': 'Falinwa Limited',
    'summary': 'PO number on stock move',
    'website': 'https://falinwa.com',
    'description': '''
    This module features is add PO number in stock move:\n
    ''',
    'depends': [
        'fal_finished_product_sequence',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}
