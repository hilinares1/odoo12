# -*- coding: utf-8 -*-
{
    "name": "Inventory Extends",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': "Stock",
    'summary': 'Inventory Extends',
    "description": """
	This module adds:\n
        1. Allows multiple cancel
    """,
    "depends": [
        'stock',
    ],
    'init_xml': [],
    'data': [
	'data/data.xml',
	'views/stock_move_views.xml',
        'views/stock_view.xml',
	'wizard/multi_cancel_picking_view.xml',
    ],
    'demo': [],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
