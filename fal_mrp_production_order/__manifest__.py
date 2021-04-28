# -*- coding: utf-8 -*-
{
    'name': 'Production Order',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Manufacturing',
    'summary': 'Create Production Order on Manufacturing',
    'description': '''
    This module has features:\n
    1. Group several manufacturing into a Production Number\n
    ''',
    'depends': [
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/mrp_security.xml',
        'data/sequence.xml',
        'views/fal_production_order_view.xml',
        'views/mrp_workorder_views.xml',
        'views/mrp_views.xml',
        'wizard/fal_production_date_fixed.xml',
    ],
    'css': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
