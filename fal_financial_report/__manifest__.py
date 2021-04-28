# -*- coding: utf-8 -*-
{
    'name': "Falinwa Report Financial",

    'summary': """
        Module to add filter on acconut reports""",

    'description': """
        module to add filter account type in account report age receivable
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Accounting & Finance',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account_reports'],

    # always loaded
    'data': [
        'data/account_financial_report_data.xml',
        'views/account_view.xml',
        'views/report_financial.xml',
        'views/search_template_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [
    ],
}
