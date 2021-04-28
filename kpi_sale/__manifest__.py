# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'KPI Sales',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 17,
    'summary': 'KPI of sales',
    'description': """
Compute KPI of sales
====================
    """,
    'depends': [
        'pos_sale',  # Fix an union in database
        'sale',
        'sale_management',
        'digest'
    ],
    'data': [
        'data/digest_data.xml',
        'views/digest_views.xml',
    ],
}
