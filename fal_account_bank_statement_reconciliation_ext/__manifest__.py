# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "ACC: Bank Statement Reconciliation Ext",
    "version": "12.4.0.0.0",
    'category': 'Accounting',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    "description": """
    Module to extend bank statement reconciliation
    """,
    "depends": ['product', 'account_accountant'],
    'init_xml': [],
    'data': [
        'views/assets.xml',
        'views/account_bank_statement_reconciliation_view.xml',
        'views/product_view.xml',
    ],
    'qweb': [
        # 'static/xml/account_reconciliation.xml',
    ],
    'demo': [],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
