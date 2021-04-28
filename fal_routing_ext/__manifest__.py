# encoding: utf-8
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'Routing Workorder',
    'version': '12.0.1.0.0',
    'summary': """
        Add wizard to finish workorder and manufacture order.""",
    'description': '''
        Add wizard to finish workorder and manufacture order.
    ''',
    'author': 'Falinwa Limited',
    'website': 'http://falinwa.com',
    'depends': ['mrp_workorder'],
    'category': 'Manufacturing',
    'data': [
        'wizard/fal_routing_ext_view.xml',
        'views/mrp_view.xml',
    ],
    'active': False,
    'installable': True
}
