# -*- coding: utf-8 -*-
{
    'name': "Timesheet Minimum Hour",

    'summary': """
        Timesheet Minimum Hour""",

    'description': """
        Timesheet Minimum Hour
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Human Resource',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet_sheet', 'hr_contract'],

    # always loaded
    'data': [
        'views/resource_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
