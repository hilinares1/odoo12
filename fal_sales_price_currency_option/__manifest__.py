# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and
# licensing details.
{
    'name': 'Falinwa Sales Price Currency Option',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Product',
    'description': """
Module to give user's an option to currency for sales price.

Enterprise Only

    Changelog:
        V.12.0.1.0.0 - First Release
    """,
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/product_view.xml',
        'views/res_config_setting_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
