# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Timesheet Invoice",
    "version": "12.4.0.0.0",
    "author": "Falinwa Limited",
    'website': 'https://falinwa.com',
    'category': "Human Resource",
    "description": """
    Module to add feature to have timesheet line invoiceable.
    """,
    "summary": 'Timesheet Invoice',
    "depends": [
        'hr_timesheet_sheet',
        'fal_invoice_additional_info'
    ],
    'init_xml': [],
    'data': [
        'wizard/hr_timesheet_invoice_create_view.xml',
        'security/ir.model.access.csv',
        'views/hr_view.xml',
        'views/fal_account_invoice.xml',
        'views/invoice_view.xml',
        'views/res_company_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
    'post_init_hook': 'post_init',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
