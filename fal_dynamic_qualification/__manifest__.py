# -*- coding: utf-8 -*-
{
    'name': "Dynamic Qualification",

    'summary': """
        Create Dynamic fields for mandatory for Qualification Process""",

    'description': """
        Create Dynamic fields for mandatory for Qualification Process
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Partner Management',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['fal_sale_approval_qualified_partner'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/company.xml',
        'wizard/partner_qualified.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
