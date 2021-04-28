# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Learning Resource',
    'version': '12.4.0.0.0',
    'author': 'Falinwa Limited',
    'description': '''
        Module to add Learning Resource
    ''',
    'depends': [
        'mail'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/learning_resource.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
