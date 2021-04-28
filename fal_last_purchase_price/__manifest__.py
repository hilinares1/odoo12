# -*- coding: utf-8 -*-
{
    'name': 'Costing method: Last Purchase Price',
    'version': '12.0.1.0.0',
    'category': 'Inventory',
    'summary': "Introducing new costing method in Odoo 'last purchase price'",
    'author': 'Falinwa Limited',
    'website': 'https://www.openhrms.com',
    'description': """
    This module introduces a new costing method to Odoo. That will update a product's cost price when a new purchase happens with the purchasing rate. if you enables automatic stock valuation and provided a price difference account, this module will generate stock journal entry to update the stock value according to the price change.
""",
    'depends': ['stock',
                'stock_account',
                'purchase'
                ],
    'data': [],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'application': False,
    'installable': True,
    'auto_install': False,
}
