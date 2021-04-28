# -*- coding: utf-8 -*-
{
    'name': 'Tax Comment',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'description': """
    Module to give Tax comment.
    """,
    'depends': [
    'account',
    'fal_comment_template',
    ],
    'data': [
        'views/comment_template_view.xml',
        'reports/report_invoice.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
