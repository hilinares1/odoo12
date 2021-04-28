# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Bank Api',
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Accounting',
    'sequence': 1,
    'summary': 'Import Bank Statement from API',
    'description': """
    Module Provide by Falinwa to import bank statement
    from API (Made for Bank Central Asia)
    ==================================================

       """,
    'website': 'https://falinwa.com',
    'depends': ['base', 'account'],
    'data': [
        "security/ir.model.access.csv",
        'views/bank_api.xml',
        'views/account_journal_bank_api.xml',
        'wizard/bank_api_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
