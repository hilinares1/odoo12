# -*- coding: utf-8 -*-
{
    'name': "Employee Private Address",

    'summary': """
        Employee Private Address""",

    'description': """
        module to create private contact when create employee
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Partner Management',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'fal_partner_private_address'],

    # always loaded
    'data': [
        'views/hr_employee.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
