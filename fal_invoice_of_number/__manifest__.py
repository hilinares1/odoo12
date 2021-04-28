# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice PO Number",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting',
    'summary': 'invoice PO number',
    "description": """
    invoice PO number
    """,
    "depends": [
        'account',
        'fal_mrp_sale_link',
    ],
    'data': [
        'views/invoice.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
