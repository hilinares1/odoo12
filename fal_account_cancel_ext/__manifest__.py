# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    "name": "ACC-02_Account Cancel Ext",
    "version": "12.4.0.0.0",
    'author': "Falinwa Limited",
    'website': "https://falinwa.com",
    "description": """
    Module to Extension the account cancel
    """,
    "depends": [
        'account_cancel',
    ],
    'init_xml': [],
    'data': [
        'security/security.xml',
        'views/account_cancel_view.xml',
    ],
    'css': [],
    'js': [],
    'installable': True,
    'active': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
