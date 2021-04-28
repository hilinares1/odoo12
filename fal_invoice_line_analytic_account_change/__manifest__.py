# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and
# licensing details.
{
    'name': 'Invoice Line Analytic Account Change',
    'version': '12.1.0.0.0',
    'author': 'Falinwa Limited',
    'website': 'https://falinwa.com',
    'category': 'Accounting & Finance',
    'description': """
        Module to give posibility to change analytic account on
        invoice line even its already confirmed.
    """,
    'depends': [
        'account_cancel'
    ],
    'data': [
        'wizard/fal_invoice_line_analytic_account_change_wizard_view.xml',
        'views/account_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
