# -*- coding: utf-8 -*-
{
    'name': "Partner Code",

    'summary': """
        Give code on partner""",

    'description': """
        Module to have different code for customer and supplier partner
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Partner Management',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'data/partner_sequence.xml',
        'views/partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
