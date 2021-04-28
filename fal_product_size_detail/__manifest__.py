{
    "name": "Product Detailed Specification",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Product',
    'summary': 'Add details in product.',
    'website': 'https://falinwa.com',
    "description": """
        This module has features:\n
        1. Add details on product. Currently stil size
        (length, width, and height)\n
        2. New UoM milimeter.\n
    """,
    "depends": [
        'stock',
    ],
    'data': [
        'data/product_data.xml',
        'views/product_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
