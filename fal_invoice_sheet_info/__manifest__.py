# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice List on Sale and Purchase",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'summary': 'List Invoice in Sale and Purchase',
    "description": """
    Module to add invoice sheet on Order form
    """,
    "depends": ['account', 'purchase', 'sale_management', 'sale_stock'],
    'data': [
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
