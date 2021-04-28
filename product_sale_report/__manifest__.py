# -*- coding: utf-8 -*-
{
    'name': 'Products Sales Report',
    'version': '12.0.1.0.2',
    'author': 'Yopi Angi',
    'license': 'LGPL-3',
    'maintainer': 'Yopi Angi<yopiangi@gmail.com>',
    'support': 'yopiangi@gmail.com',
    'category': 'Sales',
    'description': """
Product Sales Report
====================
Show products report based on sales
""",
    'depends': ['sale', 'product', 'web_google_maps'],
    'website': '',
    'data': [
        'security/ir.model.access.csv',
        'views/product_sale_report.xml',
        'views/sale_report.xml'
    ],
    'demo': [],
    'installable': True
}
