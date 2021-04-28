# -*- coding: utf-8 -*-
{
    "name": "Multi Payment Wizard",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    "description": """
    Module to give additional feature to have multiple register payment
    """,
    "depends": [
        'account',
        'sale_management',
        'purchase',
        'account_batch_payment',
    ],
    'init_xml': [],
    'data': [
        'data/payment_data.xml',
        'wizard/fal_multi_payment_wizard_view.xml',
        'views/account_invoice.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
