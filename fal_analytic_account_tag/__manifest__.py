# -*- coding: utf-8 -*-
{
    'name': "FAL : Analytic Account Tag",
    'version': '12.4.0.0.0',
    'depends': [
        'account',
    ],
    'author': "Falinwa Limited",
    'website': "www.falinwa.com",
    'description': """
    module to add analytic tags
    """,
    # data files always loaded at installation
    'data': [
        'views/analytic_tags_views.xml',
    ],
    # data files containing optionally loaded demonstration data
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
