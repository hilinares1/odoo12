# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "MultiCurrency Group Company",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting and Finance',
    'summary': 'MultiCurrency Group',
    "description": """
    This module convert all transaction into group company currency

    Changelog

    12.1.0.0.0 - First Release
    12.2.0.0.0 - Handle more case which needed to have the IFRS (Especially for report)
    """,
    "depends": [
        'account', 'sale_management', 'purchase'
    ],
    'data': [
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
        'views/account_move_view.xml',
        'views/analytic_account_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'security/ir.model.access.csv',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
