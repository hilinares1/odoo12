# -*- coding: utf-8 -*-
{
    'name': "Falinwa Account Report Groupby",

    'summary': """
        Module to change groupby on acconut reports""",

    'description': """
        Module to change groupby on acconut reports
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Accounting & Finance',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account_reports', 'fal_parent_account'],

    # always loaded
    'data': [
        'views/report_financial.xml',
        'views/search_template_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [
    ],
}
