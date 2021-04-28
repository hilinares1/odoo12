# -*- coding: utf-8 -*-
{
    'name': "Purchase Approval for Qualified Partner Only",
    'summary': """
        Purchase approval for qualified partner only""",
    'description': """
        Give approval restriction on purchase, for unqualified partner
    """,
    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Purchases',
    'version': '12.1.0.0.0',
    # any module necessary for this one to work correctly
    'depends': ['purchase', 'fal_partner_qualification'],
    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
