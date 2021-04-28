# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'CRM: Wishlist on Opportunity',
    'version': '1.0',
    'author': 'Falinwa Indonesia',
    'description': '''
    This module has features:\n
    1. Add wishlist function inside opportunity\n
    ''',
    'depends': [
        'crm',
        'fal_product_size_detail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
