# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Extention',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resource',
    'summary': 'Generic Employee Data',
    'description': '''
        Module to add extention functional in HRM
    ''',
    'depends': [
        'hr',
        'partner_firstname'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view_inherit.xml',
        'views/hr_view.xml',

    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
