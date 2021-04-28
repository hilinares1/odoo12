# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Three Levels Approval",

    'summary': """ Purchase Order Approval""",

    'description': """
        This module have three step to approval.
        UPO can be approved by 1 person (Manager), 2 persons (Manager and Accountant) or 
        3 persons (Manager, Accountant and Director) depends on the PO’s total amount.
    """,

    'author': "KIU Myanmar",
    'website': "https://www.kiuglobal.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Three Levels Approval in Purchase Order',
    'version': '12.0',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account'],

    # always loaded
    'data': [
        'security/purchase_security.xml',
        'views/purchase_view.xml',
        'views/res_company_view.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}