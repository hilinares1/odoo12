# -*- coding: utf-8 -*-
{
    'name': 'MRP: Manufacturing Time Tracking',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Manufacturing',
    'summary': 'Manufacturing time tracking',
    'description': '''
        Module to add manufacturing time tracking feature.
    ''',
    'depends': [
        'fal_mrp_work_route',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'wizard/block_wizard.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
