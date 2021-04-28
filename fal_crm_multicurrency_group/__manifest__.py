# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "CRM MultiCurrency Group Company",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting and Finance',
    'summary': 'CRM MultiCurrency Group',
    "description": """
    This module convert CRM transaction into group company currency
    """,
    "depends": [
        'crm', 'fal_multicurrency_group',
    ],
    'data': [
        'views/crm_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
