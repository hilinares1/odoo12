# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and
# licensing details.
{
    'name': 'Falinwa Analytic Account Behaviour',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'description': """
Module to give analytic account behaviour based on Falinwa expected.

Enterprise Only

    Changelog:
        V.12.0.1.0.0 - First Release
    """,
    'depends': [
        'account_asset', 'sale_stock', 'purchase_stock', 'sale_purchase', 'sale_timesheet', 'fal_analytic_account_tag'
    ],
    'data': [
        'views/account_invoice_form.xml',
        'views/bank_statement_view.xml',
        'views/res_config_setting_view.xml',
        'views/analytic_account.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
