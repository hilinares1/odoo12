# -*- coding: utf-8 -*-
{
    "name": "Account Config",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Accounting & Finance",
    'summary': '',
    "description": """
    """,
    "depends": [
        'account','payment'
    ],
    'init_xml': [],
    'data': [
        'views/res_config_settings_view_form.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
    'auto_install': True,
}
