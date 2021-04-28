# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Search',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Limited',
    'description': '''
        Module to add view to search by Project.
    ''',
    'depends': [
        'account',
        'sale',
        'purchase',
        'project'
    ],
    'init_xml': [],
    'data': [
        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
    'js': []
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
