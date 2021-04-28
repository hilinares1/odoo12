# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Analytic Account in Partner And Product',
    'version': '12.2.0.0.0',
    'author': 'Falinwa Limited',
    'summary': """
        module to add Analytic account and additional field on product and partner.""",
    'website': "https://falinwa.com",
    'description': '''
        Module to define a Analytic Account in product.
    ''',
    'depends': [
        'stock_account',
        'purchase_stock',
        'sale_stock',
    ],
    'init_xml': [],
    'data': [
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'views/stock_view.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,

}
