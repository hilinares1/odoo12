# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition.
# See LICENSE file for full copyright and licensing details.
{
    "name": "Meeting Calendar Enhancement",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Extra Tools',
    'summary': 'Manage your meetings',
    "description": """
    Module to improve meeting function

    12.1.0.0.0 - First V.12 Release
    12.1.1.0.0 - Bug Fix on Security Side
    12.2.0.0.0 - Adding Option not to automatically send email
    12.5.0.0.0 - Add action to send MOM email and dependencies to fal_block_automatic_email
    """,
    "depends": [
        'calendar',
        'account',
        'contacts',
        'hr',
        'fal_block_automatic_email',
    ],
    'images': [
        'static/image/stopwatch.png',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/fal_meeting_meter_data.xml',
        'data/fal_meeting_meter_config.xml',
        'data/fal_mom_template_data.xml',
        'views/calendar_event.xml',
        'views/res_config_views.xml',
        'views/res_partner_view.xml',
        'views/menu.xml',
        'wizard/fal_calendar_meeting_wizard_view.xml',
        'report/calendar_meeting_mom_report.xml',
        'report/calendar_meeting_public_mom_report.xml',
        'report/calendar_meeting_internal_mom_report.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
