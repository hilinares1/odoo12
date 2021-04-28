# -*- coding: utf-8 -*-

{
    'name': 'Cost of BoM',
    'version': "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        Module to define a cost of BoM.
    ''',
    'website': 'https://falinwa.com',
    'category': 'Manufacturing',
    'summary': 'Compute Cost of BoM',
    'depends': [
        'mrp_bom_cost', 'fal_mrp_production_scrap'
    ],
    'data': [
        'data/data.xml',
        'views/product_view.xml',
        'report/mrp_report_bom_structure.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
