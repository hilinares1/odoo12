# -*- coding: utf-8 -*-
{
    'name': "Customer Statement",

    'summary': """
        Customer Statement Enhancement""",

    'description': """
        Customer Statement Enhancement
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting & Finance',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'fal_invoice_additional_info',
        'account_reports_followup',
    ],

    # always loaded
    'data': [
        "views/template_view.xml"
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
