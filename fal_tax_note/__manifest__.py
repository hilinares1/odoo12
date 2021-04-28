# -*- coding: utf-8 -*-
{
    'name': 'Tax Note',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting',
    'summary': 'Tax Note',
    'description': '''
    This module has features:\n
    1. \n
    ''',
    'depends': [
        'account',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/tax_note_views.xml',
        'wizard/tax_payment_register_view.xml',
        'wizard/tax_selection_view.xml',
    ],
    'css': [],
    'qweb': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
