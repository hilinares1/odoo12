# -*- coding: utf-8 -*-
{
    'name': 'Sale line Comment by Product',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Sales',
    'summary': 'Add Comment Template in Sale lines based on Product and Supplier',
    'description': '''
    This module has features:\n
    1. Add Comment Template in Sale order Line
    ''',
    'depends': [
        'sale_management',
        'fal_comment_template',
    ],
    'data': [
        'views/sale_views.xml',
        'views/comment_template_view.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
