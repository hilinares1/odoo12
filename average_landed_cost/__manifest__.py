# -*- coding: utf-8 -*-
{
    'name': 'Average Landed Cost',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'summary': """Calculates average landed costs of products.""",
    'description': """Calculates average landed costs of products.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'maintainer': 'Cybrosys Techno Solutions',
    'depends': ['base', 'stock_landed_costs'],
    'data': ['views/average_landed_cost_views.xml',
             'security/ir.model.access.csv'],
    'images': ['static/description/images/banner.png'],
    'license': 'OPL-1',
    'price': 29,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
