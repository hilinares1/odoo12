# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Purchase Modify Analytic Account",
    "version": "12.0.1.0.0",
    'author': 'Falinwa Limited',
    'summary': """
        Module to modify analytic account on purchase.""",
    "description": """
    Module to modify analytic account
    """,
    "depends": [
        'purchase',
    ],
    'init_xml': [],
    'data': [
        'wizard/project_modify_wizard_view.xml',
        'views/purchase_view.xml',
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
    'js': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
