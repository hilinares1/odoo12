# -*- coding: utf-8 -*-
{
    'name': "Account Bank Statements Menu",
    'version': '12.2.0.0.0',
    'depends': [
        'account_voucher',
        'account_cancel',],
    'author': "Falinwa Limited",
    'category': 'Accounting & Finance',
    'summary': """
        Add bank statement menu""",
    'description': """
     Add bank statement menu and margin
    """,
    # data files always loaded at installation
    'data': [
        'views/account_bank_statement_reconciliation_view.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
