# -*- coding: utf-8 -*-
{
    'name': "Meeting Timesheet",
    'summary': "Create Timesheet From meeting",

    'description': """
    Create Timesheet From meeting

    Changelog:
    V.11.1.2.0.0 - Disable create timesheet button when it's already created
                 - Warning on no presence when timesheet button pressed
                 - Disable deleting timesheet sheet on meeting delete / draft function
    """,

    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    'category': 'Human Resource',
    'version': '12.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet', 'fal_calendar_meeting_ext'],

    # always loaded
    'data': [
        'views/calendar_event_view.xml',
        'views/analytic_account_view.xml',
        'wizard/fal_meeting_timesheet_wizard_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
