# -*- coding:utf-8 -*-
{
    'name': 'Falinwa Leave',
    'version': '12.1.0.0.0',
    'category': 'Human Resource',
    'summary': 'Extends Leave Module',
    'description': """
        Module to extends Leave Module according Custom

        CHANGE LOG:
        1. 12.0.1.0.0 -- Development
    """,
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'depends': [
        'hr_holidays',
        'hr_contract',
        'account',
        'fal_message_body_in_subtype'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/scheduler.xml',
        'data/email_template.xml',
        'data/data.xml',
        'views/res_config_settings_views.xml',
        'views/hr_leave_view.xml',
        'views/hr_employees_views.xml',
        'views/resource_calendar_view.xml',
        'views/fix_date_views.xml',
        'wizard/hr_holidays_postpone_wizard_view.xml',
        'wizard/fal_working_schedule_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
