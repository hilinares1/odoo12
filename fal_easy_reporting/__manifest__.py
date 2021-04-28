# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and
# licensing details.
{
    "name": "Dynamic Easy Reporting",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://www.falinwa.com',
    'category': 'Reports',
    'summary': 'Create Dynamic Report',
    "description": """
    Module to easily  export records without loading any records from tree.
    """,
    "depends": ['board'],
    'init_xml': [],
    'data': [
        'wizard/easy_exporting_wizard_view.xml',
        'views/easy_reporting.xml',
        'views/export_view.xml',
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
