# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Parent Account",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'summary': 'Account Hierarchial View',
    "description": """
    Module to get back the parent account
    """,
    "depends": [
        'account',
        'web_hierarchy',
    ],
    'summary': "Account Hierarchial Structure",
    'data': [
        # 'data/account_report.xml',
        'views/account_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
