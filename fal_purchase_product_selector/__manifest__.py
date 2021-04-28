{
    'name': 'Purchase Product Attribute',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        Module to give conditional choice on Purchase Order
    ''',
    'website': 'https://falinwa.com',
    'category': 'Purchase',
    'summary': 'Advanced Product Attribute Management on Purchase Order',
    'depends': [
        'fal_product_attribute',
        'purchase'
    ],
    'data': [
        'views/templates.xml',
        'views/purchase_views.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': True,
    'application': False,
}
