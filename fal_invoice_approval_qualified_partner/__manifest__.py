# -*- coding: utf-8 -*-
{
    'name': "Invoice Approval for Qualified Partner Only",
    "version": "12.1.0.0.0",
    'author': "Falinwa Limited",
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting & Finance',
    'summary': """
        Invoice approval for qualified partner only""",
    'description': """
        Give approval restriction on Invoice, for unqualified partner
    """,
    # any module necessary for this one to work correctly
    'depends': ['fal_partner_qualification', 'account'],
    'website': "https://falinwa.com",
    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/partner_qualified_demo.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
