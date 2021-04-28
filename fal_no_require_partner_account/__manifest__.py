# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'No Require Partner Accounts',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting and Finance',
    'summary': """
        No Require Partner Accounts""",
    'description': '''
    This module has features:\n
    1. Make receivable and payable accounts aren\'t required on partner
    ''',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_views.xml'
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
