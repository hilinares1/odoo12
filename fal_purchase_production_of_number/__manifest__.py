{
    "name": "Purchase Production Order Number",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'category': 'Purchase Management',
    'summary': 'Purchase Production order Number extension',
    'website': 'https://falinwa.com',
    "description": """
        Purchase Production Order Number extension
    """,
    "depends": [
        'purchase',
        'fal_mrp_sale_link',
        'inter_company_rules',
    ],
    'data': [
        'views/purchase_view.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
