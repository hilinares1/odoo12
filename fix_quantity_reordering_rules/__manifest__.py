# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Quantity Reordering Rule",
    "version": "12.0.1.0.0",
    'author': 'Falinwa Limited',
    'summary': 'add logic on Reordering Rules',
    'website': 'https://falinwa.com',
    "description": """
        Module to add additional option rule Order Fix Quantity
    """,
    "depends": ['stock'],
    'data': [
        'views/stock_warehouse_views.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
