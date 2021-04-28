# -*- coding: utf-8 -*-
{
    "name": "Account Asset Extension",
    "version": "12.2.0.0.0",
    'summary': 'Extends Asset functionality to match falinwa expectation (Enterprise)',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    "description": """
    Module to improve Account Asset module.
    """,
    "depends": ['account_asset'],
    "category": 'Accounting and Finance',
    'data': [
        'views/account_asset_view.xml',
        'views/account_invoice_view.xml',
        'wizard/fal_multi_confirm_asset_wizard_view.xml',
        'data/data.xml'
    ],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
