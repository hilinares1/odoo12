# -*- coding: utf-8 -*-
{
    'name': 'Product Label',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Product",
    'summary': 'product barcode and labels report',
    'description': '''
        Module to create product label report
    ''',
    'depends': [
        'stock',
    ],
    'init_xml': [],
    'data': [
        'report/barcode_labels.xml',
        'report/product_label.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
