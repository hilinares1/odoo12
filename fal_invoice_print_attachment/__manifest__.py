# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "Invoice With Attachment",
    "version": "12.5.0.0.0",
    "author": "Falinwa",
    "description": """
    Module to print invoice with attachment
    """,
    "depends": [
        'fal_invoice_additional_info',
    ],
    'init_xml': [],
    'data': [
        'views/invoice_view.xml',
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
