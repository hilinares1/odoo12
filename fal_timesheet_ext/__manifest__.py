# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Timesheet Extention',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resource',
    'summary': 'Improve base Functionality on Timesheet Module',
    'description': '''
        1. Security, (N+1), Timesheet N+1 have the same ability as Timehseet Officer, but only for employee he manage
    ''',
    'depends': [
        'hr_timesheet',
    ],
    'data': [
        'security/timesheet_security.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
