# -*- coding: utf-8 -*-
{
    "name": "Periods Lock Hr",
    "version": "12.1.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resource',
    'summary': 'Period Lock For Employee',
    "description": """
    Lock employee and manager expense and timesheet
    """,
    "depends": [
        'resource',
        'hr_expense',
        'fal_account_periods_lock',
    ],
    'data': [
        'views/fal_periods_lock_view.xml',
    ],
    'demo': ['data/data_demo.xml'],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
