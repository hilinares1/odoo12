# -*- coding: utf-8 -*-
{
    'name': 'Fal Quality Production Order',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    "category": 'Manufacturing',
    'website': 'https://falinwa.com',
    'description': '''
    module to modify quality control flow.

    Changelog:
        V.11.1.1.0.0 - Hide picking type id on test type, as it will be domained by the test picking
                     - Add Default picking type Id when create test type from picking
    ''',
    'depends': [
        'fal_quality',
        'fal_finished_product_sequence'
    ],
    'data': [
        'views/quality_view.xml',
    ],
    'css': [],
    'js': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
