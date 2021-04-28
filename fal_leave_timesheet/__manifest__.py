# -*- coding: utf-8 -*-
{
    'name': 'Leave Timesheet',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Human Resource',
    'summary': 'Create Timesheet From Leave',
    'description': '''
    This module has features:\n
    1. Make Project and Task visible on form \n
    ''',
    'depends': [
        'project_timesheet_holidays',
    ],
    'data': [
        'views/hr_leave_type_view.xml',
    ],
    'css': [],
    'qweb': [
    ],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
