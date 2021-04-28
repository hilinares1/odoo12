# -*- coding: utf-8 -*-
{
    'name': "Partner qualification",

    'summary': """
        Module to give qualification to partner.""",

    'description': """
        Module to give qualification to partner.
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Partner Management',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/partner.xml',
        'views/users.xml',
        'wizard/partner_qualified.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
