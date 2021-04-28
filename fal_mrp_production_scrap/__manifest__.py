# -*- coding: utf-8 -*-
{
    'name': 'Production Scrap',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Manufacturing',
    'summary': 'Scrap Percentage in Production Order',
    'description': '''
    This module has features:\n
    1. Add function to adjust qty based on scrap percentage\n
    ''',
    'depends': [
        'fal_mrp_production_order',
    ],
    'data': [
        'views/mrp_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
