# -*- coding: utf-8 -*-
{
    'name': "Phantom Routing Operation",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'version': '12.1.0.0.0',
    'summary': 'Phantom Routing Operation',
    'description': """

Phantom Routing: When the No Work Order is marked,
There will be no work order created.

""",
    'category': 'Manufacturing',
    'sequence': 10,
    'website': 'https://falinwa.com',
    'images': [],
    'depends': [
        'mrp',
    ],
    'demo': [],
    'data': [
        'views/mrp_views.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
