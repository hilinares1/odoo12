# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Timesheet Template",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resources',
    'summary': 'Feature to have timesheet template',
    "description": """
    Module to add feature to have timesheet template.
    """,
    "depends": [
        'hr_timesheet_sheet',
        'fal_hr_ext',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_timesheet_view.xml',
        'security/fal_timesheet_template_security.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,


}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
