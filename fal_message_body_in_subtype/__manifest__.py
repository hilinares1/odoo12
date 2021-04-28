# -*- coding: utf-8 -*-
{
    'name': "Message Body in Subtype",
    "version": "12.1.0.0.0",
    'author': "Falinwa Limited",
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Mail',
    'summary': """
        Add message body in subtype""",
    'description': """
        Add message body in subtype
    """,
    # any module necessary for this one to work correctly
    'depends': ['mail'],
    'website': "https://falinwa.com",
    # always loaded
    'data': [
        'views/mail_message_subtype.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
