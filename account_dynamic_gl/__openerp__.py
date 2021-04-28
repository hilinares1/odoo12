# -*- coding: utf-8 -*-
{
    'name': 'Dynamic General Ledger Report',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Quanam',
    'website': 'http://www.quanam.com',
    'summary': 'Dynamic General Ledger Report with interactive drill down view and extra filters',
    'description': """
                This module support for viewing General Ledger (Also Trial Balance mode) on the screen with 
                drilldown option. Also add features to fliter report by Accounts, Account Types 
                and Analytic accounts. Option to download report into Pdf and Xlsx

                    """,
    'website': '',
    'depends': [
        'base_setup',
        'web',
        'account',
        'report',
        'report_xlsx',
        'account_financial_report_webkit',
        'account_financial_report_webkit_xls',
        'uy_account_report_general_ledger',
    ],
    'data': [
        "data/account_data.xml",
        "reports/report_generalledger1.xml",
        "views/views.xml",
    ],
    'demo': [
    ],
    'qweb':[
        'static/src/xml/dynamic_gl_report.xml'],
    "images":['static/description/Dynamic_Gl.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
