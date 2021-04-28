# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "REP-03_Invoice Reminder",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    "description": """
    Module to reminder the invoice due date
    """,
    "depends": ['account_reports_followup'],
    'init_xml': [],
    'data': [
        'views/res_partner_view.xml',
        'data/cron_configuration.xml'
    ],
    'css': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
