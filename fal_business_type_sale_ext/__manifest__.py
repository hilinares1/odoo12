# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Business Type',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'summary': 'Add business type object in sales',
    'category': 'Sale',
    'website': "https://falinwa.com",
    'description':
    '''
        Add business type in sales to manage multiple sequence
    ''',
    'depends': [
        'sale',
        'fal_business_type',
    ],
    'data': [
        'views/business_type_views.xml',
        'views/sale_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
