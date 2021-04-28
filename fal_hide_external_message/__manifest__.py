# -*- coding: utf-8 -*-
{
    'name': "Hide External Message",
    "version": "12.2.0.0.0",
    'author': 'Falinwa Limited',
    'website': 'https://www.falinwa.com',
    'category': 'Hidden',
    'summary': "Hide external message button feature",
    'description': """
    """,
    'depends': ['web', 'mail','fal_internal_message'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}
