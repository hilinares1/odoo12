# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Message Notification In User",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'summary': 'Add Message on User Form',
    'website': 'https://falinwa.com',
    'category': 'Base',
    "description": """
        Module to add message view in users form

        Changelog:
            12.0.1.0.0 -- First Release
            12.0.2.0.0 -- Fix message always showing even there is no change in access right
    """,
    "depends": ['mail'],
    'category': 'General',
    'data': [
        'views/res_users_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
