# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Generic CoA",
    "version": "12.1.0.0.0",
    'category': 'Accounting and Finance',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    "description": """
    Module to install Generic CoA
    """,
    "depends": [
        'fal_parent_account',
    ],
    'data': [
        'data/account_chart_generic_template.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
