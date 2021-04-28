# -*- coding: utf-8 -*-
{
    'name': 'Manufacturing Costing',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Manufacturing",
    'summary': 'Manufacturing Costing',
    'description': '''
        Module to add Hourly Costing.
    ''',
    'depends': [
        'fal_cost_bom',
        'fal_mrp_production_scrap',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/fal_hourly_cost_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
