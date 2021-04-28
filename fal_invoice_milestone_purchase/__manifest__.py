# -*- coding: utf-8 -*- {}
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice Milestone Purchase",
    "version": "12.3.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Invoicing Management',
    'summary': 'Split Invoice in Purchase Order',
    "description": """
    Module to add invoice milestone for purchase

    Changelog:
        V.11.1.1.0.0 - Enable user to fill empty date of invoice milestone
        V.12.1.1.0.0 - remove interval percentage, change to frequency
        V.12.3.0.0.0 - Improvement and add dependencies to project search
    """,
    "depends": [
        'fal_invoice_milestone',
        'fal_purchase_downpayment',
        'fal_project_search',
        'purchase',
    ],
    'data': [
        'data/fal_invoice_milestone_data.xml',
        'views/purchase_views.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
