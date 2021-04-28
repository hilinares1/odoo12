# -*- coding: utf-8 -*-
# Part of Odoo - CLuedoo Edition. Ask Falinwa/Cluedoo representative for full copyright and licensing details.
{
    'name': 'Clueedo Global Object',
    'version': '12.0.0.1.0',
    'category': 'Base',
    'description': """
        Mod : \n
        - Add modification to payment term company id to made global object \n
    """,
    'author': 'CLuedoo',
    'website': 'https://www.cluedoo.com',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
    ],
    'data': [
        'views/account_view_payment_term.xml',
        'views/res_config_settings.xml',
    ],
    'qweb': ['static/src/xml/*.xml',],
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
