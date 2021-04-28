# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Partner Netting",
    "version": "12.3.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Accounting",
    'summary': '',
    "description": """
        Partner netting for Invoices.
    """,
    "depends": [
        'account',
        'account_accountant',
    ],
    'init_xml': [],
    'data': [
        'views/account.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
