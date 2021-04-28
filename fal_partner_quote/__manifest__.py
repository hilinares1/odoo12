{
    "name": "Partner Quote",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Partner Management',
    'summary': 'This module extends base module',
    'website': 'https://falinwa.com',
    "description": """
        This module has features:\n
        1. Add Sequence for Internal Reference in Customer '00+ID'.\n
        2. add menu for date sequence
    """,
    "depends": [
        'calendar',
        'product',
    ],
    'data': [
        'data/fal_internal_ref_sequence.xml',
        'views/product_view.xml',
        'views/calendar_view.xml',
        'views/sequence_date_range_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
