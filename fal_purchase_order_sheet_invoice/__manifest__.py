# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Purchase Order Sheet on Invoice",
    "version": "12.0.1.0.0",
    'author': 'Falinwa Limited',
    'summary': """
        Module to add purchase order sheet on Invoice form.""",
    "description": """
    Module to add purchase order sheet on Invoice form
    """,
    "depends": ['purchase'],
    'init_xml': [],
    'data': [
        'views/account_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
