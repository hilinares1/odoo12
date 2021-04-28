# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Crm Business Type',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'summary': 'Add business type object in crm',
    'category': 'CRM',
    'website': "https://falinwa.com",
    'description':
    '''
        Add business type in crm to manage multiple sequence
    ''',
    'depends': [
        'crm',
        'fal_business_type',
    ],
    'data': [
        'views/business_type_views.xml',
        'views/crm_lead_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
