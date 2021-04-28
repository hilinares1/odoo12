# -*- coding: utf-8 -*-
{
    "name": "MRP Planning Availability",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    "description": """
    Module to check availablity for manufacture
    based on floating production date planning.
    """,
    "depends": [
        'fal_finished_product_sequence',
    ],
    'data': [
        'wizard/mrp_production_fixed_view.xml',
        'wizard/mrp_production_set_float_date_view.xml',
        'views/mrp_view.xml',
        'views/fal_production_order.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'active': False,
    'application': False,
}
