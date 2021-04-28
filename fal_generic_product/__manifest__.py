# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Common Product Data",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Product',
    'summary': 'List Of Product',
    "description": """
    Module to install Generic Falinwa Product Category
    """,
    "depends": [
        'product',
        'purchase_stock',
        'inter_company_rules',
        'hr_expense'
    ],
    'data': [
        # 'data/fal_generic_product_category.xml',
        # 'data/fal_generic_product.xml',
        # 'data/fal_generic_product_variant.xml',
        'views/product_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
