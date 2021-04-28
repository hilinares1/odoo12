# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Expense report document",
    "version": "12.5.0.0.0",
    "author": "Falinwa",
    "description": """
    Module to print expense report document
    """,
    "depends": [
        'hr_expense',
    ],
    'init_xml': [],
    'data': [
        'views/expense.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
