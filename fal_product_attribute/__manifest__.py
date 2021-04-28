# -*- coding: utf-8 -*-

{
    'name': 'Product Attribute',
    'version': "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'description': '''
        * Main Idea : In case of there is too many product (even if it's template). So to help that, there is a attribute you can select and then system will suggest you the product.
        * Plus the attribute you select will become the reference of that sale order line.
    ''',
    'website': 'https://falinwa.com',
    'category': 'Warehouse',
    'summary': 'Advanced Product Attribute Management',
    'depends': [
        'stock',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/templates.xml',
        'views/product_attribute_view.xml',
        'views/product_attribute_selector_templates.xml',
        'views/product_attribute_selector_many2one_templates.xml'
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
