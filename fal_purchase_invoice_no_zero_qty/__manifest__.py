# -*- coding: utf-8 -*-
{
    'name': "Falinwa Invoice No Zero Qty",

    'summary': """
        module to create invoice with no zero Quantity""",

    'description': """
        module to create invoice with no zero Quantity
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchases',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase_stock'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
