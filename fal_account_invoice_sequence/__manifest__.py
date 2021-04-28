# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Invoice Draft Sequence',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'summary': 'Add invoice draft sequence',
    'category': 'Invoicing Management',
    'website': "https://falinwa.com",
    'description':
    '''
        This module contain some functions:\n
        1. Invoice number for account app\n
    ''',
    'depends': [
        'account',
    ],
    'data': [
        'data/account_invoice_sequence.xml',
        'views/account_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
