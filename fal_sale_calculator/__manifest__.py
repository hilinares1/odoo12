# -*- coding: utf-8 -*-
{
    "name": "Fal Sale Calculator",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Sale',
    'summary': 'Calculate sales order line price for selected product attribute values.',
    'website': 'https://falinwa.com',
    "description": """
        Sale Calculator for adding price to Sale Order Line according to the selected product attribute.
    """,
    "depends": [
        'sale',
        'sale_stock',
        'sale_management',
        'account',
        'fal_sale_product_selector',
    ],
    'data': [
        'views/product_views.xml',
        'views/sale_views.xml',
        'views/product_attribute_selector_templates.xml',
        'views/templates.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
