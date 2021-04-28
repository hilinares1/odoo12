# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Hr Timesheet Analytic Multi-Company",
    "version": "12.4.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resources',
    'summary': 'Enable Multi-Company on Timesheet',
    "description": """
        Timesheet are Analytic Account, which analytic item are bound to analytic account company.
        We try to remove this constraints
    """,
    "depends": ['hr_timesheet_sheet', 'fal_analytic_account_ext'],
    'data': [
    ],
    'css': [],
    'js': [],
    'qweb': [
    ],
    'installable': True,
    'active': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
