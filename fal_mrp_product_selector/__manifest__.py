# -*- coding: utf-8 -*-

{
    'name': 'MRP Product Attribute',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        * Inject it on MRP

    ''',
    'website': 'https://falinwa.com',
    'category': 'Warehouse',
    'summary': 'Advanced Product Attribute Management on MRP',
    'depends': [
        'fal_product_attribute',
        'mrp'
    ],
    'data': [
        'views/templates.xml'
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
