# -*- coding: utf-8 -*-
{
    "name": "Account Periods Lock",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Accounting & Finance",
    'summary': 'Resurface Fiscal Year',
    "description": """
    Resurface Fiscal Year function on odoo 9
    """,
    "depends": [
        'account',
    ],
    'init_xml': [],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/fal_account_periods_lock_view.xml',
    ],
    'demo': ['data/fal_account_periods_lock_demo.xml'],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
