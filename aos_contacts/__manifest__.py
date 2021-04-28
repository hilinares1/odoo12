# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Contacts',
    'version': '12.0.0.1.0',
    'summary': 'Separate Customer & Vendor Menu',
    'sequence': 1,
    "author": "Alphasoft",
    'description': """
This module is aim to add menu for Customer & Vendors
    """,
    'category' : 'Partners',
    'website': 'https://www.alphasoft.co.id/',
    'images' : ['images/main_screenshot.png'],
    'depends' : ['contacts'],
    'data': [
        #'security/ir.model.access.csv',
        "views/partner_view.xml",
    ],
    'demo': [
        
    ],
    'qweb': [
        
    ],
    'installable': True,
    'auto_install': False,
}
