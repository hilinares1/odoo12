# -*- coding: utf-8 -*-
{
    'name': "Internal Email",
    "version": "12.5.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://www.falinwa.com',
    'category': 'Hidden',
    'summary': "Provide a block email for internal only",
    'description': """
    """,
    'depends': ['base', 'web', 'mail'],
    'data': [
        'views/mail_template_view.xml',
        'views/ir_model_view.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/message_view.xml',
    ],
}
