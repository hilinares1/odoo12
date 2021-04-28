# -*- coding: utf-8 -*-
{
    "name": "ASPONE Report",
    "version": "12.0.0.0.0",
    'summary': 'Getting the value for ASPONE report',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    "description": """
    Module to fetch from odoo record, and calculate to generate ASPONE report value.
    """,
    "depends": ['account', 'l10n_fr_reports'],
    "category": 'Accounting and Finance',
    'data': [
        'security/ir.model.access.csv',
        'views/account_aspone_view.xml',
    ],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
