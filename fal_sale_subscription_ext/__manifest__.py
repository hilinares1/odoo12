# -*- coding: utf-8 -*-

{
    'name': 'Sales Subscription: title, attachment,',
    'version': '12.0.1.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Sales',
    'summary': 'Additional field on Sale Subscription',
    'description': """
        This module allows you to extend sale susbcriptions.
    """,
    'depends': [
        'sale_subscription',
    ],
    'data': [
        'views/sale_subscription_views.xml',
        'report/sale_subs_report.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
