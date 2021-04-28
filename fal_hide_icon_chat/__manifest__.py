# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hide Chat Icon Odoo',
    'version': '12.0',
    'category': 'Base',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'depends': ['base', 'mail'
                ],
    'data': [
            
             ],
    'qweb': [
            'static/src/xml/systray.xml',
        ],

    'installable': True,
    'application': True,
}
