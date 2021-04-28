{
    'name': 'Repair Order Product Attribute',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        Module to give conditional choice on Repair Order.
    ''',
    'website': 'https://falinwa.com',
    'category': 'Repair Order',
    'summary': 'Advanced Product Attribute on Repair Order',
    'depends': [
        'fal_product_attribute',
        'repair'
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
