# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Product Category Vendor',
    'version': '12.2.0.0.0',
    'author': 'Falinwa Limited',
    'category': 'Purchase',
    'summary': "Add vendor on category",
    'description': """
        Sometimes you don't want to manage the vendor list by the product / variant.
        But in the entire category, this module allows it
    """,
    'depends': ['sale_stock', 'purchase_stock', 'sale_purchase'],
    'data': [
        'views/product_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
