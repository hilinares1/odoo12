# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice : Title, Contact, Attachment, Archive",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting',
    'summary': 'Invoice : Title, Contact, Attachment, Archive',
    "description": """
    Module to add additional info in invoice customer / supplier
    """,
    "depends": ['fal_sale_sequence', 'fal_purchase_sequence'],
    'data': [
        'views/invoice_view.xml',
        'views/account_analytic_view.xml',
        'views/account_invoice_line_view.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
