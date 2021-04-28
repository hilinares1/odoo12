# -*- coding: utf-8 -*-
{
    'name': "Procurement Request",
    'version': '12.1.0.0.0',
    'depends': ['purchase_stock', 'sale'],
    'author': "Falinwa Limited",
    'website': 'https://falinwa.com',
    'category': 'Purchases',
    'summary': "Create Procurement Request",
    'description': """
    Module to add additional state Procurement Request
    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/sequence.xml',
        'wizard/procurement_request_wizard_view.xml',
        'views/purchase_view.xml',
        'views/product_view.xml',
        'views/stock_view.xml',
    ],
    'installable': True,
    'active': False,
    'application': False,
}
