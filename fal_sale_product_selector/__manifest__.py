# -*- coding: utf-8 -*-

{
    'name': 'Sale Product Attribute',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        * Inject it on Sale Object

    ''',
    'website': 'https://falinwa.com',
    'category': 'Warehouse',
    'summary': 'Advanced Product Attribute Management on Sale Order',
    'depends': [
        'fal_product_attribute',
        'sale_management'
    ],
    'data': [
        'views/sale_order_view.xml'
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
