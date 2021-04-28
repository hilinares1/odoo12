# -*- coding: utf-8 -*-
{
    'name': 'SO Link to Production Order',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Manufacturing",
    'summary': 'SO Link to Production Order',
    'description': '''
    This module has features:\n
    1. In Sale Order Line add field contains generated production order.\n
    2. In Production Order add fields Sale Order ID and Sale Order Line ID.\n
    ''',
    'depends': [
        'sale_mrp',
        'fal_mrp_production_order',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/fal_production_order_view.xml',
        'views/sale_views.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
