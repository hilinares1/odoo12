# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Generate Payroll",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    "description": """
    Module to developed Odoo payroll based on Falinwa standard.
    """,
    "depends" : ['hr_payroll_account'],
    'init_xml': [],
    'data': [
        'views/hr_payroll_view.xml',
    ],
    'css': [],
    'js' : [
    ],
    'qweb': [],
    'installable': True,
    'active': False,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
