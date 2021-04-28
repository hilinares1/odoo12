# -*- coding: utf-8 -*-
{
    'name': "Company Short Name",

    'summary': """
        Company short name""",

    'description': """
        Give short name to company
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
        # 'security/ir.model.access.csv',
        'views/partner.xml',
        'views/company.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
