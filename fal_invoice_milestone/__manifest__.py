# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice Milestone",
    "version": "12.1.1.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Invoicing Management',
    'summary': 'Split Invoice in Sale Order',
    "description": """
    Module to add invoice milestone

    Changelog:
        V.11.1.1.0.0 - Enable user to fill empty date of invoice milestone
        V.12.1.1.0.0 - remove interval percentage, change to frequency
    """,
    "depends": [
        'sale_management',
    ],
    'data': [
        'data/fal_invoice_milestone_data.xml',
        'views/res_config_settings.xml',
        'wizard/change_term_line_view.xml',
        'views/fal_invoice_milestone_views.xml',
        'views/account_views.xml',
        'views/sale_views.xml',
        'security/ir.model.access.csv',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
