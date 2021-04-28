# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Falinwa Generic CoAA",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting and Finance',
    'summary': 'Generic Chart of Analytic',
    "description": """
    Module to install Generic Falinwa Chart of Analytic Account
    """,
    "depends": [
        'fal_parent_account',
    ],
    'data': [
        'data/account_chart_analytic_generic_template.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
