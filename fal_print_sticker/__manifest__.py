{
    "name": "Print Sticker",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Warehouse',
    'summary': 'Module to print sticker on inventory.',
    'website': 'https://falinwa.com',
    "description": """
         Module to print sticker on inventory.
    """,
    "depends": [
        'fal_mrp_of_number',
    ],
    'data': [
        'views/res_company_views.xml',
        'report/fal_picking_sticker.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
