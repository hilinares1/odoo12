# -*- coding: utf-8 -*-
{
    'name': "Private Contact",

    'summary': """
        Private Contact""",

    'description': """
        Module to give private contact
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Partner Management',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts'],

    # always loaded
    'data': [
        'views/partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
