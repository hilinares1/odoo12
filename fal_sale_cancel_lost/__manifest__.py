# -*- coding: utf-8 -*-
{
    'name': "Sale Cancel Lost",

    'summary': """
        Sale cancel lost""",

    'description': """
        Sale cancel lost
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Sales',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'data/reason_data.xml',
        'wizard/fal_cancel_quotation_wizard_view.xml',
        'wizard/fal_lost_quotation_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
