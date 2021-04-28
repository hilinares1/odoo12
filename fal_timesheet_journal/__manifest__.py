# -*- coding: utf-8 -*-
{
    'name': 'Journal Entry from Timesheet',
    'version': '12.1.0.0.0',
    'category': 'Accounting & Finance',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'description': '''
    When validating timesheet,
    this module will create journal entries based on timesheet.

    Changelog:
        V.12.0.1.0.0 - First Migrate
        V.12.0.2.0.0 - Change Behavior on Post Journal Security
        V.12.0.3.0.0 - Manager only is too annoying, give to accountant
    ''',
    'depends': [
        'hr_timesheet_sheet',
        'account',
    ],
    'data': [
        'data/data.xml',
        'views/hr_timesheet_view.xml',
        'wizard/timesheet_journal_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'application': False,
}
