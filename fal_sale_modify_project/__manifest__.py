# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Sale Modify Analytic Account",
    "version": "12.0.1.0.0",
    'author': 'Falinwa Limited',
    'summary': """
        Module to modify analytic account on sales.""",
    "description": """
    Module to modify analytic account
    """,
    "depends": [
        'sale_management',
    ],
    'init_xml': [],
    'data': [
        'wizard/project_modify_wizard_view.xml',
        'views/sale_view.xml',
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
    'js': [],
}
