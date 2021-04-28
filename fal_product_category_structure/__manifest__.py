# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and
# licensing details.
{
    'name': 'Product Category Structure',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'description': """
Module to give additional feature of product category structure.
    """,
    'depends': [
        'stock_account',
        'sale_management',
        'web_hierarchy'],
    'data': [
        'views/product_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
