# -*- coding: utf-8 -*-

{
    'name': 'Consolidation IFRS',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        Add IFRS option to account report (Enterprise)

        Warning:
        Can't manage the changing in book keeping currency

        Change Log
        12.2.0.0.0 - First Release
    ''',
    'website': 'https://falinwa.com',
    'category': 'Accounting',
    'summary': 'Account Report IFRS',
    'depends': [
        'account_reports',
        'fal_multicurrency_group'
    ],
    'data': [
        'data/account_financial_report_data.xml',
        'views/account_report_view.xml',
        'views/report_journal.xml',
        'views/search_template_view.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
