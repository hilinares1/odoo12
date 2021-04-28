# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Falinwa Business Type',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'summary': 'Add business type object',
    'category': 'Base',
    'website': "https://falinwa.com",
    'description':
    '''
        Business type object.
    ''',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/business_type_views.xml',
        'wizard/create_menu_wizard.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
