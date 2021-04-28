# -*- coding: utf-8 -*-
{
    'name': " Sales order: title, contact, attachment, archive.",

    'summary': """
        Sales order title, contact, attachment, archive.""",

    'description': """
        Sales order: title, contact, attachment, archive.
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Sales',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management','fal_invoice_additional_info', 'sale_stock'],

    # always loaded
    'data': [
        'views/sale_view.xml',
        'views/sale_order_line_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
