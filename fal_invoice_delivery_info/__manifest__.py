# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Delivery List on Invoice",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'summary': 'List Delivery in Invoice',
    "description": """
    Module to add Delivery sheet on Invoice form
    """,
    "depends": ['stock_picking_invoice_link'],
    'data': [
        'report/account_report.xml',
        'views/report_invoice.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
