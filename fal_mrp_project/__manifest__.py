{
    "name": "MRP Project",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Manufacturing',
    'summary': 'Generate define project in MRP',
    'website': 'https://falinwa.com',
    "description": """
        Add project on MRP Production,
        Add value of project from sale order when creating manufacturing order from production order,
    """,
    "depends": [
        'fal_mrp_sale_link',
        'fal_project_in_partner_product',
    ],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
