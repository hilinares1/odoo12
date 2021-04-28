# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Falinwa Activity Widget',
    'version': '12.0',
    'category': 'Base',
    'author': 'Falinwa Limited',
    'website': 'https://www.falinwa.com',
    'summary': 'Ir Model to inherit Activity',
    'description': """
        This module allow new model to inherit mail.activity.mixin in Studio
    """,
    'data': [
        "views/ir_model_views.xml",
    ],
    'depends': ['mail'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
