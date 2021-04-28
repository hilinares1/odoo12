# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Finished Product Sequence",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'summary': 'PO number sequence',
    "description": """
    Module to define a sequence on manufacture
    when the product is finished product.
    """,
    "depends": ['fal_mrp_sale_link'],
    'init_xml': [],
    'data': [
        'data/finished_product_sequence.xml',
        'views/mrp_view.xml',
    ],
    'css': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}
