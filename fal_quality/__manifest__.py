# -*- coding: utf-8 -*-
{
    'name': 'Fal Quality',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    "category": 'Manufacturing',
    'website': 'https://falinwa.com',
    'description': '''
    module to modify quality control flow.

    Changelog:
        V.11.1.1.0.0 - Hide picking type id on test type, as it will be domained by the test picking
                     - Add Default picking type Id when create test type from picking
        V.12.1.0.0.0 - Add Workorder Quality Check, backorder quality check
    ''',
    'depends': [
        'quality_mrp',
        'quality_control',
        'mrp_workorder',
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/quality_view.xml',
        'views/mrp_quality_view.xml',
        'views/stock_picking_inherit.xml',
        'report/quality_check_report.xml',
        'report/quality_alert_report.xml',
    ],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
