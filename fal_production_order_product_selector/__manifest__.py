{
    'name': 'Production Order Product Attribute',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        Module to give conditional choice on Production Order.
    ''',
    'website': 'https://falinwa.com',
    'category': 'Production Order',
    'summary': 'Advanced Product Attribute on Production Order',
    'depends': [
        'fal_product_attribute',
        'fal_mrp_production_order'
    ],
    'data': [
        'views/templates.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': True,
    'application': False,
}
