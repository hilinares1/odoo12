# -*- coding: utf-8 -*-
{
    'name': 'Controlling Dashboard',
    'version': '12.3.0.0.0',
    'author': 'Falinwa Limited',
    'category': 'Accounting & Finance',
    'website': 'https://falinwa.com',
    'description': """
Module to give additional feature of project dashboard.
    """,
    'depends': [
        'fal_project_budget',
        'hr_expense',
        'sale_timesheet',
        'timesheet_grid',
        'fal_timesheet_journal',
        'fal_multicurrency_group',
    ],
    'data': [
        'views/general_view.xml',
        'views/fal_dashboard_templates.xml',
        'views/project_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
