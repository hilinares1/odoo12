# -*- coding: utf-8 -*-
{
    'name': "Sale Approval for Qualified Partner Only",

    'summary': """
        Sale approval for qualified partner only""",

    'description': """
        Give approval restriction on sale, for unqualified partner
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Sales',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['fal_sale_approval', 'fal_partner_qualification'],

    # always loaded
    'data': [
        # 'wizard/sale_proposal_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
